#########################################################################
# start imports
#########################################################################
import datetime
import string,cgi,time
import os
import re
from timeit import default_timer as timer

#########################################################################
# http server imports
#########################################################################
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

#########################################################################
# opencv imports, (hopefully opencv 3.x)
#########################################################################
from imutils.video import WebcamVideoStream
import imutils
import cv2
import numpy as np
 
#########################################################################
# threading imports
#########################################################################
import threading
#########################################################################
# end imports
#########################################################################




#########################################################################
# start variables
#########################################################################
# cameraQuality 0-100, can affect CPU utilization
cameraQuality=85

# streamWidth is the size of the video stream that gets sent to browser
streamWidth=640

# if camera appears as /dev/video0, 0 is the videoDeviceNumber to use
videoDeviceNumber=0

# color tracking on/off
# set colorTracking=False if you don't want to get into the color-tracking
# code. Setting to False makes for less lag and higher FPS, of course.
colorTracking=True
font = cv2.FONT_HERSHEY_TRIPLEX

#########################################################################
# if colorTracking=True:
# describe the lower/upper bounds of the HSV objects. these will
# vary camera-by-camera, object-by-object, lighting-condition-by-
# lighting-condition. Use a range-detection python script to determine
# the color of your object. Ideally, there might be some code in this
# project that automatically will hone in on the object that is
# directly in front of the camera, and generate some lower/upper bounds
# for that object. That's what the pixy camera does, I think.
#########################################################################
# green cube
#colorLower = (55, 175, 67)
#colorUpper = (104, 255, 207)

# yellow tennis ball
colorLower = (47, 39, 172)
colorUpper = (99, 155, 255)
#########################################################################
# end variables
#########################################################################




#########################################################################
# doAction(something)
#
# this function invokes a threaded process that will skip
# past events if it takes too long to get a lock. this can
# be used to anything outside the functions of video grabbing,
# processing, and serving. This would be for things like moving
# servos, driving a car, things that might take a while to perform.
#
# call doAction with the msg, and the action will be performed via a
# threaded remoteControlClass call, and video processing will be immediately
# resumed.
#
# the lock and the actionThreads array insure that actions are performed 
# one at a time, and in order. The lockExpireTime variable determines how
# long is "too long", with regard to waiting for a lock. For instance, if
# the servo commands are sent out faster than they can be performed, a 
# backlog of commands will exist (in actionThreads[]), and the actions will
# just get more and more delayed. Using lockExpireTime allows this code
# to discard delayed actions and proceed ahead to the most current action.
# this may not always be desired though. Also, you may want to modify this
# code to support multiple locks, depending upon the action (or even no
# lock for some actions).
#
# the example action performed below simply prints the msg to the console.
# put in a time.sleep(x) after (or before) the print to see the threading
# and lock timer in action.
#########################################################################
actionThreads=[]
lockExpireTime=0.5
def doAction(msg):
  global actionThreads, lockExpireTime
  thread=remoteControlClass(msg)
  thread.start()
  actionThreads.append(thread)

class remoteControlClass(threading.Thread):
  tLock=threading.Lock()

  def __init__(self, msg):
    threading.Thread.__init__(self)
    self.msg=msg

  def run(self):
    # start a timer, get a lock, end the timer. basically see how long
    # it's taking to acquire locks right now.
    startTime=timer()
    self.tLock.acquire()
    nowTime=timer()

    if (nowTime-startTime > lockExpireTime):
      # the lock took too long to acquire, just get out asap so that
      # the array of threads can hopefully catch up to a more-current
      # action.
      print "lock too too long: %s" % self.msg
      self.tLock.release()
    else:
      try:
        if self.msg:
          # you are in the thread here, so now do whatever it is
          # you wanted to do based upon msg (now self.msg).
          print "thread msg: %s" % self.msg
      finally:
        # whatever you were doing has now completed. release the lock.
        self.tLock.release()
#########################################################################
# end doAction(something)
#########################################################################

#########################################################################
# WebcamVideoStream class
#########################################################################
class WebcamVideoStream:
  def __init__(self, src=0):
    # initialize the video camera stream and read the first frame
    # from the stream
    self.stream = cv2.VideoCapture(src)
    (self.grabbed, self.frame) = self.stream.read()

    # initialize the variable used to indicate if the thread should
    # be stopped
    self.stopped = False

  def start(self):
    # start the thread to read frames from the video stream
    threading.Thread(target=self.update, args=()).start()
    return self
 
  def update(self):
    # keep looping infinitely until the thread is stopped
    while True:
      # if the thread indicator variable is set, stop the thread
      if self.stopped:
        return
 
      # otherwise, read the next frame from the stream
      (self.grabbed, self.frame) = self.stream.read()
 
  def read(self):
    # return the frame most recently read
    return self.frame

  def stop(self):
    # indicate that the thread should be stopped
    self.stopped = True
#########################################################################
# end WebcamVideoStream class
#########################################################################

#########################################################################
# httpHandler class
#########################################################################
class httpHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    global cameraQuality, streamWidth
    try:
      self.path=re.sub('[^.a-zA-Z0-9]', "",str(self.path))

      if self.path.endswith(".mjpeg"):
        self.send_response(200)
        self.wfile.write("Content-Type: multipart/x-mixed-replace; boundary=--aaboundary")
        self.wfile.write("\r\n\r\n")

        while True:
          # video frame is grabbed here
          frame = vs.read()
          if colorTracking:
            # blur it, hsv it, mask according to lower/upper masks
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            # get contours of objects matching color
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            if len(cnts) > 0:
              # c is the biggest area detected
              c = max(cnts, key=cv2.contourArea)
              ((x, y), radius) = cv2.minEnclosingCircle(c)
              if radius > 15:
                # get the moments. in the context of opencv images, moments are mathematically-
                # calculated descriptors. namely the center of the object in this case
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # draw a circle around the object
                cv2.circle(frame, (int(x), int(y)), int(radius),
                  (0, 255, 255), 2)
                # put a dot at the center of the object
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                msg = "R=%s  x:y=%s:%s" % (int(radius),int(x),int(y))

                # display some coordinates at the top of the frame
                cv2.rectangle(frame, (0, 0), (640, 40), (0,0,0), -2)
                cv2.putText(frame, msg, (5, 30), font, 1, (0,255,255), 1)

                # tell the threaded doAction to do something based upon this object's
                # existence, or location, or size
                doAction(msg)

          # finally, resize the frame as needed for output to the network
          frame = imutils.resize(frame, width=streamWidth)
       
          # send to http server
          r, cv2mat=cv2.imencode(".jpeg",frame,[cv2.IMWRITE_JPEG_QUALITY,cameraQuality])
          JpegData=cv2mat.tostring()
          self.wfile.write("--aaboundary\r\n")
          self.wfile.write("Content-Type: image/jpeg\r\n")
          self.wfile.write("Content-length: "+str(len(JpegData))+"\r\n\r\n" )
          self.wfile.write(JpegData)
          self.wfile.write("\r\n\r\n\r\n")

        # frames have stopped for some reason. clean everything up
        cv2.destroyAllWindows()
        vs.stop()
      else:
          pass
    except IOError, e:
      if isinstance(e.args, tuple):
        #print "errno is %d" % e[0]
        if e[0]==32:
          print "Detected remote disconnect"
        else:
          pass
      else:
        print "Socket error", e
        # self.send_error(404,'File Not Found: %s' % self.path)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    '''Handle requests in a separate thread.'''
#########################################################################
# end httpHandler class
#########################################################################

#########################################################################
# main processing
#########################################################################
def main():
  global vs, videoDeviceNumber

  # created a threaded video stream
  print("starting webcam thread...")
  vs = WebcamVideoStream(src=videoDeviceNumber).start()
  # allow the camera sensor to warm up before grabbing frames
  time.sleep(1)

  try:
    server = ThreadedHTTPServer(('', 8080), httpHandler)
    print 'started httpserver...'
    server.serve_forever()
  except KeyboardInterrupt:
    print '^C received, shutting down server'
    server.shutdown()
    server.server_close()
    try:
      os.sys.exit(0)
    except SystemExit:
      os._exit(0)

if __name__ == '__main__':
  main()
#########################################################################
# end main processing
#########################################################################

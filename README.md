# python-opencv-threaded-webcam
Basic threaded mjpeg webcam server with opencv 3.x processing. Works well on SBC computers like Raspberry Pi or Odroid C2.

# requirements
- a computer. I'm using an Odroid C2. I have done this on Raspberry Pi2, and Pi3, but Odroid C2 is quite a bit faster.
- a USB webcam. I'm using a Sony Playstation Eye, less than $5 on Amazon prime, here: http://www.amazon.com/gp/product/B000VTQ3LU/ref=pd_lpo_sbs_dp_ss_2?pf_rd_p=1944687682&pf_rd_s=lpo-top-stripe-1&pf_rd_t=201&pf_rd_i=B000B69ECS&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=1FW1XMZQ0H8WZNAM2Q2W
- a debian-based operating system. I'm using Jessie arm64, kindly provided for Odroid C2 by meveric, here: http://forum.odroid.com/viewtopic.php?f=138&t=19403
- python 2.7 (may work with 3.x, but no guarantees)
- opencv 3.x (could work with 2.x, but 3.x has a lot more image processing features)
- python modules: imutils, cv2 (3.x version, not 2.x version), numpy, threading, matploglib, scipi. You can either get these via apt, or pip. Your choice.

# compiling opencv 3.x on raspberry pi, or odroid c2
1. apt-get install some required building and image-related dev packages:
	```
	sudo apt-get install libopencv-dev build-essential cmake git libgtk2.0-dev pkg-config python-dev python-numpy libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtif f5-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libxine2-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev libtbb-dev libqt4-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils
	```

2. get the current version of opencv 3.x source, and unzip it

3. prepare for the compile
	```
	cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_V4L=ON -D WITH_QT=ON -D WITH_OPENGL=ON ..
	```

4. compile. this takes a while. -j4 will use 4 cores and will be roughly 4x as fast, but it will make the computer pretty sluggish. I use -j3 so that one core is available for other things while it compiles.
	```
	make -j4
	```

5. Either use checkinstall to build yourself a deb package so you don't have to do this again (requires apt-get checkinstall):
	```
	sudo checkinstall
	```

	OR, just make install it if you don't mind redoing all of this again if you start with a fresh OS:

	```
	sudo make install
	```

6. Lastly, create yourself an opencv.conf file:
	```
	sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
	```

If all the above worked out, you should be able to run the python program and it will serve /dev/video0 via port 8080. Access the video at http://your_IP:8080/video.mjpeg

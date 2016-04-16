# python-opencv-threaded-webcam
Basic threaded mjpeg webcam server with opencv 3.x processing. Works well on SBC computers like Raspberry Pi or Odroid C2.

# requirements
- python 2.x
- opencv 3.x
- python modules: imutils, cv2 (3.x version, not 2.x version), numpy, threading, matploglib, scipi. You can either get these via apt, or pip. Your choice.

# compiling opencv 3.x on raspberry pi, or odroid c2
1. apt-get install some required building and image-related dev packages:
libopencv-dev
build-essential
cmake
git
libgtk2.0-dev
pkg-config
python-dev
python-numpy
libdc1394-22
libdc1394-22-dev
libjpeg-dev
libpng12-dev
libtif
f5-dev
libjasper-dev
libavcodec-dev
libavformat-dev
libswscale-dev
libxine2-dev
libgstreamer0.10-dev
libgstreamer-plugins-base0.10-dev
libv4l-dev
libtbb-dev
libqt4-dev
libfaac-dev
libmp3lame-dev
libopencore-amrnb-dev
libopencore-amrwb-dev
libtheora-dev
libvorbis-dev
libxvidcore-dev
x264
v4l-utils

2. get the current version of opencv 3.x source, and unzip it

3. prepare for the compile
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_V4L=ON -D WITH_QT=ON -D WITH_OPENGL=ON ..
make -j4 (or 3 if you have other things to do, or 1 if you're on a single-core cpu)

# Either use checkinstall to build yourself a deb package so you don't have to do this again
sudo checkinstall

# OR, just make install it I guess
sudo make install

sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'


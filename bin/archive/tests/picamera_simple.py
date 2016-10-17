#!/usr/bin/python
import time
import picamera

frames = 30

with picamera.PiCamera() as camera:
    camera.resolution = (2592, 1944)
    start = time.time()
    camera.capture_sequence([
        'image%02d.jpg' % i
        for i in range(frames)
        ], resize=(1024, 768), use_video_port=True)
    finish = time.time()
print('Captured %d frames at %.2ffps' % (
    frames,
    frames / (finish - start)))
#!/usr/bin/python
import serial, io, glob
from time import sleep
from shutil import copyfile, move
from os import path, mkdir, remove

# define our camera class
class CameraDevice:

    def Connect(self, camera_cfg, script_cfg):

        try:

            camera = serial.Serial(camera_cfg['device'], baudrate=camera_cfg['baudrate'],
                                   bytesize=camera_cfg['bytesize'],
                                   parity=camera_cfg['parity'], stopbits=camera_cfg['stopbits'],
                                   timeout=camera_cfg['timeout'])

            if camera.is_open:
                if script_cfg['debug']:
                    print (" camera connection opened ")
                    # camera.close()
                # self.PhotoMode(camera, script_cfg)
                return camera
            else:
                if script_cfg['debug']:
                    print (" camera connection not opened ")
                return False


        except:

            if script_cfg['debug']:
                print(" camera serial connection failed ")
            return False


    # this is the trigger process for the camera
    def Trigger(self, camera, script_cfg):

        try:

            test = camera.read()
            if test == b'':
                print(test)

                # camera.open()
                cmd = "$D1\n"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                response = camera.read(7)
                #response = camera.readline()

                if script_cfg['debug']:
                    print(response)

                if response == b'@D1:LED':

                    # camera.close()
                    return True

                if response == b'@D1:WAR':

                    CameraDevice.CameraMode(CameraDevice, camera, script_cfg)

                    return False
                else:

                    return False

            else:

                return False

        except:

            if script_cfg['debug']:
                print(" camera trigger failed ")
            return False


    def CameraMode(self, camera, script_cfg):

        try:

            camera.close()
            camera.open()

            test = camera.readline()
            if test == b'':

                print("switch back to camera mode")
                test = camera.readline()
                # camera.open()
                cmd = "$D5"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$Pu"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D5"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D9"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D7"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$Pm"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)
                return True

        except:

            if script_cfg['debug']:
                print(" camera mode failed ")
            return False


    # this is the trigger process for the camera
    def USBMode(self, camera, script_cfg):
        try:

            camera.close()
            camera.open()

            test = camera.readline()
            if test == b'':
                print(test)

                # camera.open()
                cmd = "$D5"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$Pu"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D5"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D9"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                cmd = "$D7"
                camera.write(cmd.encode('ascii'))
                camera.flush()
                sleep(0.2)
                response = camera.readline()
                print(response)

                response = camera.readline()
                print(response)

                return True

        except:

            if script_cfg['debug']:
                print(" usb mode failed ")

            return False

    def TestMount(self, camera_cfg, i):

        print("testing ", camera_cfg['mount'])

        i = 0
        while not path.isdir(camera_cfg['mount']):

            print(" waiting on the mount device ", i)
            i += 1
            sleep(1)
            if i > 60:
                break

        if path.isdir(camera_cfg['mount']):

            print(" mount is available ")

            return True

    def CopyImages(self, camera_cfg, script_cfg):

        try:

            # make sure the dir does not already exists and create it
            if not path.isdir(script_cfg['path'] + '/tmp/images'):
                mkdir(script_cfg['path'] + '/tmp/images')
                if script_cfg['debug']:
                    print(' created an images directory ')

            move(camera_cfg['mount'], script_cfg['path'] + '/tmp/images')

            return True

        except:

            return False

    def GetImages(self, camera_cfg, script_cfg):

        images = []
        for filename in glob.glob(script_cfg['path'] + '/tmp/images/**/*.JPG', recursive=True):
            images.append(filename)

        return images
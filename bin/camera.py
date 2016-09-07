#!/usr/bin/python
import serial, io
from time import sleep

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
                cmd = "$D1"
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

                    return False
                else:

                    return False

        except:

            if script_cfg['debug']:
                print(" camera trigger failed ")
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
                print(" camera trigger failed ")

            return False
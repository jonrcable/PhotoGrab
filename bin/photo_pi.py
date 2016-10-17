#!/usr/bin/python
import picamera
import struct
from sys import stdout
from io import BytesIO
from os import path, remove
from _datetime import datetime, timedelta
from time import sleep, perf_counter
from tabulate import tabulate
from neopixel import *

# load our custom classes
from bin.database import DBLite
from bin.structure import FileStruct
from bin.imu import IMUDevice

# define our main class
class PhotoGrab:

    # lets init our master process
    def __init__(self, camera_cfg, imu_cfg, offsets_cfg, script_cfg):

        # lets bring our varibles into the class
        self.camera_cfg = camera_cfg
        self.imu_cfg = imu_cfg
        self.offsets_cfg = offsets_cfg
        self.script_cfg = script_cfg

        # lets set the global process
        self.process = {}
        self.process['start'] = False # init the main process status to true
        self.process['connection'] = {} # init the database connection
        self.process['camera'] = {} # init the camera connection
        self.process['trigger'] = False # init the camera trigger to false
        self.process['loop'] = 0 # init the loop count
        self.process['count'] = 0 # init the fired count
        self.process['pid'] = 0  # the pid of the subprocess writing IMU data

        # lets start things off
        self.Start()

    # lets kick off the process
    def Start(self):

        print("| opening, starting camera service |")

        # try to open the camera
        camera = picamera.PiCamera(camera_num=0, stereo_mode='none', stereo_decimate=False, resolution=self.camera_cfg['resolution'], framerate=None, sensor_mode=self.camera_cfg['sensor_mode'], led_pin=None)

        # camera settings
        camera.exposure_mode = self.camera_cfg['exposure_mode']
        camera.iso = self.camera_cfg['iso']
        camera.awb_mode = self.camera_cfg['awb_mode']
        camera.awb_gains = self.camera_cfg['awb_gains']
        camera.shutter_speed = self.camera_cfg['shutter_speed']
        camera.brightness = self.camera_cfg['brightness']
        camera.exposure_compensation = self.camera_cfg['exposure_compensation']
        camera.meter_mode = self.camera_cfg['meter_mode']
        camera.contrast = self.camera_cfg['contrast']

        # Create NeoPixel object with appropriate configuration.
        self.led_flash = Adafruit_NeoPixel(self.camera_cfg['led_count'], self.camera_cfg['led_pin'], self.camera_cfg['led_freq_hz'], self.camera_cfg['led_dma'],
                                      self.camera_cfg['led_inverter'], self.camera_cfg['led_brightness'], self.camera_cfg['led_channel'], ws.SK6812W_STRIP)
        # Intialize the library (must be called once before other functions).
        self.led_flash.begin()

        print("| started, autotigger -", self.script_cfg['headless'], "|")

        if not self.script_cfg['headless']:
            print ('| looking for ', self.script_cfg['path'] + '/tmp/trigger.proc |')
        else:
            print ('| starting auto capture |')

        print('| process will run ', self.script_cfg['max'], ' or ',
              self.script_cfg['triggers'], ' triggers |')

        # run some basic tests and conenct our script
        # these script hault on fail, see logs details
        self.process['start'] = self.Connect()

        # if everything connects
        if self.process['start']:

            # try to open the camera process
            try:

                # open the in-memory photo stream
                stream = BytesIO()

                # set th flash on
                # set th flash on
                self.led_flash.setPixelColor(0, Color(self.camera_cfg['led_color_r'],
                                                 self.camera_cfg['led_color_g'],
                                                 self.camera_cfg['led_color_b']))
                self.led_flash.show()

                # grab a reliable piece of time
                start_stamp = datetime.now()  # init system date stamp
                # first loop, we need to set the frames stop timecode to the start time
                frame_stop = perf_counter()

                # capture frames continuously in-memory until we capture a trigger
                for photo in camera.capture_continuous(stream, format='jpeg', use_video_port=False, resize=None, splitter_port=0, quality=100):

                    # set th flash off
                    self.led_flash.setPixelColor(0, Color(0, 0, 0))
                    self.led_flash.show()

                    # time since the last photo the last operation ran
                    camera_lapse = perf_counter() - frame_stop

                    # this frames start timecode
                    frame_start = perf_counter()

                    # get the start byte of our imu file
                    imu_byte = path.getsize(self.script_cfg['path'] + '/tmp/imu.dat')

                    # Truncate the stream to the current position (in case
                    # prior iterations output a longer image)
                    stream.truncate()

                    # this frames stop timecode
                    frame_stop = perf_counter()
                    # get the time stamp that this frame was recveived
                    frame_stamp = start_stamp + timedelta(0, frame_start)
                    # get the total time this operation took
                    frame_lapse = frame_stop - frame_start

                    self.process['loop'] += 1  # this loop counts

                    result = {}
                    # tmp holder for the IMU data
                    result['telemetry'] = ''  # we will get this on post process
                    # store the results meta data for this frame
                    result['trigger'] = format(frame_stamp)
                    result['trigger_lapse'] = "{:.12f}".format(frame_lapse)
                    result['camera_lapse'] = "{:.12f}".format(camera_lapse)
                    result['imu_byte'] = imu_byte

                    # if we have hit the max amount of loops then we need to stop
                    if self.script_cfg['max'] != 0 and self.process['loop'] >= self.script_cfg['max']:
                        # close our connections, kill everything
                        stream.close()
                        self.End(camera)
                        break

                    # if we have hit the max amount of triggers then we need to stop
                    elif self.script_cfg['triggers'] != 0 and self.process['count'] >= self.script_cfg['triggers']:
                        # close our connections, save everything
                        stream.close()
                        self.End(camera)
                        break

                    # otherwise lets see if a stop file exists
                    elif path.isfile(self.script_cfg['path'] + '/tmp/stop.proc'):

                        # close our connections, save everything
                        stream.close()
                        self.End(camera)
                        break

                    # test our triggers
                    else:

                        # if we are set to run headless then do not wait for the tigger file
                        if self.script_cfg['headless']:

                            print("| capture | ")

                            self.process['count'] += 1  # this trigger counts
                            self.process['loop'] = 0  # reset the loop count

                            # get the file name and open the file
                            result['image'] = "image-" + str(self.process['count']).zfill(4) + ".jpg"

                            # write our frame to a file
                            file = open(self.script_cfg['path'] + "/tmp/" + result['image'], 'wb')
                            file.flush()  # <-- here's something not to forget!

                            # Rewind the stream and write the file to tmp
                            stream.seek(0)
                            file.write(stream.read())
                            file.close()

                            # get the file size
                            result['size'] = path.getsize(self.script_cfg['path'] + "/tmp/" + result['image'])

                            # Reset the stream for the next capture
                            stream.seek(0)
                            stream.truncate()
                            stream.flush()

                            # send the result to the database
                            DBLite.InsertDB(DBLite, self.process['connection'], self.script_cfg, result)

                            print("| complete -", result, " | ")

                            # set th flash on
                            self.led_flash.setPixelColor(0, Color(self.camera_cfg['led_color_r'],
                                                             self.camera_cfg['led_color_g'],
                                                             self.camera_cfg['led_color_b']))
                            self.led_flash.show()

                        # otherwise lets see if a tigger file exists
                        elif path.isfile(self.script_cfg['path'] + '/tmp/trigger.proc'):

                            print("| capture trigger | ")

                            self.process['count'] += 1  # this trigger counts
                            self.process['loop'] = 0  # reset the loop count

                            # get the file name and open the file
                            result['image'] = "image-" + str(self.process['count']).zfill(4) + ".jpg"

                            # write our frame to a file
                            file = open(self.script_cfg['path'] + "/tmp/" + result['image'], 'wb')
                            file.flush()  # <-- here's something not to forget!

                            # Rewind the stream and write the file to tmp
                            stream.seek(0)
                            file.write(stream.read())
                            file.close()

                            # get the file size
                            result['size'] = path.getsize(self.script_cfg['path'] + "/tmp/" + result['image'])

                            # Reset the stream for the next capture
                            stream.seek(0)
                            stream.truncate()
                            stream.flush()

                            # send the result to the database
                            DBLite.InsertDB(DBLite, self.process['connection'], self.script_cfg, result)

                            # remove the trigger file
                            remove(self.script_cfg['path'] + '/tmp/trigger.proc')

                            print("| complete -", result, " | ")

                            # set th flash on
                            # set th flash on
                            self.led_flash.setPixelColor(0, Color(self.camera_cfg['led_color_r'],
                                                             self.camera_cfg['led_color_g'],
                                                             self.camera_cfg['led_color_b']))
                            self.led_flash.show()

                        else:
                            # throw away this frame, no trigger found
                            print("| rest offset -", self.offsets_cfg['rest'], " | ")
                            # Reset the stream for the next capture
                            stream.seek(0)
                            stream.truncate()
                            stream.flush()
                            sleep(self.offsets_cfg['rest'])

            except KeyboardInterrupt:
                print ("| bye user exit, closing connections |")
                # close our connections, kill everything
                stream.close()
                self.End(camera)

        else:

            print("| failed to connect services, closing camera |")
            # close the camera, something went wrong starting our services
            camera.close()

    # If we need to close anything we do it here
    def End(self, camera):

        # set th flash processing
        self.led_flash.setPixelColor(0, Color(255, 255, 0))
        self.led_flash.show()

        # if the process count matches the trigger count, we succeeded
        if self.process['count'] == self.script_cfg['triggers'] or path.isfile(self.script_cfg['path'] + '/tmp/stop.proc'):

            i = 0
            while i < 3:
                # set the camera led off
                self.led_flash.setPixelColor(0, Color(0, 0, 0))
                self.led_flash.show()
                sleep(0.25)
                i += 1
                # set the camera led to warn
                self.led_flash.setPixelColor(0, Color(255, 255, 0))
                self.led_flash.show()
                sleep(0.25)

            # close the camera
            camera.close()

            # kill the imu process
            IMUDevice.StopIMU(IMUDevice, self.process['pid'], self.script_cfg)

            # if we have reached the end, report
            rows = DBLite.DisplayDB(DBLite, self.process['connection'], self.script_cfg)

            # get the name of our archive before we close the database
            archive = DBLite.GetArchiveName(DBLite, self.process['connection'], self.script_cfg)

            # if we are in ascii then process the imu information
            if self.imu_cfg['stream'] == 'ascii':
                IMUDevice.ProcessIMU(IMUDevice, self.process['connection'], self.script_cfg, rows)

                # get the updated rows
                rows = DBLite.DisplayDB(DBLite, self.process['connection'], self.script_cfg)

                # export a processed imu file
                FileStruct.ProcessedCSV(FileStruct, self.script_cfg, rows)

            # close our db connection
            DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)

            # write a friendly csv file
            FileStruct.WriteCSV(FileStruct, self.script_cfg, rows)

            # move the database/imu data to a new store location
            FileStruct.Save(FileStruct, self.script_cfg, archive)

            # pretty print the final results
            # if we are in ascii print the telemetry
            if self.imu_cfg['stream'] == 'ascii':
                output = tabulate(rows, headers=["Trigger", "Trigger Lapse", "Camera Lapse", "Byte", "Image", "Size", "Telemetry"], floatfmt=".12f")

                print(output)

                with open(self.script_cfg['path'] + '/tmp/results.txt', "w") as text_file:
                    print(output, file=text_file)

            else:
                output = tabulate(rows, headers=["Trigger", "Trigger Lapse", "Camera Lapse", "Byte", "Image", "Size"], floatfmt=".12f")

                print(output)

                with open(self.script_cfg['path'] + '/tmp/results.txt', "w") as text_file:
                    print(output, file=text_file)

            print("| done, ", self.process['count'], "/", self.script_cfg['triggers'], "success |")

            self.led_flash.setPixelColor(0, Color(0, 255, 0))
            self.led_flash.show()

            self.process['start'] = False
            exit()

        else:

            # close the camera
            camera.close()

            # kill the imu process
            IMUDevice.StopIMU(IMUDevice, self.process['pid'], self.script_cfg)
            # close our db connection
            DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)

            print("| done, ", self.process['count'], "/", self.script_cfg['triggers'], "failed |")

            self.led_flash.setPixelColor(0, Color(0, 0, 0))
            self.led_flash.show()

            self.process['start'] = False
            exit()

    # these are the init self checks for the process
    def Connect(self):

        # now try to start our services
        try:

            i = 0
            while i < 3:
                # set the camera led off
                self.led_flash.setPixelColor(0, Color(0, 0, 0))
                self.led_flash.show()
                sleep(0.25)
                i += 1
                # set the camera led to warn
                self.led_flash.setPixelColor(0, Color(255, 255, 0))
                self.led_flash.show()
                sleep(0.25)

            if self.script_cfg['debug']:
                print(' run all of our prechecks ')

            # cleanup any old jobs
            FileStruct.CleanUp(FileStruct, self.script_cfg)

            # create our directories
            FileStruct.CreateStructure(FileStruct, self.script_cfg)

            # init connection to a new sqlite database
            self.process['connection'] = DBLite.StartDB(DBLite, self.script_cfg)

            #create a new databse table
            DBLite.InitDB(DBLite, self.process['connection'], self.script_cfg)
            if self.script_cfg['debug']:
                print(' new database connection successful ')

            # get the IMU data
            self.process['pid'] = IMUDevice.StartIMU(IMUDevice, self.imu_cfg, self.script_cfg)

            # if this fails so should the script
            if not self.process['pid']:

                if self.script_cfg['debug']:
                    print(' new imu connection failed ')

                # close the database connection we no longer need it
                DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)
                return False

            else:
                if self.script_cfg['debug']:
                    print(' new imu connection started ')

            print("| connection(s) successful, waiting on", self.script_cfg['triggers'] ,"trigger(s) |")
            return True

        except:
            # something went bad halt
            print("| connection(s) failed |")
            # fail
            return False
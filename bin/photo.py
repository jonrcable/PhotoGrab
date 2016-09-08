#!/usr/bin/python
from os import path, remove
from _datetime import datetime, timedelta
from time import sleep, perf_counter
from tabulate import tabulate

# load our custom classes
from bin.database import DBLite
from bin.structure import FileStruct
from bin.imu import IMUDevice
from bin.camera import CameraDevice

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

        print("| starting, autotigger -", self.script_cfg['headless'] , "|")

        # report the start
        if self.script_cfg['debug']:
            print ('start looking for ', self.script_cfg['path'] + '/tmp/trigger.proc')
            print ('process start ', self.process['loop'], ' will run ', self.script_cfg['max'], ' or ', self.script_cfg['triggers'], ' triggers')

        # run some basic tests and conenct our script
        # these script hault on fail, see logs details
        self.process['start'] = self.Connect()

        # run the process if our tests are valid
        while self.process['start']: # constructs our process loop

            # start monitoring our process
            try:

                # if we have hit the max amount of loops then we need to stop
                if self.script_cfg['max'] != 0 and self.process['loop'] >= self.script_cfg['max']:
                    # stop the process and exit
                    self.End()
                    break

                # if we have hit the max amount of triggers then we need to stop
                elif self.script_cfg['triggers'] != 0 and self.process['count'] >= self.script_cfg['triggers']:
                    # stop the process and exit
                    self.End()
                    break

                # runs some triggers
                else:

                    # if we are set to run headless then do not wait for the tigger file
                    if self.script_cfg['headless']:

                        # run the tigger process, now
                        result = self.Event(True)

                        if not result:
                            print( " trigger was not valid " )

                        else:
                            print(" trigger was valid ")
                            # send the result to the database
                            DBLite.InsertDB(DBLite, self.process['connection'], self.script_cfg, result)

                    # otherwise lets see if a tigger file exists
                    else:

                        # look for the tigger file in the following path
                        if path.isfile(self.script_cfg['path'] + '/tmp/trigger.proc'):  # does the trigger file exists fire

                            # run the tigger process, now
                            result = self.Event(True)

                            if not result:
                                print(" trigger is not ready ")

                            else:
                                print(" trigger recorded storing ")
                                # send the result to the database
                                DBLite.InsertDB(DBLite, self.process['connection'], self.script_cfg, result)

                            # remove the trigger file
                            remove(self.script_cfg['path'] + '/tmp/trigger.proc')

                        else:
                            # run the tigger process, fail
                            self.Event(False)

            except KeyboardInterrupt:
                print ("| bye early exit, closing connections |")
                # close our connections
                DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)
                IMUDevice.StopIMU(IMUDevice, self.process['pid'], self.script_cfg)
                exit()

    # If we need to close anything we do it here
    def End(self):

        # kill the imu process
        IMUDevice.StopIMU(IMUDevice, self.process['pid'], self.script_cfg)

        # set some thing we will need
        display = {}
        archive = None

        # if the process count matches the trigger count
        if self.process['count'] == self.script_cfg['triggers']:

            # if we have reached the end, should we report
            rows = DBLite.DisplayDB(DBLite, self.process['connection'], self.script_cfg)

            # switch the camera to USB Mode
            CameraDevice.USBMode(CameraDevice, self.process['camera'], self.script_cfg)

            # update the rows with their binary telemetry
            IMUDevice.ProcessIMU(IMUDevice, self.process['connection'], self.script_cfg, rows)

            # test the mount is ready
            Test = CameraDevice.TestMount(CameraDevice, self.camera_cfg, 0)

            # get the name of our archive before we close the database
            archive = DBLite.GetArchiveName(DBLite, self.process['connection'], self.script_cfg)

            # copy the images off the camera
            if Test:
                CameraDevice.CopyImages(CameraDevice, self.camera_cfg, self.script_cfg)
                images = CameraDevice.GetImages(CameraDevice, self.camera_cfg, self.script_cfg)
                DBLite.UpdateImages(DBLite, self.process['connection'], self.script_cfg, rows, images)

            CameraDevice.CameraMode(CameraDevice, self.process['camera'], self.script_cfg)

            print("| closing, ", self.process['count'], "/", self.script_cfg['triggers'], "success |")

        else:

            print("| closing ", self.process['count'], "/", self.script_cfg['triggers'], "failed |")

        # if we have reached the end, should we report
        display = DBLite.DisplayDB(DBLite, self.process['connection'], self.script_cfg)

        # write a friendly csv file
        FileStruct.WriteCSV(FileStruct, self.script_cfg, display)

        # close our connections
        DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)

        # if we have result to display and save
        if self.process['count'] == self.script_cfg['triggers']:

            # pretty print the final results
            print(tabulate(display, headers=["Trigger", "Start", "Byte", "Stop", "Byte", "Runtime", "Segment (size)", "BLOB (size)", "Image"], floatfmt=".12f"))

            # move the database/imu data to a new store location
            FileStruct.Save(FileStruct, self.script_cfg, archive)

        if self.script_cfg['debug']:
            print(' process end ', self.process['loop'])

        self.process['start'] = False
        exit()

    # these are the init self checks for the process
    def Connect(self):

        # now try to start our services
        try:

            if self.script_cfg['debug']:
                print(' run all of our prechecks ')

            # create our directories
            FileStruct.CreateStructure(FileStruct, self.script_cfg)

            # cleanup any old jobs
            FileStruct.CleanUp(FileStruct, self.script_cfg)

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

            # try to open the camera
            camera = CameraDevice.Connect(CameraDevice, self.camera_cfg, self.script_cfg)
            if not camera:

                # close the database connection we no longer need it
                #DBLite.CloseDB(DBLite, self.process['connection'], self.script_cfg)
                # hault the imu device
                #IMUDevice.StopIMU(IMUDevice, self.process['pid'], self.script_cfg)
                self.End()

                if self.script_cfg['debug']:
                    print(' new camera connection failed ')

            else:

                # set the camera process
                self.process['camera'] = camera

            # CameraDevice.ClearImages(CameraDevice, camera, self.camera_cfg, self.script_cfg)

            print("| connection(s) successful, waiting on", self.script_cfg['triggers'] ,"trigger(s) |")
            return True

        except:
            # something went bad halt
            print("| connection(s) failed |")
            # fail
            return False

    # this is the actual process to trigger an event
    def Event(self, trigger):

        self.process['loop'] += 1  # this loop counts
        result = {}

        # if we have a trigger lets do this
        if trigger:

            self.process['loop'] = 0  # reset the loop count

            if self.script_cfg['debug']:
                print(' trigger', self.process['count'], 'waiting on camera ')

            # grab a reliable piece of time
            trigger = datetime.now()  # system time, if we can get above we ignore this

            # get the start byte of our imu file
            start_byte = path.getsize(self.script_cfg['path'] + '/tmp/imu.txt')
            # start the timer
            start = perf_counter()

            # lets fire the camera trigger
            snap = CameraDevice.Trigger(CameraDevice, self.process['camera'], self.script_cfg)

            # tmp holder for the IMU data
            result['telemetry'] = '' # we will get this on post process

            # get the stop byte of our imu file
            stop_byte = path.getsize(self.script_cfg['path'] + '/tmp/imu.txt')
            # end the counter
            stop = perf_counter()

            # report the elapsed time it took to run this process
            elapsed = stop - start
            # get the end time
            delta = trigger + timedelta(0, elapsed)

            result['trigger'] = format(trigger)
            result['elapsed'] = "{:.12f}".format(elapsed)
            result['delta'] = format(delta)
            result['start_byte'] = start_byte
            result['stop_byte'] = stop_byte
            result['size'] = stop_byte - start_byte

            if snap:

                self.process['count'] += 1  # this trigger counts
                print("| start -", trigger, "| stop -", delta, "| elapsed - {:.12f} seconds".format(elapsed), "|")
                return result

            elif snap == None:

                sleep(0.10)
                self.Event(False)

            else:

                sleep(0.10)
                print(" camera ack return failed ", snap)
                self.Event(False)

        # otherwise lets just do cleanup or whatever
        else:

            if self.script_cfg['debug']:
                print('trigger false ', self.process['loop'], '/', self.script_cfg['max'])

            sleep(self.offsets_cfg['rest'])  # we should rest for X before we start again

            return False
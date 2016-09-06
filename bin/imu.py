#!/usr/bin/python
from os import path, kill
from signal import SIGKILL
from subprocess import Popen
from time import sleep

# load our custom classes
from bin.database import DBLite

class IMUDevice:

    # this is the serial process to get the IMU data
    def StartIMU(self, imu_cfg, script_cfg):

        # simple test to see if the imu is running
        if path.exists(imu_cfg['device']):

            try:
                # write our log file
                log = open(script_cfg['path'] + '/tmp/imu.txt', 'a')
                log.flush()  # <-- here's something not to forget!

                # run a simple cat command as a background process to capture the data to a file
                proc = Popen("cat " + imu_cfg['device'], stdout=log, stderr=log, shell=True)
                if script_cfg['debug']:
                    print(" imu collection started process: ", proc.pid)
                    print(" sleep for (", imu_cfg['delay'] ,") seconds, waiting on imu ")

                # place a delay to make sure the imu data gets up to speed
                sleep(imu_cfg['delay'])

                # return the process id of the imu data collection
                return proc.pid

            except:
                print('| failed to start imu data |')
                return False

        else:
            print('| device is not connected |')
            return False


    # this is the serial process to stop the imu process
    def StopIMU(self, pid, script_cfg):
        try:
            # kil the data collection background process
            kill(pid, SIGKILL)
            if script_cfg['debug']:
                print(" imu data collection stopped: ", pid)
            return True

        except:
            if script_cfg['debug']:
                print(" imu data collection failed to stop: ", pid)
            return False


    # post process the IMU information
    def ProcessIMU(self, connection, script_cfg, rows):
        try:

            print("| processing, segmenting imu file to sql blob |")

            # write our log file
            log = open(script_cfg['path'] + '/tmp/imu.txt', 'rb')

            # loop the log information from the collected triggers
            for index, row in enumerate(rows):
                rowid = row[0]
                start_byte = row[2]
                stop_byte = row[4]
                # determine the delta size between the two timers
                byte_delta = stop_byte - start_byte
                # read the file segment fromthe byte points
                log.seek(start_byte, 0)
                part = log.read(byte_delta)
                # update this record to sql
                DBLite.UpdateTelemetry(DBLite, connection, script_cfg, part, rowid)
                # REPLACE self.UpdateTelemetry(part, rowid)

            return True

        except:

            if script_cfg['debug']:
                print("failed, segmenting imu file to sql blob")
            return False
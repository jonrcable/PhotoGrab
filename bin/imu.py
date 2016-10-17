#!/usr/bin/python
import json
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
                log = open(script_cfg['path'] + '/tmp/imu.dat', 'a')
                log.flush()  # <-- here's something not to forget!

                # run a simple cat command as a background process to capture the data to a file
                # this is the golden ticket
                # (stty 38400 cs8 -cstopb -parity; cat > /Users/Jon/Development/Code/Apps/CameraIMU/tmp/ugh.dat | od -x) < /dev/cu.KeySerial1
                # this is the golden ticket

                # proc = Popen("(stty 38400 cs8 -cstopb -parity; cat > " + script_cfg['path'] + "/tmp/imu.txt) < " + imu_cfg['device'], shell=True)
                # ttylog -b 9600 -d /dev/ttyS0 > file.txt
                # (stty 38400 cs8 -cstopb -parity; ttylog -b 38400 -d /dev/cu.KeySerial1 > /Users/Jon/Development/Code/Apps/CameraIMU/tmp/imu.txt
                # (stty 38400 cs8 -cstopb -parity; cat > /Users/Jon/Development/Code/Apps/CameraIMU/tmp/tmp/more.dat | od -x) < /dev/cu.KeySerial1
                # od -x < /dev/ttyS0
                # (grabserial -v -d "/dev/cu.KeySerial1" -b 38400 -w 8 -p N -s 1 -e 30 -t -m "Starting kernel.*") < /Users/Jon/Development/Code/Apps/CameraIMU/tmp/test.txt
                # (grabserial -v -d "/dev/cu.KeySerial1" -b 38400 -w 8 -p N -s 1 -e 30 -t -m "Starting kernel.*") < /Users/Jon/Development/Code/Apps/CameraIMU/tmp/test.txt
                # tty 38400 cs8 -cstopb | ttylog - b 38400 - d /dev/tty.KeySerial1 > /Users/Jon/Development/Code/Apps/CameraIMU/tmp/imu2.txt
                # stty -F /dev/ttyS0 115200 cs8 parenb -parodd
                # proc = Popen("(stty -F " + imu_cfg['device'] + " 38400 cs8 -cstopb; cat > " + script_cfg['path'] + "/tmp/imu.txt)", shell=True)

                if imu_cfg['stream'] == 'binary':
                    proc = Popen(
                        "(stty " + imu_cfg['baudrate'] + " cs8 -cstopb -parity; cat > " + script_cfg['path'] + "/tmp/imu.dat | od -x) < " +
                        imu_cfg['device'], shell=True)
                else:
                    proc = Popen(
                        "(stty " + imu_cfg['baudrate'] + "; cat > " + script_cfg['path'] + "/tmp/imu.dat) < " +
                        imu_cfg['device'], shell=True)

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
            # we need to kill the secondary CAT process
            catID = pid+1
            kill(catID, SIGKILL)
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
            log = open(script_cfg['path'] + '/tmp/imu.dat', 'r')

            # loop the log information from the collected triggers
            for index, row in enumerate(rows):
                rowid = row[0]
                imu_byte = row[4]
                # read the file segment from the byte points
                log.seek(imu_byte, 0)
                line = log.readline()
                # make sure the head is what we thing it should be
                test_head = line[:18]

                if test_head == 'y-p-r-lat-long-elv':
                    print(test_head)
                else:
                    # get the next line
                    line = log.readline()

                variables = line.split(',')

                telemetry = {}
                telemetry['yaw'] = variables[1]
                telemetry['pitch'] = variables[2]
                telemetry['roll'] = variables[3]
                telemetry['lat'] = variables[4]
                telemetry['long'] = variables[5]
                telemetry['elv'] = variables[6].rstrip('\n')

                store = json.dumps(telemetry)

                # update this record to sql
                DBLite.UpdateTelemetry(DBLite, connection, script_cfg, store, rowid)

            return True

        except:

            if script_cfg['debug']:
                print("failed, segmenting imu file to sql blob")
            return False
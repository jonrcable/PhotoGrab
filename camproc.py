#!/usr/bin/python
import os, re, sqlite3, configparser, signal, serial
import bin.database
from subprocess import Popen
from _datetime import datetime, timedelta
from time import sleep, perf_counter
from shutil import copyfile
from tabulate import tabulate

# define our main class
class PhotoGrab:

    # lets init our master process
    def __init__(self, camera_cfg, imu_cfg, offsets_cfg, script_cfg):

        # lets bring our varibles into the class
        self.camera_cfg = camera_cfg
        self.imu_cfg = imu_cfg
        self.offsets_cfg = offsets_cfg
        self.script_cfg = script_cfg

        # lets set the the global process
        self.process = {}
        self.process['start'] = False # init the main process status to true
        self.process['connection'] = False # init the serial connection to false
        self.process['trigger'] = False # init the camera trigger to false
        self.process['loop'] = 0 # init the loop count
        self.process['count'] = 0 # init the fired count
        self.process['pid'] = 0  # the pid of the subprocess writing IMU data

        # init our serial connections
        self.camera_ser = None
        self.imu_ser = None

        # lets start things off
        self.Start()

    # lets kick off the process
    def Start(self):

        # report the start
        if self.script_cfg['debug']:
            print ('start looking for ', self.script_cfg['path'] + '/tmp/trigger.proc')
            print (' process start ', self.process['loop'], ' will run ', self.script_cfg['max'], ' or ', self.script_cfg['triggers'], ' triggers')

        # run some basic tests and conenct our script
        # these script hault on fail, see logs details
        self.process['start'] = self.Connect()

        # run the process if our tests are valid
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

                        # send the result to the database
                        event = self.InsertDB(result)

                    # otherwise lets see if a tigger file exists
                    else:

                        # look for the tigger file in the following path
                        if os.path.isfile(self.script_cfg['path'] + '/tmp/trigger.proc'):  # does the trigger file exists fire

                            # run the tigger process, now
                            result = self.Event(True)

                            # send the result to the database
                            event = self.InsertDB(result)

                            # remove the trigger file
                            os.remove(script_cfg['path'] + '/tmp/trigger.proc')

                        else:
                            # run the tigger process, fail
                            self.Event(False)

            except KeyboardInterrupt:
                print ("Bye early exit, closing connections")
                # close our connections
                self.CloseDB()
                self.StopIMU()
                exit()

    # If we need to close anything we do it here
    def End(self):

        # kill the imu process
        self.StopIMU()

        # if we have reached the end, should we report
        rows = self.DisplayDB()

        # get the name of our archive before we close the databse
        archive = self.GetArchiveName()

        # close our connections
        self.CloseDB()

        # move the database/imu data to a new store location
        self.Save(archive)

        if self.script_cfg['debug']:
            print(' process end ', self.process['loop'])

        # pretty print the final results
        print(tabulate(rows, headers=["Id", "Start", "Byte", "Stop", "Byte", "Delta", "Telemetry"], floatfmt=".12f"))

        self.process['start'] = False
        exit()

    # these are the init self checks for the process
    def Connect(self):

        # now try to start our services
        try:

            if self.script_cfg['debug']:
                print(' run all of our prechecks ')

            # create our directories
            self.CreateStructure()

            # cleanup any old jobs
            self.CleanUp()

            # init connection to a new sqlite database
            self.StartDB()

            #create a new databse table
            self.InitDB()
            if self.script_cfg['debug']:
                print(' new database connection successful ')

            # get the IMU data
            self.process['pid'] = self.StartIMU()
            # if this fails so should the script
            if not self.process['pid']:

                if self.script_cfg['debug']:
                    print(' new imu connection failed ')

                # close the database connection we no longer need it
                self.CloseDB()
                return  False

            else:
                if self.script_cfg['debug']:
                    print(' new imu connection successful ')
                return True

        except:
            # something went bad halt
            if self.script_cfg['debug']:
                print(' failed to open all the connections ')
            # fail
            return False

    # this is the actual process to trigger an event
    def Event(self, trigger):

        self.process['loop'] += 1  # this loop counts
        result = {}

        # if we have a trigger lets do this
        if trigger:

            self.process['count'] += 1  # this trigger counts

            if self.script_cfg['debug']:
                print(' trigger true ', self.process['count'])

            # grab a reliable piece of time
            # trigger = self.GetIMU() # request the time from the IMU, def the way we want
            trigger = datetime.now()  # system time, if we can get above we ignore this

            # get the start byte of our imu file
            start_byte = os.path.getsize(self.script_cfg['path'] + '/tmp/imu.txt')
            # start the timer
            start = perf_counter()

            # lets fire the camera trigger
            self.Trigger()
            # tmp holder for the IMU data
            result['telemetry'] = ''

            # get the stop byte of our imu file
            stop_byte = os.path.getsize(self.script_cfg['path'] + '/tmp/imu.txt')
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

            if self.script_cfg['debug']:
                print(' started - ', trigger)
                print(" - elapsed time = {:.12f} seconds".format(elapsed))
                print(' ended - ', delta)

            return result

        # otherwise lets just do cleanup or whatever
        else:

            if self.script_cfg['debug']:
                print('trigger false ', self.process['loop'], ' of ', self.script_cfg['max'])

            sleep(self.offsets_cfg['rest'])  # we should rest for X before we start again

            return result

    # this is the trigger process for the camera
    def Trigger(self):

        sleep(1)
        return

    # this is the serial process to get the IMU data
    def StartIMU(self):

        # simple test to see if the imu is running
        if os.path.exists(self.imu_cfg['device']):

            try:
                # write our log file
                log = open(self.script_cfg['path'] + '/tmp/imu.txt', 'a')
                log.write('start of the imu output\n')
                log.flush()  # <-- here's something not to forget!

                # run a simple cat command as a background process to capture the data to a file
                proc = Popen("cat " + self.imu_cfg['device'], stdout=log, stderr=log, shell=True)
                if self.script_cfg['debug']:
                    print(" imu collection started process: ", proc.pid)

                # return the process id of the imu data collection
                return proc.pid

            except:
                print(' failed to start IMU data hault ')
                exit()

        else:
            print(' device is not connected try again hault ')
            return False

    # this is the serial process to stop the imu process
    def StopIMU(self):

        try:
            # kil the data collection background process
            os.kill(self.process['pid'], signal.SIGKILL)
            if self.script_cfg['debug']:
                print(" imu data collection stopped: ", self.process['pid'])
            return True

        except:
            if self.script_cfg['debug']:
                print(" imu data collection failed to stop: ", self.process['pid'])
            return False

    # create the directory structure
    def CreateStructure(self):

        try:
            # we might need to create a few dirs
            if not os.path.isdir(self.script_cfg['path'] + '/tmp'):
                os.mkdir(self.script_cfg['path'] + '/tmp')
                if self.script_cfg['debug']:
                    print (' created a tmp folder ')

            if not os.path.isdir(self.script_cfg['archive'] + '/archives'):
                os.mkdir(self.script_cfg['archive'] + '/archives')
                if self.script_cfg['debug']:
                    print(' created an archive directory ')

        except:
            print(' failed to create directory hault')
            exit()

        return True

    # cleanup any old stuff from the last job
    def CleanUp(self):
        # test if a previous database file exists
        if os.path.isfile(self.script_cfg['path'] + '/tmp/process.sqlite'):
            try:
                # remove the trigger file
                os.remove(script_cfg['path'] + '/tmp/process.sqlite')
                if self.script_cfg['debug']:
                    print(' removed a stale database file ')

            except:
                # something went bad halt
                if self.script_cfg['debug']:
                    print(' no old database to worry about ')
                # fail
                return False

        # test if a previous imu file eists
        if os.path.isfile(self.script_cfg['path'] + '/tmp/imu.txt'):
            try:
                # remove the trigger file
                os.remove(script_cfg['path'] + '/tmp/imu.txt')
                if self.script_cfg['debug']:
                    print(' removed a stale imu file ')

            except:
                # something went bad halt
                if self.script_cfg['debug']:
                    print(' no old imu file to worry about ')
                # fail
                return False

        return True

    # create the new database structure
    def InitDB(self):

        try:
            # create the new table to store the telemetry
            self.database.execute(
                'CREATE TABLE triggers (trigger VARCHAR, elapsed VARCHAR, delta INTEGER, start_byte INTEGER, stop_byte INTEGER, telemetry TEXT)')
            self.sql.commit()

            if self.script_cfg['debug']:
                print(' created a new triggers table ')
            return True

        except:
            # something went bad halt
            if self.script_cfg['debug']:
                print(' failed to create a new database ')
            # fail
            return False

    # start the database connection
    def StartDB(self):
        # init connection to a new sqlite database
        self.sql = sqlite3.connect(self.script_cfg['path'] + '/tmp/process.sqlite')
        self.database = self.sql.cursor()

        return

    # if we opened connections we need to close them
    def CloseDB(self):

        # if we opened these we have to close them
        # close the sql connection
        self.sql.close()
        if self.script_cfg['debug']:
            print(' sql connection closed ')

        return

    # insert a new row into the database
    def InsertDB(self, result):

        try:
            # create the new table to store the telemetry
            self.database.execute('''INSERT INTO triggers (trigger, elapsed, delta, start_byte, stop_byte, telemetry) VALUES(?,?,?,?,?,?)''',
                                  (result['trigger'], result['elapsed'], result['delta'], result['start_byte'], result['stop_byte'], result['telemetry']))
            self.sql.commit()

            if self.script_cfg['debug']:
                print(' inserted new event to table ')
            return True

        except:
            # something went bad halt
            if self.script_cfg['debug']:
                print(' failed to insert event to table ', result)
            # fail
            return False

    # display pretty results
    def DisplayDB(self):

        try:
            # get all the rows
            self.database.execute('SELECT rowid, trigger, start_byte, delta, stop_byte, elapsed, telemetry FROM triggers')
            rows =  self.database.fetchall()

            return rows

        except:
            # nothing to display
            print(' failed to display the summary event ')

            return False

    # return the name of he archive before we close the sq databse
    def GetArchiveName(self):

        try:
            # get the last row from the table
            self.database.execute('SELECT rowid, trigger FROM triggers ORDER BY rowid LIMIT 1')
            save =  self.database.fetchone()
            # remove any special chars
            archive = re.sub('[^a-zA-Z0-9\n]', '', save[1])

            return archive
        except:
            print(' fail to get the archive name ')

    # finally archive the database to its store location
    def Save(self, archive):
        try:

            # make sure the dir does not already exists and create it
            if not os.path.isdir(self.script_cfg['path'] + '/archives/' + archive):
                os.mkdir(self.script_cfg['path'] + '/archives/' + archive)
                if self.script_cfg['debug']:
                    print(' created an process directory ')

            # move the process to the archive
            copyfile(self.script_cfg['path'] + '/tmp/process.sqlite', self.script_cfg['archive'] + '/archives/' + archive + '/db.sqlite')
            print(' sql archive saved ', self.script_cfg['archive'] + '/archives/' + archive + '/db.sqlite')
            # move the process to the archive
            copyfile(self.script_cfg['path'] + '/tmp/imu.txt', self.script_cfg['archive'] + '/archives/' + archive + '/binary.txt')
            print(' imu archive saved ', self.script_cfg['archive'] + '/archives/' + archive + '/imu.txt')

            return True

        except:
            # nothing to save
            if self.script_cfg['debug']:
                print(' the archive was not saved ')

            return False

# RUN THIS AUTO
# choose a custom config or fail
if os.path.isfile('config.inc'):

    # open the config
    config = configparser.ConfigParser()
    config.read('config.inc')

    # we have a configuration lets setup the process

    # these are to store the hardware configs
    camera_cfg = {}
    camera_cfg['baudrate'] = config.getint('camera_cfg', 'baudrate')
    camera_cfg['parity'] = config.get('camera_cfg', 'parity')
    camera_cfg['stopbit'] = config.getint('camera_cfg', 'stopbit')
    camera_cfg['datalen'] = config.getint('camera_cfg', 'datalen')

    imu_cfg = {}
    imu_cfg['device'] = config.get('imu_cfg', 'device')

    # these are to store the project configs
    offsets_cfg = {}
    offsets_cfg['rest'] = config.getint('offsets_cfg', 'rest')  # time in sec to rest if no trigger, 0 none

    # general script configs
    script_cfg = {}
    script_cfg['debug'] = config.getboolean('script_cfg', 'debug')  # do you want to print out the debug information
    script_cfg['headless'] = config.getboolean('script_cfg', 'headless')  # do you to run autonomously, till max BEWARE: when max set to 0 and this is True - infinity
    script_cfg['path'] = config.get('script_cfg', 'path')  # path of the directory to process from
    script_cfg['archive'] = config.get('script_cfg', 'archive')  # path of the directory to archive too
    script_cfg['max'] = config.getint('script_cfg', 'max')  # max attempts at running this loop, 0 infinite
    script_cfg['triggers'] = config.getint('script_cfg', 'triggers')  # max triggers before ending this loop, 0 infinite

    # Lets kick off the process
    PhotoGrab(camera_cfg, imu_cfg, offsets_cfg, script_cfg)

else:
    # no config file hard stop
    print(' copy config.default to config.inc and setup the script')
    exit()
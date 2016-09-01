#!/usr/bin/python
import os, re, sqlite3
from _datetime import datetime, timedelta
from time import sleep, perf_counter
from shutil import copyfile
from tabulate import tabulate

# these are to store the hardware configs
camera_cfg = {}
imu_cfg = {}

# these are to store the project configs
offsets_cfg = {}
offsets_cfg['rest'] = 1 # time in sec to rest if no trigger, 0 none

# general script configs
script_cfg = {}
script_cfg['debug'] = False # do you want to print out the debug information
script_cfg['headless'] = True # do you to run autonomously, till max BEWARE: when max set to 0 and this is True - infinity
script_cfg['path'] = '/Users/Jon/Development/Code/Apps/CameraIMU' # path of the directory to monitor
script_cfg['max'] = 50 # max attempts at running this loop, 0 infinite
script_cfg['triggers'] = 10 # max triggers before ending this loop, 0 infinite

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

        # lets start things off
        self.Start()

    # lets kick off the process
    def Start(self):

        if self.script_cfg['debug']:
            print ('start looking for ', self.script_cfg['path'] + '/tmp/trigger.proc')
            print (' process start ', self.process['loop'], ' will run ', self.script_cfg['max'], ' or ', self.script_cfg['triggers'], ' triggers')

        # run some basic tests
        self.process['start'] = self.Connect()

        # run the process if our tests are valid
        while self.process['start']: # constructs our process loop

            # start monitoring our process

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


    # these are the init self checks for the process
    def Connect(self):

        if self.script_cfg['debug']:
            print (' run all of our prechecks ')

        # we might need to create a few dirs
        if not os.path.isdir(self.script_cfg['path'] + '/tmp'):
            os.mkdir(self.script_cfg['path'] + '/tmp')
            if self.script_cfg['debug']:
                print (' created a tmp folder ')

        if not os.path.isdir(self.script_cfg['path'] + '/archives'):
            os.mkdir(self.script_cfg['path'] + '/archives')
            if self.script_cfg['debug']:
                print(' created an archive directory ')

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
                    print(' failed to remove a stale database ')
                # fail
                return False

        # now try to start the database conection
        try:
            # init connection to a new sqlite database
            self.sql = sqlite3.connect(self.script_cfg['path'] + '/tmp/process.sqlite')
            self.database = self.sql.cursor()

            #create a new databse table
            self.InitDB()

            if self.script_cfg['debug']:
                print(' new database connection successful ')

        except:
            # something went bad halt
            if self.script_cfg['debug']:
                print(' failed to create a new database ')
            # fail
            return False

        return True


    # create the new database structure
    def InitDB(self):

        try:
            # create the new table to store the telemetry
            self.database.execute(
                'CREATE TABLE triggers (trigger VARCHAR, elapsed VARCHAR, delta INTEGER, telemetry BLOB)')
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


    # insert a new row into the database
    def InsertDB(self, result):

        try:
            # create the new table to store the telemetry
            self.database.execute('''INSERT INTO triggers (trigger, elapsed, delta, telemetry) VALUES(?,?,?,?)''',
                                  (result['trigger'], result['elapsed'], result['delta'], result['telemetry']))
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

    def DisplayDB(self):

        try:
            self.database.execute('SELECT rowid, trigger, delta, elapsed, telemetry FROM triggers')

            rows =  self.database.fetchall()

            print(tabulate(rows, headers=["Id", "Start", "Stop", "Delta", "Telemetry"], floatfmt=".12f"))

        except:
            print(' failed to display the summary event ')

        return

    # If we need to close anything we do it here
    def End(self):

        # if we have reached the end, should we report
        self.DisplayDB()

        # move the database to a new store location
        self.Save()

        # close the sql connection
        self.sql.close()

        if self.script_cfg['debug']:
            print (' sql connection closed ')
            print (' process end ', self.process['loop'])

        self.process['start'] = False
        exit()

    # finally archive the database to its store location
    def Save(self):
        try:
            self.database.execute('SELECT rowid, trigger, delta, elapsed, telemetry FROM triggers ORDER BY rowid LIMIT 1')
            save =  self.database.fetchone()
            archive = re.sub('[^a-zA-Z0-9\n]', '', save[1])

            if not os.path.isdir(self.script_cfg['path'] + '/archives/' + archive):
                os.mkdir(self.script_cfg['path'] + '/archives/' + archive)
                if self.script_cfg['debug']:
                    print(' created an process directory ')

            copyfile(self.script_cfg['path'] + '/tmp/process.sqlite', self.script_cfg['path'] + '/archives/' + archive + '/db.sqlite')
            print(' archive saved ', self.script_cfg['path'] + '/db/' + archive + '.sqlite')

        except:

            if self.script_cfg['debug']:
                print(' the archive was not saved ')

            return

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

            # start the timer
            start = perf_counter()

            # lets fire the camera trigger
            # self.Trigger()
            # tmp holder for the IMU data
            result['telemetry'] = ''

            # end the counter
            stop = perf_counter()

            # report the elapsed time it took to run this process
            elapsed = stop - start
            # get the end time
            delta = trigger + timedelta(elapsed)

            result['trigger'] = format(trigger)
            result['elapsed'] = "{:.12f}".format(elapsed)
            result['delta'] = format(delta)

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

        return

    # this is the serial process to get the IMU data
    def GetIMU(self):

        return

# Lets kick off the process
PhotoGrab(camera_cfg, imu_cfg, offsets_cfg, script_cfg)
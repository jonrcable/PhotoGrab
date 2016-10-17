#!/usr/bin/python
import json
from os import path, mkdir, makedirs, remove
from shutil import copyfile, copytree, rmtree, make_archive

# define our file class
class FileStruct:

    # create the directory structure
    def CreateStructure(self, script_cfg):

        try:
            # we might need to create a few dirs
            if not path.isdir(script_cfg['path'] + '/tmp'):
                makedirs(script_cfg['path'] + '/tmp')
                if script_cfg['debug']:
                    print (' created a tmp folder ')

            if not path.isdir(script_cfg['archive'] + '/archives'):
                mkdir(script_cfg['archive'] + '/archives')
                if script_cfg['debug']:
                    print(' created an archive directory ')

            if script_cfg['debug']:
                print(' created default directories')

            return True

        except:

            if script_cfg['debug']:
                print(' failed to create directory hault')
            return False

    # cleanup any old stuff from the last job
    def CleanUp(self, script_cfg):

        try:
            # test if a previous database file exists
            # if path.isfile(script_cfg['path'] + '/tmp/process.sqlite'):
                # remove the trigger file
            #    remove(script_cfg['path'] + '/tmp/process.sqlite')
            #    if script_cfg['debug']:
            #        print(' removed a stale database file ')

            # test if a previous imu file exists
            # if path.isfile(script_cfg['path'] + '/tmp/imu.dat'):
                # remove the trigger file
            #    remove(script_cfg['path'] + '/tmp/imu.dat')
            #    if script_cfg['debug']:
            #        print(' removed a stale imu file ')

            # test if a previous trigger file exists
            # if path.isfile(script_cfg['path'] + '/tmp/trigger.proc'):
                # remove the trigger file
            #    remove(script_cfg['path'] + '/tmp/trigger.proc')
            #    if script_cfg['debug']:
            #        print(' removed a stale trigger file ')

            # test if a previous image dir exists
            if path.isdir(script_cfg['path'] + '/tmp'):
                # remove the trigger file
                rmtree(script_cfg['path'] + '/tmp')
                if script_cfg['debug']:
                    print(' removed a stale tmp directory ')

            return True

        except:

            if script_cfg['debug']:
                print(' failed to cleanup directory ')

            return False

    # write a csv file from the database
    def WriteCSV(self, script_cfg, rows):

        try:

            with open(script_cfg['path'] + '/tmp/export.csv', 'w') as f:

                for index, row in enumerate(rows):
                    f.write(
                        '{0},{1},{2},{3},{4},{5},{6}\n'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

            if script_cfg['debug']:
                print(" writing a friendly csv file ")

            return True

        except:

            if script_cfg['debug']:
                print(' failed to write csv file ')

            return False

    # write a csv file from the database
    def ProcessedCSV(self, script_cfg, rows):

        try:

            with open(script_cfg['path'] + '/tmp/processed.csv', 'w') as f:

                for index, row in enumerate(rows):
                    #rowid0, trigger1, trigger_lapse2, camera_lapse3, imu_byte4, image5, size6, telemetry7

                    telemetry = json.loads(row[7])
                    #telemetry['yaw'] = variables[1]
                    #telemetry['pitch'] = variables[2]
                    #telemetry['roll'] = variables[3]
                    #telemetry['lat'] = variables[4]
                    #telemetry['long'] = variables[5]
                    #telemetry['elv'] = variables[6].rstrip('\n')

                    # from AGI v.01
                    # str("nyxzacb")  # n - label, x/y/z - coordinates, a/b/c - yaw, pitch, roll

                    # row[5], telemetry['lat'], telemetry['long'], telemetry['elv'], telemetry['yaw'], telemetry['pitch'], telemetry['roll']

                    f.write(
                        '{0},{1},{2},{3},{4},{5},{6}\n'.format(row[5], telemetry['lat'], telemetry['long'], telemetry['elv'],
                                                               telemetry['yaw'], telemetry['pitch'], telemetry['roll']))

            if script_cfg['debug']:
                print(" writing a friendly AGI file! ")

            return True

        except:

            if script_cfg['debug']:
                print(' failed to write csv file ')

            return False

    # finally archive the database to its store location
    def Save(self, script_cfg, archive):

        try:

            if path.isfile(script_cfg['path'] + '/tmp/stop.proc'):
                remove(script_cfg['path'] + '/tmp/stop.proc')

            if path.isfile(script_cfg['path'] + '/tmp/trigger.proc'):
                remove(script_cfg['path'] + '/tmp/trigger.proc')

            # make an archive file of all of the contents
            make_archive(script_cfg['archive'] + '/archives/' + archive, 'zip', script_cfg['path'] + '/tmp')

            if script_cfg['debug']:
                print('| archive saved, ', script_cfg['archive'] + '/archives/' + archive + '.zip |')

            return True

        except:
            # nothing to save
            if script_cfg['debug']:
                print(' the archive was not saved ')

            return False
#!/usr/bin/python
from os import path, mkdir, remove
from shutil import copyfile, copytree, rmtree, make_archive

# define our file class
class FileStruct:

    # create the directory structure
    def CreateStructure(self, script_cfg):

        try:
            # we might need to create a few dirs
            if not path.isdir(script_cfg['path'] + '/tmp'):
                mkdir(script_cfg['path'] + '/tmp')
                if script_cfg['debug']:
                    print (' created a tmp folder ')

            if not path.isdir(script_cfg['archive'] + '/archives'):
                mkdir(script_cfg['archive'] + '/archives')
                if script_cfg['debug']:
                    print(' created an archive directory ')

        except:
            print(' failed to create directory hault')
            exit()

        return True

    # cleanup any old stuff from the last job
    def CleanUp(self, script_cfg):
        # test if a previous database file exists
        if path.isfile(script_cfg['path'] + '/tmp/process.sqlite'):
            try:
                # remove the trigger file
                remove(script_cfg['path'] + '/tmp/process.sqlite')
                if script_cfg['debug']:
                    print(' removed a stale database file ')

            except:
                # something went bad halt
                if script_cfg['debug']:
                    print(' no old database to worry about ')
                # fail
                return False

        # test if a previous imu file exists
        if path.isfile(script_cfg['path'] + '/tmp/imu.txt'):
            try:
                # remove the trigger file
                remove(script_cfg['path'] + '/tmp/imu.txt')
                if script_cfg['debug']:
                    print(' removed a stale imu file ')

            except:
                # something went bad halt
                if script_cfg['debug']:
                    print(' no old imu file to worry about ')
                # fail
                return False

        # test if a previous trigger file exists
        if path.isfile(script_cfg['path'] + '/tmp/trigger.proc'):
            try:
                # remove the trigger file
                remove(script_cfg['path'] + '/tmp/trigger.proc')
                if script_cfg['debug']:
                    print(' removed a stale trigger file ')

            except:
                # something went bad halt
                if script_cfg['debug']:
                    print(' no old trigger file to worry about ')
                # fail
                return False

        # test if a previous image dir exists
        if path.isdir(script_cfg['path'] + '/tmp/images'):
            try:
                # remove the trigger file
                rmtree(script_cfg['path'] + '/tmp/images')
                if script_cfg['debug']:
                    print(' removed a stale images directory ')

            except:
                # something went bad halt
                if script_cfg['debug']:
                    print(' failed to removed a stale images directory ')
                # fail
                return False

        return True

    def WriteCSV(self, script_cfg, rows):

        try:

            print(" writing a friendly csv file ")

            with open(script_cfg['path'] + '/tmp/export.csv', 'w') as f:

                for index, row in enumerate(rows):
                    f.write(
                        '{0},{1},{2},{3},{4},{5},{6},{7},{8}\n'.format(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                       row[6], row[7], row[8]))

            return True

        except:

            return False

    # finally archive the database to its store location
    def Save(self, script_cfg, archive):

        try:

            # make sure the dir does not already exists and create it
            #if not path.isdir(script_cfg['path'] + '/archives/' + archive):
            #    mkdir(script_cfg['path'] + '/archives/' + archive)
            #    if script_cfg['debug']:
            #        print(' created an process directory ')

            # make an archive file of all of the contents
            make_archive(script_cfg['archive'] + '/archives/' + archive, 'zip', script_cfg['path'] + '/tmp')

            # move the images to an archive
            # copytree(script_cfg['path'] + '/tmp/images', script_cfg['archive'] + '/archives/' + archive + "/images")
            # move the process to the archive
            # copyfile(script_cfg['path'] + '/tmp/process.sqlite', script_cfg['archive'] + '/archives/' + archive + '/db.sqlite')
            # move the process to the archive
            # copyfile(script_cfg['path'] + '/tmp/imu.txt', script_cfg['archive'] + '/archives/' + archive + '/binary.dat')
            # move the process to the archive
            # copyfile(script_cfg['path'] + '/tmp/export.csv', script_cfg['archive'] + '/archives/' + archive + '/export.csv')

            print('| archive saved, ', script_cfg['archive'] + '/archives/' + archive + '.zip |')

            return True

        except:
            # nothing to save
            if script_cfg['debug']:
                print(' the archive was not saved ')

            return False
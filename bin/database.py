#!/usr/bin/python
import re, sqlite3

# define our database class
class DBLite:

    # create the new database structure
    def InitDB(self, connection, script_cfg):

        try:
            # create the new table to store the telemetry

            connection['database'].execute(
                'CREATE TABLE triggers (trigger VARCHAR, trigger_lapse VARCHAR, camera_lapse VARCHAR, imu_byte INTEGER, telemetry BLOB, image VARCHAR, size INTEGER)')

            connection['sql'].commit()

            if script_cfg['debug']:
                print(' created a new triggers table ')
            return True

        except:
            # something went bad halt
            if script_cfg['debug']:
                print(' failed to create a new database table')
            # fail
            return False

    # start the database connection
    def StartDB(self, script_cfg):

        try:

            connection = {}
            # init connection to a new sqlite database
            connection['sql'] = sqlite3.connect(script_cfg['path'] + '/tmp/process.sqlite')
            connection['database'] = connection['sql'].cursor()

            if script_cfg['debug']:
                print(' new database connection opened ')
            return connection

        except:
            # something went bad halt
            if script_cfg['debug']:
                print(' failed to create a new database connection ')
            # fail
            return False

    # if we opened connections we need to close them
    def CloseDB(self, connection, script_cfg):

        # if we opened these we have to close them
        # close the sql connection
        connection['sql'].close()
        if script_cfg['debug']:
            print(' sql connection closed ')

        return

    # insert a new row into the database
    def InsertDB(self, connection, script_cfg, result):

        try:
            # create the new table to store the telemetry
            connection['database'].execute('''INSERT INTO triggers (trigger, trigger_lapse, camera_lapse, imu_byte, telemetry, image, size) VALUES(?,?,?,?,?,?,?)''',
                                  (result['trigger'], result['trigger_lapse'], result['camera_lapse'], result['imu_byte'], result['telemetry'], result['image'], result['size']))
            connection['sql'].commit()

            if script_cfg['debug']:
                print(' inserted new event to table ')
            return True

        except:
            # something went bad halt
            if script_cfg['debug']:
                print(' failed to insert event to table ', result)
            # fail
            return False

    # display pretty results
    def DisplayDB(self, connection, script_cfg):

        try:
            # get all the rows
            connection['database'].execute('SELECT rowid, trigger, trigger_lapse, camera_lapse, imu_byte, image, size, telemetry FROM triggers')
            rows = connection['database'].fetchall()

            if script_cfg['debug']:
                print(' capture event summary ')

            return rows

        except:
            # nothing to display
            if script_cfg['debug']:
                print(' failed to caputure summary event ')

            return False

    # return the name of he archive before we close the sq databse
    def GetArchiveName(self, connection, script_cfg):

        try:
            # get the last row from the table
            connection['database'].execute('SELECT rowid, trigger FROM triggers ORDER BY rowid LIMIT 1')
            save = connection['database'].fetchone()
            # remove any special chars
            archive = re.sub('[^a-zA-Z0-9\n]', '', save[1])

            return archive
        except:
            print(' fail to get the archive name ')

            return False

    # MAYBE, not currently in use
    # update a row with its telemetry
    def UpdateTelemetry(self, connection, script_cfg, binary, rowid):
        try:

            connection['database'].execute("UPDATE triggers SET telemetry = ? WHERE rowid = ?", (binary, rowid))
            connection['sql'].commit()

            if script_cfg['debug']:
                print(" updated trigger", rowid, "with imu information ")

            return True

        except:

            if script_cfg['debug']:
                print(" fail to update trigger", rowid, "with imu information ")

            return False

    # DEPRECIATED, left for sort logic
    # line up each row with the proper image
    def UpdateImages(self, connection, script_cfg, rows, images):
        try:

            # loop the log information from the collected triggers
            i = 0
            for index, row in enumerate(rows):
                image = images[i].split(script_cfg['path'] + "/tmp/images")
                rowid = row[0]
                connection['database'].execute("UPDATE triggers SET image = ? WHERE rowid = ?", (image[1], rowid))
                connection['sql'].commit()
                print(" matched img to sql", image[1])
                i += 1

            return True

        except:

            if script_cfg['debug']:
                print(" failed to updates images in the database ")

            return False
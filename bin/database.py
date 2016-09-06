#!/usr/bin/python
import re, sqlite3

# define our database class
class DBLite:

    # create the new database structure
    def InitDB(self, connection, script_cfg):

        try:
            # create the new table to store the telemetry
            connection['database'].execute(
                'CREATE TABLE triggers (trigger VARCHAR, elapsed VARCHAR, delta INTEGER, start_byte INTEGER, stop_byte INTEGER, size INTEGER, telemetry BLOB)')
            connection['sql'].commit()

            if script_cfg['debug']:
                print(' created a new triggers table ')
            return True

        except:
            # something went bad halt
            if script_cfg['debug']:
                print(' failed to create a new database ')
            # fail
            return False

    # start the database connection
    def StartDB(self, script_cfg):

        connection = {}
        # init connection to a new sqlite database
        connection['sql'] = sqlite3.connect(script_cfg['path'] + '/tmp/process.sqlite')
        connection['database'] = connection['sql'].cursor()

        return connection

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
            connection['database'].execute('''INSERT INTO triggers (trigger, elapsed, delta, start_byte, stop_byte, size, telemetry) VALUES(?,?,?,?,?,?, ?)''',
                                  (result['trigger'], result['elapsed'], result['delta'], result['start_byte'], result['stop_byte'], result['size'], result['telemetry']))
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
            connection['database'].execute('SELECT rowid, trigger, start_byte, delta, stop_byte, elapsed, size, length(telemetry) FROM triggers')
            rows = connection['database'].fetchall()

            if script_cfg['debug']:
                print(' capture event summary ')

            return rows

        except:
            # nothing to display
            if script_cfg['debug']:
                print(' failed to caputure summary event ')

            return False

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
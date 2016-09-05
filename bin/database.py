#!/usr/bin/python
import re, sqlite3

# define our database class
class DBLite:

    # start the database connection
    def StartDB(self, script_cfg):
        # init connection to a new sqlite database
        sql = sqlite3.connect(script_cfg['path'] + '/tmp/process.sqlite')
        database = sql.cursor()

        result = {}
        result['sql'] = sql
        result['database'] = database

        return result

    # create the new database structure
    def InitDB(self, database, sql, script_cfg):

        try:
            # create the new table to store the telemetry
            database.execute(
                'CREATE TABLE triggers (trigger VARCHAR, elapsed VARCHAR, delta INTEGER, start_byte INTEGER, stop_byte INTEGER, telemetry TEXT)')
            sql.commit()

            if script_cfg['debug']:
                print(' created a new triggers table ')
            return True

        except:
            # something went bad halt
            if script_cfg['debug']:
                print(' failed to create a new database ')
            # fail
            return False

    # if we opened connections we need to close them
    def CloseDB(self, sql, script_cfg):

        # if we opened these we have to close them
        # close the sql connection
        sql.close()
        if script_cfg['debug']:
            print(' sql connection closed ')

        return

    # insert a new row into the database
    def InsertDB(self, database, sql, script_cfg, result):

        try:
            # create the new table to store the telemetry
            database.execute('''INSERT INTO triggers (trigger, elapsed, delta, start_byte, stop_byte, telemetry) VALUES(?,?,?,?,?,?)''',
                                  (result['trigger'], result['elapsed'], result['delta'], result['start_byte'], result['stop_byte'], result['telemetry']))
            sql.commit()

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
    def DisplayDB(self, database):

        try:
            # get all the rows
            database.execute('SELECT rowid, trigger, start_byte, delta, stop_byte, elapsed, telemetry FROM triggers')
            rows =  database.fetchall()

            return rows

        except:
            # nothing to display
            print(' failed to display the summary event ')

            return False

    # return the name of he archive before we close the sq databse
    def GetArchiveName(self, database):

        try:
            # get the last row from the table
            database.execute('SELECT rowid, trigger FROM triggers ORDER BY rowid LIMIT 1')
            save =  database.fetchone()
            # remove any special chars
            archive = re.sub('[^a-zA-Z0-9\n]', '', save[1])

            return archive
        except:
            print(' fail to get the archive name ')
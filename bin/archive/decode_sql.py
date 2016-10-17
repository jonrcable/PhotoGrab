#!/usr/bin/python
import sqlite3

connection = {}
# init connection to a new sqlite database
connection['sql'] = sqlite3.connect('/Users/Jon/Development/Code/Apps/CameraIMU/archives/20160906153140892363/db.sqlite')
connection['database'] = connection['sql'].cursor()

# get all the rows
connection['database'].execute(
    'SELECT rowid, trigger, start_byte, delta, stop_byte, elapsed, size, telemetry FROM triggers')
rows = connection['database'].fetchall()

# loop the log information from the collected triggers
for index, row in enumerate(rows):
    binary = row[7].decode()

    print(binary)

# close the sql connection
connection['sql'].close()
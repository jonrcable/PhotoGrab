
import struct

# write our log file
log = open('/Users/Jon/Development/Code/Apps/CameraIMU/archives/20160906153140892363/binary.txt', 'rb')
edit = str (log.read())

log.close()

test = edit.find('\0xCA')

print(test)

# start - byte - preable 0xCA



#!/bin/sh
### BEGIN INIT INFO
# Provides: A ramdisk to save intermittent data
# Required-Start:
# Required-Stop:
# X-Start-Before:
# X-Stop-After:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: create a ramdisk
# Description: create a ramdisk with 64MB and mount it to /media/ram0
### END INIT INFO
#
case "$1" in
    start)
        if [ ! -e /media/ram0 ]; then
                mkdir /media/ram0
        fi
        /sbin/mke2fs -m 0 /dev/ram0
        /bin/mount /dev/ram0 /media/ram0
;;
    stop)
/bin/umount -v /media/ram0
;;
restart)
/bin/mount /dev/ram0 /media/ram0
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart}"
        exit 1
esac
exit 0
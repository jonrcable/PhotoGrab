#!/usr/bin/python
from configparser import ConfigParser
from os import path

# load our custom classes
from bin.photo import PhotoGrab

# RUN THIS AUTO
# choose a custom config or fail
if path.isfile('config.inc'):

    # open the config
    config = ConfigParser()
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
    imu_cfg['delay'] = config.getint('imu_cfg', 'delay')

    # these are to store the project configs
    offsets_cfg = {}
    offsets_cfg['rest'] = config.getfloat('offsets_cfg', 'rest')  # time in sec to rest if no trigger, 0 none

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
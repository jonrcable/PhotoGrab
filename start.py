#!/usr/bin/python
from configparser import ConfigParser
from os import path

# load our custom classes
from bin.photo_pi import PhotoGrab

# RUN THIS AUTO
# choose a custom config or fail
if path.isfile('config.inc'):

    # open the config
    config = ConfigParser()
    config.read('config.inc')

    # we have a configuration lets setup the process

    # these are to store the hardware configs
    camera_cfg = {}
    camera_cfg['exposure_mode'] = config.get('camera_cfg', 'exposure_mode')
    camera_cfg['iso'] = config.getint('camera_cfg', 'iso')
    camera_cfg['awb_mode'] = config.get('camera_cfg', 'awb_mode')
    camera_cfg['awb_gains'] = config.getfloat('camera_cfg', 'awb_gains')
    camera_cfg['shutter_speed'] = config.getint('camera_cfg', 'shutter_speed')
    camera_cfg['brightness'] = config.getint('camera_cfg', 'brightness')
    camera_cfg['resolution'] = config.get('camera_cfg', 'resolution')
    camera_cfg['sensor_mode'] = config.getint('camera_cfg', 'sensor_mode')
    camera_cfg['exposure_compensation'] = config.getint('camera_cfg', 'exposure_compensation')
    camera_cfg['meter_mode'] = config.get('camera_cfg', 'meter_mode')
    camera_cfg['contrast'] = config.getint('camera_cfg', 'contrast')
    camera_cfg['led_count'] = config.getint('camera_cfg', 'led_count')
    camera_cfg['led_pin'] = config.getint('camera_cfg', 'led_pin')
    camera_cfg['led_freq_hz'] = config.getint('camera_cfg', 'led_freq_hz')
    camera_cfg['led_dma'] = config.getint('camera_cfg', 'led_dma')
    camera_cfg['led_brightness'] = config.getint('camera_cfg', 'led_brightness')
    camera_cfg['led_inverter'] = config.getboolean('camera_cfg', 'led_inverter')
    camera_cfg['led_channel'] = config.getint('camera_cfg', 'led_channel')
    camera_cfg['led_color_r'] = config.getint('camera_cfg', 'led_color_r')
    camera_cfg['led_color_g'] = config.getint('camera_cfg', 'led_color_g')
    camera_cfg['led_color_b'] = config.getint('camera_cfg', 'led_color_b')

    imu_cfg = {}
    imu_cfg['stream'] = config.get('imu_cfg', 'stream')
    imu_cfg['baudrate'] = config.get('imu_cfg', 'baudrate')
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
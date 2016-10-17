# cannon7d test script
# dated fail tests - does not work for PR
# camera is not for underwater tests

import os
import gphoto2 as gp
from time import sleep, perf_counter
from _datetime import datetime, timedelta

context = gp.gp_context_new()
camera = gp.check_result(gp.gp_camera_new())

gp.check_result(gp.gp_camera_init(camera, context))

print("Capture Image")

# start the timer
trigger = datetime.now()  # system time, if we can get above we ignore this
start = perf_counter()

file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_MOVIE, context))

# end the counter
stop = perf_counter()

# report the elapsed time it took to run this process
elapsed = stop - start
# get the end time
delta = trigger + timedelta(0, elapsed)

print(elapsed)

print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

target = os.path.join('/tmp', file_path.name)

print('copying image to', target)

camera_file = gp.check_result(gp.gp_camera_file_get(camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, context))

gp.check_result(gp.gp_file_save(camera_file, target))

gp.check_result(gp.gp_camera_exit(camera, context))


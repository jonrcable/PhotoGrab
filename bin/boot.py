#!/bin/python
import RPi.GPIO as GPIO
from subprocess import Popen, DEVNULL
from time import sleep, time
from neopixel import *

# define our main class
class BootCamera:

    def __init__(self):

        shutdown_gpio_pin_number=14
        camera_gpio_pin_number=24
        trigger_gpio_pin_number=23
        led_gpio_pin_number = 18

        GPIO.setmode(GPIO.BCM)
        # GPIO.setup(shutdown_gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(shutdown_gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(camera_gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(trigger_gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(shutdown_gpio_pin_number, GPIO.BOTH, bouncetime=2000)
        GPIO.add_event_detect(camera_gpio_pin_number, GPIO.BOTH, bouncetime=2000)
        GPIO.add_event_detect(trigger_gpio_pin_number, GPIO.BOTH, bouncetime=750)

        GPIO.add_event_callback(shutdown_gpio_pin_number, self.Shutdown)
        GPIO.add_event_callback(camera_gpio_pin_number, self.CameraAction)
        GPIO.add_event_callback(trigger_gpio_pin_number, self.DropTrigger)

        self.camera = False
        self.start = time()

        # Create NeoPixel object with appropriate configuration.
        self.led_status = Adafruit_NeoPixel(1, led_gpio_pin_number, 800000, 5, False, 40, 0, ws.SK6812W_STRIP)
        # Intialize the library (must be called once before other functions).
        self.led_status.begin()

        self.ShowStart()

        try:

            while True:
                sleep(0.25)

        except:

            GPIO.cleanup()

        ## GPIO.wait_for_edge(camera_gpio_pin_number, GPIO.FALLING) == True

        ## GPIO.add_event_detect(trigger_gpio_pin_number, GPIO.RISING, callback=self.DropTrigger())

    # show the camera is being started
    def ShowStart(self):

        try:

            i = 0
            while i < 10:
                # set the camera led off
                self.led_status.setPixelColor(0, Color(0, 0, 0))
                self.led_status.show()
                sleep(0.25)
                # set the camera led to warn
                self.led_status.setPixelColor(0, Color(255, 255, 0))
                self.led_status.show()
                sleep(0.25)
                i += 1

            sleep(5)

            # set the camera led to ready
            self.led_status.setPixelColor(0, Color(0, 255, 0))
            self.led_status.show()

            return True

        except:

            return False

    # display error
    def ShowError(self, gpio_pin_number):
        try:

            i = 0
            while i < 3:
                # set the led red
                self.led_status.setPixelColor(0, Color(255, 0, 0))
                self.led_status.show()
                sleep(0.05)
                # set the led off
                self.led_status.setPixelColor(0, Color(0, 0, 0))
                self.led_status.show()
                sleep(0.05)
                i += 1

            if self.camera:
                # set the camera led to ready
                self.led_status.setPixelColor(0, Color(0, 0, 255))
                self.led_status.show()

            else:
                # set the camera led to ready
                self.led_status.setPixelColor(0, Color(0, 255, 0))
                self.led_status.show()

            return True

        except:

            return False

    # start the camera process
    def CameraAction(self, gpio_pin_number):

        try:

            if self.camera:
                self.camera = False
                print("stop camera")
                self.StopCamera(gpio_pin_number)

            else:
                self.camera = True
                print("start camera")
                self.camera = self.StartCamera(gpio_pin_number)

            sleep(0.10)
            return True

        except:

            return False

    # start the camera process
    def StartCamera(self, gpio_pin_number):

        # call("/usr/bin/sudo /usr/bin/python3 ./start.py".split(), cwd="/home/scripts/bin", stdout=PIPE)

        try:

            if time()-self.start > 10:

                i = 0
                while i < 3:
                    # set the camera led to warn
                    self.led_status.setPixelColor(0, Color(255, 255, 0))
                    self.led_status.show()
                    sleep(0.25)
                    # set the camera led off
                    self.led_status.setPixelColor(0, Color(0, 0, 0))
                    self.led_status.show()
                    sleep(0.25)
                    i += 1

                # set the camera led to ready
                self.led_status.setPixelColor(0, Color(0, 0, 255))
                self.led_status.show()

                # call("/usr/bin/sudo /usr/bin/python3 ./start.py", cwd="/home/scripts/bin")
                command = "sudo python3 ./start.py"
                Popen(command.split(), stdout=DEVNULL, cwd="/home/pi/scripts")

                sleep(0.25)

                print("camera started")

                return True

            else:

                print("failed to start camera time limit")
                self.camera = False
                self.ShowError(gpio_pin_number)


        except OSError:

            print("failed to start camera")
            self.camera = False
            self.ShowError(gpio_pin_number)

            return False

    # stop the camera process
    def StopCamera(self, gpio_pin_number):

        try:

            i = 0
            while i < 3:
                # set the camera led to warn
                self.led_status.setPixelColor(0, Color(255, 255, 0))
                self.led_status.show()
                sleep(0.25)
                # set the camera led off
                self.led_status.setPixelColor(0, Color(0, 0, 0))
                self.led_status.show()
                sleep(0.25)
                i += 1

            command = "/usr/bin/sudo /bin/touch /ram/tmp/stop.proc"
            process = Popen(command.split(), stdout=DEVNULL)

            sleep(0.25)

            print("camera stopped")

            return True

        except:

            print("failed to stop camera")
            self.ShowError(gpio_pin_number)

            return False

    # drop a trigger file
    def DropTrigger(self, gpio_pin_number):

        try:

            if self.camera and time()-self.start > 10:

                command = "/usr/bin/sudo /bin/touch /ram/tmp/trigger.proc"
                process = Popen(command.split(), stdout=DEVNULL)

                print("dropped trigger")

            else:

                print("failed to drop trigger")
                self.ShowError(gpio_pin_number)

            return True

        except:

            print("failed to drop trigger")
            self.ShowError(gpio_pin_number)

            return False

    # shutdown the camera
    def Shutdown(self, gpio_pin_number):

        try:

            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])

            if uptime_seconds > 180 and time()-self.start > 10:

                if not self.camera:
                    print("about to shutdown")
                    command = "/usr/bin/sudo /sbin/shutdown -h now"
                    Popen(command.split(), stdout=DEVNULL)

                    while True:
                        # set the camera led to we are shutting down
                        self.led_status.setPixelColor(0, Color(255, 0, 0))
                        self.led_status.show()
                        sleep(0.05)
                        # set the camera led off
                        self.led_status.setPixelColor(0, Color(0, 0, 0))
                        self.led_status.show()
                        sleep(0.05)

                else:

                    print("failed camera still running")
                    self.ShowError(gpio_pin_number)

            else:

                print("shutdown invalid time limit")
                self.ShowError(gpio_pin_number)


        except OSError:

            print("failed to shutdown")
            self.ShowError(gpio_pin_number)

            return False

# Lets kick off the process
BootCamera()
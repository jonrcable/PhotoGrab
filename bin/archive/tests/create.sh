#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M%s%N")

raspistill -r -o /home/pi/scripts/stills/$DATE.jpg

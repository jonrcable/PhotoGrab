## Python PhotoGrab Micro Controller Environment

This is the installation and setup file for the Photograbber process script

sudo apt-get install libyaml-dev

## Installation
- Python 3.2+
- install pip package manager
    wget https://bootstrap.pypa.io/get-pip.py
    sudo -H ./get-pip.py
    
- install the following pythong libs
    sudo -H pip3.5 install pyserial sqlite3 re configparser

## Example Output (pretty)
| starting, autotigger - True |

| connection(s) successful, waiting on 5 trigger(s) |

| start - 2016-09-05 23:46:11.533418 | stop - 2016-09-05 23:46:12.038074 | elapsed - 0.504656470002 seconds |

| start - 2016-09-05 23:46:12.039625 | stop - 2016-09-05 23:46:12.543429 | elapsed - 0.503804369000 seconds |

| start - 2016-09-05 23:46:12.545330 | stop - 2016-09-05 23:46:13.050546 | elapsed - 0.505215527999 seconds |

| start - 2016-09-05 23:46:13.052316 | stop - 2016-09-05 23:46:13.556251 | elapsed - 0.503934861998 seconds |

| start - 2016-09-05 23:46:13.558345 | stop - 2016-09-05 23:46:14.062578 | elapsed - 0.504232635998 seconds |

| processing, segmenting imu file to sql blob |

| closing,  5 / 5 success |

  Trigger  Start                         Byte  Stop                          Byte         Runtime    Segment (size)    BLOB (size)
---------  --------------------------  ------  --------------------------  ------  --------------  ----------------  -------------
        1  2016-09-05 23:46:11.533418     129  2016-09-05 23:46:12.038074     609  0.504656470002               480            480
        2  2016-09-05 23:46:12.039625     609  2016-09-05 23:46:12.543429    1089  0.503804369000               480            480
        3  2016-09-05 23:46:12.545330    1089  2016-09-05 23:46:13.050546    1569  0.505215527999               480            480
        4  2016-09-05 23:46:13.052316    1569  2016-09-05 23:46:13.556251    2081  0.503934861998               512            512
        5  2016-09-05 23:46:13.558345    2081  2016-09-05 23:46:14.062578    2561  0.504232635998               480            480

| archive saved,  /Users/Jon/Development/Code/Apps/CameraIMU/archives/20160905234611533418 |    

## Example Output (detail)
| starting, autotigger - True |

start looking for  /Users/Jon/Development/Code/Apps/CameraIMU/tmp/trigger.proc

process start  0  will run  1000  or  5  triggers

 run all of our prechecks 
 
 removed a stale database file 
 
 removed a stale imu file 
 
 created a new triggers table 
 
 new database connection successful 
 
 imu collection started process:  7616
 
 sleep for ( 2 ) seconds, waiting on imu 
 
 new imu connection started 
 
| connection(s) successful, waiting on 5 trigger(s) |

 trigger true  1
 
| start - 2016-09-05 23:48:40.371159 | stop - 2016-09-05 23:48:40.871408 | elapsed - 0.500249443001 seconds |

 inserted new event to table 
 
 trigger true  2
 
| start - 2016-09-05 23:48:40.873702 | stop - 2016-09-05 23:48:41.375297 | elapsed - 0.501595419002 seconds |

 inserted new event to table 
 
 trigger true  3
 
| start - 2016-09-05 23:48:41.377028 | stop - 2016-09-05 23:48:41.877105 | elapsed - 0.500077242999 seconds |

 inserted new event to table 
 
 trigger true  4
 
| start - 2016-09-05 23:48:41.878629 | stop - 2016-09-05 23:48:42.378833 | elapsed - 0.500203910000 seconds |

 inserted new event to table 
 
 trigger true  5
 
| start - 2016-09-05 23:48:42.381182 | stop - 2016-09-05 23:48:42.883997 | elapsed - 0.502814801999 seconds |

 inserted new event to table 
 
 imu data collection stopped:  7616
 
 capture event summary 
 
| processing, segmenting imu file to sql blob |

 updated trigger 1 with imu information 
 
 updated trigger 2 with imu information 
 
 updated trigger 3 with imu information 
 
 updated trigger 4 with imu information 
 
 updated trigger 5 with imu information 
 
 capture event summary 
 
| closing,  5 / 5 success |

 sql connection closed 
 
  Trigger  Start                         Byte  Stop                          Byte         Runtime    Segment (size)    BLOB (size)
---------  --------------------------  ------  --------------------------  ------  --------------  ----------------  -------------
        1  2016-09-05 23:48:40.371159     160  2016-09-05 23:48:40.871408     640  0.500249443001               480            480
        2  2016-09-05 23:48:40.873702     640  2016-09-05 23:48:41.375297    1120  0.501595419002               480            480
        3  2016-09-05 23:48:41.377028    1120  2016-09-05 23:48:41.877105    1600  0.500077242999               480            480
        4  2016-09-05 23:48:41.878629    1600  2016-09-05 23:48:42.378833    2080  0.500203910000               480            480
        5  2016-09-05 23:48:42.381182    2080  2016-09-05 23:48:42.883997    2560  0.502814801999               480            480
 
 created an process directory 
 
| archive saved,  /Users/Jon/Development/Code/Apps/CameraIMU/archives/20160905234840371159 |

 process end  0    
    
# Notes for later
this is exactly what we need!
http://vislab-ccom.unh.edu/~schwehr/rt/python-binary-files.html

Instaling gphoto

requires brew install pkg-config
sudo pip3 install gphoto2
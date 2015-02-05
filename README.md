Climaduino Controller
=====================

The Climaduino Controller is Raspberry Pi-based and interacts with the Arduino-based Climaduino Thermostat to provide a web interface optimized for mobile use. The Web Controller allows parameters on the Thermostat to be tweaked and generates historical graphs of temperature and humidity readings. It also can be used as a programmable thermostat.

The controller communicates with the thermostat over a serial connection provided over USB. There is a USB cable connecting both the Arduino and the Raspberry Pi. The controller leverages the Django web framework and JQuery Mobile to provide a site optimized for mobile.

More information
----------------

See the instructable with all the information here: http://www.instructables.com/id/Introducing-Climaduino-The-Arduino-Based-Thermosta/

Installation steps for new version
----------------------------------
Newest version does not need to run from a Raspberry Pi. It should be able to run on any Unix-like operating system.

Steps for a Raspberry Pi:
- Install raspbian image using NOOBS http://www.raspberrypi.org (http://www.raspberrypi.org/help/noobs-setup/)
- Set proper settings in the configuration screen (raspi-config)
-- Advanced Options > Hostname
-- Advanced Options > Memory Split = 16
- set up networking and possibly WiFi

- Install the following
-- sudo apt-get install -y build-essential python-dev python-setuptools libcairo2-dev libpango1.0-dev libxml2-dev rrdtool librrd-dev mosquitto libnss-mdns screen git

- Clone the code (NOTE: ADDRESS SHOULD BE CHANGED TO MASTER BRANCH WHEN FEATURE COMPLETE)
-- git clone -b feature/mqtt_pubsub_model https://github.com/bbustin/Climaduino-web-controller.git ~/climaduino



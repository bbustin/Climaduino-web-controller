Climaduino Controller
=====================

The Climaduino Controller interacts one or more Arduino Yún-based Climaduino Thermostats using the MQTT protocol. It provides a web interface optimized for mobile use. It can be run on a Raspberry Pi or any machine with a Unix-like OS. The Web Controller allows parameters on the Thermostat to be tweaked and generates historical graphs of temperature and humidity readings. It also can be used as a programmable thermostat.

The controller communicates with the thermostat using the MQTT pub/sub protocol over the network. The controller leverages the Django web framework and JQuery Mobile to provide a site optimized for mobile.

More information
----------------

See the instructable about the previous version is available here: http://www.instructables.com/id/Introducing-Climaduino-The-Arduino-Based-Thermosta/

Installation steps for new version
----------------------------------
Newest version does not need to run from a Raspberry Pi. It should be able to run on any Unix-like operating system.

Steps for a Raspberry Pi:
- Install raspbian image using NOOBS http://www.raspberrypi.org (http://www.raspberrypi.org/help/noobs-setup/)
- Set proper settings in the configuration screen (raspi-config)
-- Advanced Options > Hostname = climaduino (If different, need to update Climaduino sensor's mqtt_bridge.py file)
-- Advanced Options > Memory Split = 16
- set up networking and possibly WiFi

Steps applicable to all:
- Install the following
-- sudo apt-get install -y build-essential python-dev python-setuptools libcairo2-dev libpango1.0-dev libxml2-dev rrdtool librrd-dev mosquitto libnss-mdns screen git

- Install Climaduino controller
-- git clone -b develop https://github.com/bbustin/Climaduino-web-controller.git ~/climaduino #(NOTE: ADDRESS SHOULD BE CHANGED TO MASTER BRANCH WHEN FEATURE COMPLETE)
-- cd ~/climaduino
-- sudo python setup.py develop
-- python manage.py syncdb
-- sudo cp ~/climaduino/startup_script\ for\ Debian/climaduino-controller /etc/init.d
-- sudo update-rc.d climaduino-controller defaults
-- sudo reboot

- To manually start Climaduino controller
-- sudo service climaduino-controller start
-- web interface accessible at http://climaduino.local
-- admin interface at http://climaduino.local/admin

- To stop Climaduino controller
-- sudo service climaduino-controller stop

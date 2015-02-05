#!/bin/bash
echo "========================================================================="
echo "Climaduino"
echo "========================================================================="

echo "-------------------------------------------------------------------------"
echo "Backend daemons"
echo "-------------------------------------------------------------------------"
echo "Starting component: rrdtool_logger"
/usr/bin/screen -d -m -S rrdtool_logger python manage.py rrdtool_logger
echo "Starting component: mqtt_bridge"
/usr/bin/screen -d -m -S mqtt_bridge python manage.py mqtt_bridge
echo "Starting component: programming_sentry"
/usr/bin/screen -d -m -S programming_sentry python manage.py programming_sentry

echo "-------------------------------------------------------------------------"
echo "UI"
echo "-------------------------------------------------------------------------"
echo "Starting Climaduino web user interface listening on port 8080"
/usr/bin/screen -d -m -S web_interface python manage.py runserver 0.0.0.0:8080
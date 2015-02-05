#!/bin/bash
echo "========================================================================="
echo "Climaduino"
echo "========================================================================="

echo "-------------------------------------------------------------------------"
echo "Backend daemons"
echo "-------------------------------------------------------------------------"
echo "Starting component: rrdtool_logger"
/usr/bin/screen -D -m -S rrdtool_logger python manage.py rrdtool_logger
echo "Starting component: mqtt_bridge"
/usr/bin/screen -D -m -S mqtt_bridge python manage.py mqtt_bridge
echo "Starting component: programming_sentry"
/usr/bin/screen -D -m -S programming_sentry python manage.py programming_sentry

echo "-------------------------------------------------------------------------"
echo "UI"
echo "-------------------------------------------------------------------------"
echo "Starting Climaduino web user interface listening on port 80"
/usr/bin/screen -D -m -S web_interface python manage.py runserver 0.0.0.0:80
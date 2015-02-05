#!/bin/bash
echo "========================================================================="
echo "Climaduino"
echo "========================================================================="

echo "-------------------------------------------------------------------------"
echo "UI"
echo "-------------------------------------------------------------------------"
echo "Stopping Climaduino web user interface listening on port 80"
/usr/bin/screen -X -S web_interface quit

echo "-------------------------------------------------------------------------"
echo "Backend daemons"
echo "-------------------------------------------------------------------------"
echo "Stopping component: programming_sentry"
/usr/bin/screen -X -S programming_sentry quit
echo "Stopping component: rrdtool_logger"
/usr/bin/screen -X -S rrdtool_logger quit
echo "Stopping component: mqtt_bridge"
/usr/bin/screen -X -S mqtt_bridge quit


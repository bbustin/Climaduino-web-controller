#!/usr/bin/env bash
echo "Updating apt-get"
apt-get update
echo "Installing any missing pre-requisites from apt-get"
apt-get install -y build-essential python-dev python-setuptools libcairo2-dev libpango1.0-dev libxml2-dev rrdtool librrd-dev
echo "Running 'python setup.py develop'"
python /vagrant/setup.py develop
echo "cd into the /vagrant directory before beginning"
echo ""
echo "If database has not yet been created, then run:"
echo "python manage.py syncdb"
echo ""
echo "If you want to start the server, then run:"
echo "python manage.py runserver 0.0.0.0:8000"

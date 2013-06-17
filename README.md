skypunch
========

Background
----------
Skypunch is a service monitoring system which allows monitoring of cloud services for their availability and uptime. Skypunch can be configured to monitor any REST service and inform a user to the availability, or lack of, based on configurable notification parameters.  Skypunch supports the ability to access a REST service using various HTTP authentication methods including the usage of Openstack Keystone authentication tokens.


Instructions
============
1) Getting code
git clone https://github.com/pemellquist/skypunch.git <your directory>



sudo apt-get install python-pip python-dev build-essential
sudo pip install python-daemon
sudo apt-get install mysql-server
sudo pip install SQLAlchemy
sudo pip install mysql-connector-python
tail -f skypunch.log | ccze -A


Error cases:
Unable to connect to target
Wrong response from target
invalid authn params for BASIC
involve authn param for Keystone
Keystone authn failure


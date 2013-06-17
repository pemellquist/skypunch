skypunch
========

Background
----------
Skypunch is a service monitoring system which allows monitoring of cloud services for their availability and uptime. Skypunch can be configured to monitor any REST service and inform a user to the availability, or lack of, based on configurable notification parameters.  Skypunch supports the ability to access a REST service using various HTTP authentication methods including the usage of Openstack Keystone authentication tokens.

Design
------
Skypunch runs a system daemon using an SQL database for the definition of 'targets' to be monitored. Each target defined will be monitored at the defined REST URL and method at the defined frequency. As each target is monitored, skypunch will 1: log the result details to a log file 2: update the SQL database with the results and 3: inform a configurable user on the occurrence of an error or recovery.

Skypunch is made up of the following main areas.
    1) Python based monitoring code.
    2) MySQL datbase for defined 'targets' and 'notifiers'.
    3) Configuration file for main runtime configuration.
    4) Log file for run time information of each monitoring request.
    5) Simple Command Line Interface (CLI) for interacting with.



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


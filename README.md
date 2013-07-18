Skypunch  - Cloud Service Monitoring System
========

Introduction
----------
Skypunch is a cloud service monitoring solution which allows for the monitoring of cloud services for their availability and performance. Skypunch can be configured to monitor any cloud service, public or private, and inform you regardning the availability, or lack of, based on configurable parameters.  Skypunch supports the ability to access any service using various HTTP(S) authentication methods including **built in support for Openstack Cloud Services**.


Monitoring all your services
----------
Skypunch is a system service using an SQL database for the definition of 'targets' to be monitored. Each target defined will be monitored at the defined URL and frequency. As each target is monitored, skypunch will log the result details to a log file,update the SQL database with the results and inform a configurable user on the occurrence of an error or recovery.

Main Features
-------------
**Background monitoring of an unlimited number of services**<br>
Skypunch runs as a system daemon which monitors as many cloud services you like. The services can be any service including public and private cloud services which can be hosted within any cloud.

**Built in Openstack Smarts**<br>
Skypunch has built in support for services which require Openstack Keystone tokens. Skypunch will automatically retrieve an Openstack Keystone token and use it with the target request.<br>

**Detailed Failure Tracing**<br>
When a service fails the monitoring test, skypunch provides a detailed trace of what worked and what failed. The intent is to assist the operator with actionable information rather than just say it does not work!<br>

**Flexible Service Configuration**<br>
Skypunch allows a target to be defined in a flexible manner including which protocol it supports, the specific HTTP method to be used, the response required and which authentication scheme should be used. Together, these allow for the monitoring of a wide range of services.<br>

**100% Python based**<br>
Skypunch is implemented in Python and uses a number of Python libraries including sqlalchemy for mysql access.<br>

**MySQL database for defined 'targets' and 'notifiers'**<br>
SQL tables for targets to be monitored and users to be notified are defined within the mysql database. In addition, the tables model various statistics for each monitored target.<br>

**Configuration file for main runtime configuration**<br>
A configuration file allows for global run time settings.<br>

**Log file for run time information**<br>
A log file captures all request details.<br>


**Simple Command Line Interface (CLI)**<br>
A CLI allows interfacing with the skypunch daemon to list targets, notifiers and their current state<br> 

The Skypunch Data Model
-----------------
At the core of skypunch are the database tables which the skypunch daeamon uses to monitor targets and inform users. 
The details for these tables can be found in [skypunch.sql](https://github.com/pemellquist/skypunch/blob/master/sql/skypunch.sql) <br><br>

**Targets Table** <br>
The targets table models each service to be monitored and collects performance statistics over time.
* URL of system to be monitored (HTTP or HTTPS)
* HTTP Method to use (GET,PUT,POST,DELETE,HEAD)
* The type of HTTP authentication to use (NONE, BASIC, OPENSTACK)
* The frequency of monitoring  (as frequent as once a second)
* A timeout to fail on 
* The expected result for 'success' (HTTP status code e.g. 200)
* The last status (PASS, FAIL)
* Timestamp of last request 
* A detailed description of a failure (if present)
* Statistics on success and failures (counters)
* Is the target enabled to be used?

**Notifiers Table** <br>
The notifiers table models who should be notified upon key skypunch events (failure or success).
* The type of notification (SMTP currently is only supported)
* Notification specific parameters (e.g. email address and parameters) 


Installing Skypunch 
--------------------

In order to run skypunch, you will need to install the code and prerequisite libraries.
The following instructions define how to install everything on a single system. These instructions can be modified as needed for other setups. These instructions assume a linux Ubuntu system but can be changed to run on other operating systems. 

Note! The current installation is a manual process. The plan is make this a debian package using a python package install. For now, the steps below are required.

**1 - Install and setup mysql**<br>
Note! the default [skypunch.config](https://github.com/pemellquist/skypunch/blob/master/skypunch.config ) file defines the mysql connection parameters 
including user, password and mysql server address. The default assumes root:root and localhost, change as needed. <br>

    $sudo apt-get install mysql-server
    
**2 - Install Python**<br>
The current code has been tested on Python 2.7.3.<br>
    
    $sudo apt-get install python

**3 - Install skypunch from github**<br>
The current packaging is full source code.<br>
    
    $git clone https://github.com/pemellquist/skypunch.git <your_skypunch_directory>

**4 - Install dependent libraries**<br>
    
    $sudo apt-get install python-pip python-dev build-essential
    
    $sudo pip install python-daemon
    
    $sudo pip install SQLAlchemy
    
    $sudo pip install mysql-connector-python


**5 - Load skypunch SQL schema into mySQL**<br>

Loading the skypunch schema into mysql will allow defining targets and notifiers.<br>
    
    $mysql -u youruser -p < <your_skypunch_directory>/sql/skpunch.sql

After doing this step you may also go into mysql and poke around. You should be able to see the
skypunch database and two tables ( use skypunch; describe targets; describe notifiers; )


**6 - Define targets and notifiers**<br>

Targets and notifiers can be defined in a config file and loaded into the
database. You can also edit the mysql database directly as needed. 
An example target and notifier definition file is provided, [data.sql](https://github.com/pemellquist/skypunch/blob/master/sql/data.sql), and can be changed as needed. Add all the targets and notifiers needed in your own copy of this file.
    
    $mysql -u youruser -p < <your_skypunch_directory>/sql/data.sql


Running Skypunch
----------------
Once skypunch is installed a CLI allows controlling the skypunch daemon and querying the database for targets, notifiers. The CLI also allows testing targets manually and enabling or disabling targets.


**1 - Skypunch CLI options**<br>

    $python skypunch/skypunch.py
    version: 0.3.0
    usage: skypunch start | stop  | targets [id] [enable | disable | test] | notifiers [id] [enable | disable]

**2 - Starting skypunch**<br>

    $python your_skypunch_directory/skypunch.py start
    started with pid 8100
    starting skypunch ....
    
Starting skypunch will kick of a daemon process running which will read in [skypunch.config](https://github.com/pemellquist/skypunch/blob/master/skypunch.config ) and start the monitoring based on targets and notifiers defined in the mysql database.
Tailing out skypunch.log is an easy way to see that it is running properly.

    $tail -f skypunch.log
    ..
    2013-07-11 06:10:57,053 INFO [1] HP Cloud Dot COM               GET https://www.hpcloud.com PASS (OK)
    ..
    
**3 - Stopping skypunch**<br>

    $python your_skypunch_directory/skypunch.py stop
    shutting down skypunch ...
    

**4 - List currently loaded targets**<br>
You can list out all currently loaded targets in the database used by skypunch with a summary status using the 'targets' option.

    $python your_skypunch_directory/skypunch.py targets

    +----+------------------------------+--------+---------------------+---------+------------+------------+
    | ID | Name                         | Status | LastUpdated         | Enabled | Pass Count | Fail Count |
    +----+------------------------------+--------+---------------------+---------+------------+------------+
    | 1  | Google Dot COM               | PASS   | 2013-07-11 06:17:54 | Yes     | 12996      | 0          |
    | 2  | Openstack Block Storage      | PASS   | 2013-07-11 06:17:49 | Yes     | 12984      | 2          |
    | 3  | Openstack CDN Region         | PASS   | 2013-07-11 06:17:50 | Yes     | 12972      | 1          |
    | 4  | Openstack Compute Region A   | PASS   | 2013-07-11 06:17:51 | Yes     | 12970      | 2          |
    | 5  | Openstack Compute Region B   | PASS   | 2013-07-11 06:17:51 | Yes     | 12965      | 4          |
    | 6  | Openstack Compute Region C   | PASS   | 2013-07-11 06:17:52 | Yes     | 12969      | 0          |
    | 7  | Openstack Object Storage     | PASS   | 2013-07-11 06:17:53 | Yes     | 12959      | 1          |
    | 8  | Localhost nginx test         | PASS   | 2013-07-11 06:17:53 | Yes     | 11864      | 1103       |
    +----+------------------------------+--------+---------------------+---------+------------+------------+

This summary view shows all the targets with the status of the last monitor, if the target is enabled, and pass / fail counts.

**5 - List details about a specific target**<br>
Using the target Id, you can query for complete details for any defined target.

    $python skypunch/skypunch.py targets 1

    +---------------------+-------------------------+
    | ID                  | 1                       |
    +---------------------+-------------------------+
    | Name                | Google Dot COM          |
    +---------------------+-------------------------+
    | Status              | PASS                    |
    +---------------------+-------------------------+
    | Enabled             | Yes                     |
    +---------------------+-------------------------+
    | Status Description  | OK                      |
    +---------------------+-------------------------+
    | Last Updated        | 2013-07-11 06:28:39     |
    +---------------------+-------------------------+
    | Target URL          | https://www.google.com  |
    +---------------------+-------------------------+
    | Target Method       | GET                     |
    +---------------------+-------------------------+
    | Authentication      | NONE                    |
    +---------------------+-------------------------+
    | Expected Value      | 200                     |
    +---------------------+-------------------------+
    | Frequency (sec)     | 10                      |
    +---------------------+-------------------------+
    | Timeout (sec)       | 10                      |
    +---------------------+-------------------------+
    | Pass Count          | 13048                   |
    +---------------------+-------------------------+
    | Fail Count          | 0                       |
    +---------------------+-------------------------+
    | 200 Status Count    | 13048                   |
    +---------------------+-------------------------+
    | 300 Status Count    | 0                       |
    +---------------------+-------------------------+
    | 400 Status Count    | 0                       |
    +---------------------+-------------------------+
    | 500 Status Count    | 0                       |
    +---------------------+-------------------------+
    | Network Fail Count  | 0                       |
    +---------------------+-------------------------+
    | Repeated Fail Count | 0                       |
    +---------------------+-------------------------+

 
**6 - Enable or disable a target**<br>
There may be times when you would like to disable the monitoring of a target but leave it within the database to be enabled in the future.
The disable option will stop the skypunch daemon from making subsequent monitor calls to this target.

    $python skypunch/skypunch.py
    version: 0.3.0
    usage: skypunch start | stop  | targets [id] [enable | disable | test] | notifiers [id] [enable | disable]
    
    $python skypunch/skypunch.py targets 8 disable
    Target: Localhost nginx test has been Disabled
    
    $python skypunch/skypunch.py targets 8 enable
    Target: Localhost nginx test has been Enabled


**7 - Test a target right now in manual mode**<br>
The CLI allows testing an existing target independent from the background monitoring and showing the results within stdout. This may prove useful when trying to diagnose an issue on the fly. The 'test' option will test the specified target and display all details of the test.


    $ python skypunch/skypunch.py targets 8 test
    [8] Localhost nginx test           GET http://localhost PASS (OK)
    2013-07-13 04:44:25.113623 Connecting to http://localhost ....
    2013-07-13 04:44:25.118338 Connection    [OK]
    2013-07-13 04:44:25.118354 Sending target request string ...
    2013-07-13 04:44:25.118388 Sent [OK]
    2013-07-13 04:44:25.118591 Sending GET request  [OK]
    2013-07-13 04:44:25.119201 Reading response [OK]
    2013-07-13 04:44:25.119219 Response [OK]


**8 - List details about all Notifiers**<br>
The CLI allows listing all currently loaded notifiers.

    $ python skypunch/skypunch.py notifiers
    +----+--------------+---------+------+-------------------------+
    | ID | Name         | Enabled | Type | Address                 |
    +----+--------------+---------+------+-------------------------+
    | 1  | Operations   | Yes     | SMTP | openstack-ops@gmail.com |
    +----+--------------+---------+------+-------------------------+

**9 - List details about a specific notifier**<br>
The CLI allows listing details about a specific notifier including pass and fail counts.

    $ python skypunch/skypunch.py notifiers 1
    +------------+-------------------------+
    | ID         | 1                       |
    +------------+-------------------------+
    | Name       | Operations              |
    +------------+-------------------------+
    | Enabled    | Yes                     |
    +------------+-------------------------+
    | Type       | SMTP                    |
    +------------+-------------------------+
    | Address    | openstack-ops@gmail.com |
    +------------+-------------------------+
    | Pass Count | 257                     |
    +------------+-------------------------+
    | Fail Count | 27                      |
    +------------+-------------------------+



Defining Targets to be Monitored
--------------------------------
Defining a target to be monitored requires the insertion of a row into the 'targets' database. The database schema can
be found in  [skypunch.sql](https://github.com/pemellquist/skypunch/blob/master/sql/skypunch.sql)<br>

**Simple Service Monitoring**<br>
Simple example to monitor www.google.com. Google always stays up so this is a good example of a service which will either always return a 200 or report a network issue if the network cannot access Google.

    # create a google.com target
    # checks http://www.google.com for GET and requires a 200 status
    # no authentication used
    # called every 10 seconds, timeout is 10 seconds, enabled
    USE skypunch;

    INSERT INTO targets
    VALUES (0,'Google home page','0','NEW',NULL,'NEW','','http://www.google.com','GET','NONE','',200,10,10,0,0,0,0,0,0,0,0,1);


**Service with BASIC authn**<br>
In this example, an nginx HTTP server has been installed on the local system. Definition of a target for 'nginx test server' allows taking it down and seeing the target status change to status = 'FAIL' and triggering email notifications. Setting up basic HTTP authentication requi
res the Skypunch target to use authn = 'BASIC'. This requires setting the authn parameters for the user and password.

    # create a localhost target for monitoring a http server with basic authentication
    INSERT INTO targets
    VALUES (0,'nginx with basic authn','0','NEW',NULL,'','NEW','http://localhost','GET','BASIC','user=freebeer,password=forall',200,10,10,0,0,0,0,0,0,0,0,1);

**Openstack service with Keystone authn**<br>
In this example, an openstack service exists which requires usage of an Openstack Keystone token. The Keystone endpoint
and keystone credentials are required to be specified. Skypunch will automatically log into the Keystone Auth service, get a token
 and use it against the specified service endpoint.

    # create an Openstack target
    INSERT INTO targets
    VALUES (0,'Openstack Service','0','NEW',NULL,'','NEW','https://openstack.service.url','GET','OPENSTACK','user=xxxx,password=yyyyy,osauthendpoint=OPENSTACK_KEYSTONE_ENDPOINT,tenantid=ZZZZZZZZZZ',200,10,10,0,0,0,0,0,0,0,0,1);
 
 





Testing and Error Cases Covered
--------------------------------
1. Unable to connect to target
<p>In the event the skypunch daemon cannot reach the target and connect, a network error will be generated and target will be put in FAIL status. All notifiers will be informed.
2. Wrong response from target
<p>The target is required to respond with the same response code in the target definition ( e.g. a target with a 200 respond should respond with a 200 for success). If the response does not match, the target status will be FAIL and all notifiers will be informed.
3. Invalid authn params for BASIC
<p>When defining the authn type as BASIC the target definition must have a 'user' and 'password' defined. Failing to do so will result in an error.
4. Invalid authn param for OPENSTACK
<p>When defining the authn type as OPENSTACK the target definition must have the 'user', 'password','osauthendpoint' and 'tenantid' parameters defined. Failing to do so will result in an error.   
5. Invalid Openstack Keystone authn failure
<p>If the Openstack Keystone parameters are defined but the Keystone endpoint fails to allow access this error will be generated.



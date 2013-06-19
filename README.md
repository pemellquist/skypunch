Skypunch
========

Background
----------
Skypunch is a service monitoring system which allows monitoring of cloud services for their availability and uptime. Skypunch can be configured to monitor any REST service and inform a user to the availability, or lack of, based on configurable notification parameters.  Skypunch supports the ability to access a REST service using various HTTP authentication methods including the usage of Openstack Keystone authentication tokens.

Design
------
Skypunch runs as a system daemon using an SQL database for the definition of 'targets' to be monitored. Each target defined will be monitored at the defined REST URL and method at the defined frequency. As each target is monitored, skypunch will log the result details to a log file ,update the SQL database with the results and inform a configurable user on the occurrence of an error or recovery.

Skypunch is comprised of the following main areas:<br><br>
**Python based monitoring code**<br>
Skypunch is implemented in Python and uses a number of Python libraries including sqlalchemy for mysql access.<br>

**MySQL database for defined 'targets' and 'notifiers'**<br>
SQL table schemas for the definition of targets to be monitored and users to be notified are defined in a mysql database.
The most recent monitored status is also updated to the target database for each target.<br>

**Configuration file for main runtime configuration**<br>
A config file allows for global run time settings.<br>

**Log file for run time information**<br>
A log file captures all monitored call details.<br>

**Built in support for Openstack Keystone authentication**<br>
Skypunch can monitor any HTTP REST service including Openstack services which require Openstack Keystone tokens<br>

**Simple Command Line Interface (CLI)**<br>
A CLI allows inspecting the current status of each monitored target.<br>

Skypunch Database
-----------------
At the core of skypunch are the database tables which the skypunch daeamon uses to monitor targets and inform notifiers. 
The details for these tables can be found in *skypunch.sql* <br><br>

**targets Table** <br>
Each row in the table defines details of how to monitor each target including:
* URL of system to be monitored 
* HTTP Method to use
* The type of HTTP authentication to use ( NONE, BASIC, OPENSTACK )
* The frequency of monitoring  ( as frequent as once a second )
* A timeout to fail on 
* The expected result for 'success'
    
Each row in the table also defines results for monitoring of each target
1. The last last status (PASS, FAIL)
2. Timestamp of last monitor
3. A detailed description of a failure
4. statistics on success and failures

**notifiers Table** <br>
Each row within the notifier table defines someone, or system, to be notified upon a failure or success.
1. The type of notification ( SMTP, Tweet, etc )
2. Notification specific parameters ( email address and parameters) 


Installing and Running Skypunch
-------------------------------

In order to run skypunch, you will need to install the code and prerequisite libraries.
 The following instructions define how to run everything on a single system including mysql on the same system. These instructions can be modified as needed for other setups. These instructions assume a linux Ubuntu system but can be changed to run on other systems. The real prerequisites are Python and MySQL.

    1. Install and setup mysql
    Note! the default skypunch.config file defines the mysql connection parameters 
    including user & password ( default is root:root ).

    $sudo apt-get install mysql-server
    
    2. Install Python 
    The current code has been tested on Python 2.7.3.
    
    $sudo apt-get install python    

    3. Install skypunch from github
    The current packaging is full source code.
    
    $git clone https://github.com/pemellquist/skypunch.git your_skypunch_directory

    4. Install dependent libraries
    
    $sudo apt-get install python-pip python-dev build-essential
    
    $sudo pip install python-daemon
    
    $sudo apt-get install mysql-server
    
    $sudo pip install SQLAlchemy
    
    $sudo pip install mysql-connector-python

    5. Load skypunch SQL schema into mySQL
    Loading the skypunch schema into mysql will allow defining targets and notifiers.
    
    $mysql -u youruser -p < your_skypunch_directory/sql/skpunch.sql 

    6. Define targets and notifiers
    Targets and notifiers can be defined in a provided config file and loaded into the
    database. An example file is provided and can be changed as needed.
    
    $mysql -u youruser -p < your_skypunch_directory/sql/data.sql

    7. Run, verify and test
    Run skypunch and verify that things are working by using the CLI to list out targets.
    Look at the log file to see how the monitoring is working. Try some tests to see if
    the email notifier is working.

    list skypunch options
    $ python your_skypunch_directory/skypunch.py
    usage: skypunch start | stop | list

    start skypunch
    $python your_skypunch_directory/skypunch.py start
    started with pid 8100
    starting skypunch ....

    list currently loaded targets
    $python your_skypunch_directory/skypunch.py list 
    +----+----------------------------+--------+---------------------+
    | ID | Name                       | Status | LastUpdated         |
    +----+----------------------------+--------+---------------------+
    | 1  | Google home page           | PASS   | 2013-06-17 23:06:13 |
    | 2  | HP home page               | PASS   | 2013-06-17 23:06:13 |
    | 3  | GitHub LBaaS               | PASS   | 2013-06-17 23:06:13 |
    | 4  | GitHub LBaaS (bad)         | FAIL   | 2013-06-17 23:06:12 |
    | 5  | GitHub LBaaS (basic authn) | PASS   | 2013-06-17 23:06:12 |
    | 6  | HPCS LBaaS Service         | PASS   | 2013-06-17 23:06:13 |
    | 7  | Localhost nginx test       | FAIL   | 2013-06-17 23:06:13 |
    +----+----------------------------+--------+---------------------+

    list details about a specific target
    $python skypunch/skypunch.py list 1
    +---------------------+-----------------------+
    | ID                  | 1                     |
    +---------------------+-----------------------+
    | Name                | Google home page      |
    +---------------------+-----------------------+
    | Status              | PASS                  |
    +---------------------+-----------------------+
    | Status Description  | OK                    |
    +---------------------+-----------------------+
    | Last Updated        | 2013-06-17 23:06:55   |
    +---------------------+-----------------------+
    | Target URL          | http://www.google.com |
    +---------------------+-----------------------+
    | Target Method       | GET                   |
    +---------------------+-----------------------+
    | Authentication      | NONE                  |
    +---------------------+-----------------------+
    | Expected Value      | 200                   |
    +---------------------+-----------------------+
    | Frequency (sec)     | 10                    |
    +---------------------+-----------------------+
    | Timeout (sec)       | 10                    |
    +---------------------+-----------------------+
    | Pass Count          | 7900                  |
    +---------------------+-----------------------+
    | Fail Count          | 0                     |
    +---------------------+-----------------------+
    | 200 Status Count    | 7900                  |
    +---------------------+-----------------------+
    | 300 Status Count    | 0                     |
    +---------------------+-----------------------+
    | 400 Status Count    | 0                     |
    +---------------------+-----------------------+
    | 500 Status Count    | 0                     |
    +---------------------+-----------------------+
    | Network Fail Count  | 0                     |
    +---------------------+-----------------------+
    | Repeated Fail Count | 0                     |
    +---------------------+-----------------------+
 
    tailing the log file shows current monitoring
    tail -f skypunch.log
    2013-06-18 04:07:52,071 ERROR [4] GitHub LBaaS (bad)             GET https://www.ggithub.com/LBaaS FAIL (network error to target)
    2013-06-18 04:07:52,432 INFO  [5] GitHub LBaaS (basic authn)     GET https://github.com/LBaaS PASS (OK)
    2013-06-18 04:07:52,546 INFO  [6] HPCS LBaaS Service             GET https://region-a.geo-1.lbaas.hpcloudsvc.com/v1.1 PASS (OK)
    2013-06-18 04:07:52,564 INFO  [7] Localhost nginx test           GET http://localhost PASS (OK)
    2013-06-18 04:07:52,903 INFO  [1] Google home page               GET http://www.google.com PASS (OK)
    2013-06-18 04:07:53,064 INFO  [2] HP home page                   GET http://www.hp.com PASS (OK)
    2013-06-18 04:07:53,413 INFO  [3] GitHub LBaaS                   GET https://github.com/LBaaS PASS (OK)


Defining Targets to be Monitored
--------------------------------



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



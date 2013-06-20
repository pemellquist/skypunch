Skypunch
========

Background
----------
Skypunch is a service monitoring service which allows for the monitoring of cloud services for their availability and uptime. Skypunch can be configured to monitor any REST service and inform a user to the availability, or lack of, based on configurable notification parameters.  Skypunch supports the ability to access any REST service using various HTTP(S) authentication methods including the usage of Openstack Keystone authentication tokens.


Design
------
Skypunch runs as a system daemon using an SQL database for the definition of 'targets' to be monitored. Each target defined will be monitored at the defined REST URL and frequency. As each target is monitored, skypunch will log the result details to a log file ,update the SQL database with the results and inform a configurable user on the occurrence of an error or recovery.

Skypunch is comprised of the following main:<br><br>
**Python based monitoring code**<br>
Skypunch is implemented in Python and uses a number of Python libraries including sqlalchemy for mysql access.<br>

**MySQL database for defined 'targets' and 'notifiers'**<br>
SQL tables for targets to be monitored and users to be notified are defined within the mysql database.
The most recent monitored status and empirical statistics are updated with each target request.<br>

**Configuration file for main runtime configuration**<br>
A configuration file allows for global run time settings.<br>

**Log file for run time information**<br>
A log file captures all request details.<br>

**Built in support for Openstack Keystone authentication**<br>
Skypunch can monitor any HTTP(S) REST service including Openstack services which require Openstack Keystone tokens.
Skypunch will automatically retrieve an Openstack Keystone token and use it with the target request.<br>

**Simple Command Line Interface (CLI)**<br>
A CLI allows interfacing with the skypunch daemon to list targets, notifiers and their current state<br> 

Skypunch Database
-----------------
At the core of skypunch are the database tables which the skypunch daeamon uses to monitor targets and inform users. 
The details for these tables can be found in *skypunch.sql* <br><br>

**targets Table** <br>
Each row in the table defines details of how to monitor each target including:
* URL of system to be monitored (HTTP or HTTPS)
* HTTP Method to use (GET,PUT,POST,DELETE,HEAD)
* The type of HTTP authentication to use (NONE, BASIC, OPENSTACK)
* The frequency of monitoring  (as frequent as once a second)
* A timeout to fail on 
* The expected result for 'success' (HTTP status code e.g. 200)
    
Each row in the table also defines results for each target
* The last status (PASS, FAIL)
* Timestamp of last request 
* A detailed description of a failure (if present)
* Statistics on success and failures (counters)

**notifiers Table** <br>
Each row within the notifier table defines someone to be notified upon a failure or success.
* The type of notification (SMTP, Tweet, RSS)
* Notification specific parameters (e.g. email address and parameters) 


Installing Skypunch (for dev and ops)
-------------------------------

In order to run skypunch, you will need to install the code and prerequisite libraries.
The following instructions define how to install everything on a single system. These instructions can be modified as needed for other setups. These instructions assume a linux Ubuntu system but can be changed to run on other operating systems. 

**1 - Install and setup mysql**<br>
Note! the default skypunch.config file defines the mysql connection parameters 
including user, password and mysql server address. The default assumes root:root and localhost, change as needed. <br>

*$sudo apt-get install mysql-server*
    
**2 - Install Python**<br>
The current code has been tested on Python 2.7.3.<br>
    
*$sudo apt-get install python*    

**3 - Install skypunch from github**<br>
The current packaging is full source code.<br>
    
*$git clone https://github.com/pemellquist/skypunch.git your_skypunch_directory*

**4 - Install dependent libraries**<br>
    
*$sudo apt-get install python-pip python-dev build-essential*<br>
    
*$sudo pip install python-daemon*<br>
    
*$sudo apt-get install mysql-server*<br>
    
*$sudo pip install SQLAlchemy*<br>
    
*$sudo pip install mysql-connector-python*<br>


**5 - Load skypunch SQL schema into mySQL**<br>

Loading the skypunch schema into mysql will allow defining targets and notifiers.<br>
    
*$mysql -u youruser -p < your_skypunch_directory/sql/skpunch.sql* <br>

After doing this step you may also go into mysql and poke around. You should be able to see the
skypunch database and two tables ( use skypunch; describe targets; describe notifiers; )


**6 - Define targets and notifiers**<br>

Targets and notifiers can be defined in a provided config file and loaded into the
database. An example file is provided, *data.sql*, and can be changed as needed.
    
*$mysql -u youruser -p < your_skypunch_directory/sql/data.sql*


Running Skypunch
----------------


**1 - list skypunch options**<br>

*$python your_skypunch_directory/skypunch.py*<br>
usage: skypunch start | stop | list<br>

**2 - start skypunch**<br>

*$python your_skypunch_directory/skypunch.py start*
started with pid 8100<br>
starting skypunch ....<br>

**3 - list currently loaded targets**<br>

*$python your_skypunch_directory/skypunch.py list*

    +----+----------------------------+--------+---------------------+
    | ID | Name                       | Status | LastUpdated         |
    +----+----------------------------+--------+---------------------+
    | 1  | Google home page           | PASS   | 2013-06-17 23:06:13 |
    | 2  | HP home page               | PASS   | 2013-06-17 23:06:13 |
    | 3  | GitHub Skypunch            | PASS   | 2013-06-17 23:06:13 |
    | 4  | GitHub Skypunch (bad)      | FAIL   | 2013-06-17 23:06:12 |
    | 6  | Localhost nginx test       | PASS   | 2013-06-17 23:06:13 |
    +----+----------------------------+--------+---------------------+

**4 - list details about a specific target**<br>

*$python skypunch/skypunch.py list 1*

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
 
**5 - tailing the log file shows current monitoring**<br>

*$tail -f skypunch.log*

    2013-06-18 04:07:52,071 ERROR [4] GitHub LBaaS (bad)             GET https://www.ggithub.com/LBaaS FAIL (network error to target)
    2013-06-18 04:07:52,432 INFO  [5] GitHub LBaaS (basic authn)     GET https://github.com/LBaaS PASS (OK)
    2013-06-18 04:07:52,546 INFO  [6] HPCS LBaaS Service             GET https://region-a.geo-1.lbaas.hpcloudsvc.com/v1.1 PASS (OK)
    2013-06-18 04:07:52,564 INFO  [7] Localhost nginx test           GET http://localhost PASS (OK)
    2013-06-18 04:07:52,903 INFO  [1] Google home page               GET http://www.google.com PASS (OK)
    2013-06-18 04:07:53,064 INFO  [2] HP home page                   GET http://www.hp.com PASS (OK)
    2013-06-18 04:07:53,413 INFO  [3] GitHub LBaaS                   GET https://github.com/LBaaS PASS (OK)


Defining Targets to be Monitored
--------------------------------
Defining a target to be monitored requires the insertion of a row into the 'targets' database.<br>

Simple example to monitor www.google.com. Google always stays up so this is a good example of a service which will either always return a 200 or report a network issue if the network cannot access Google.

    # create a google.com target
    # checks http://www.google.com for GET and requires a 200 status
    # no authentication used
    # called every 10 seconds, timeout is 10 seconds, enabled
    USE skypunch;

    INSERT INTO targets
    VALUES (0,'Google home page','0','NEW',NULL,'NEW','','http://www.google.com','GET','NONE','',200,10,10,0,0,0,0,0,0,0,0,1);


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



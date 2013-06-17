skypunch
========

Background
----------
Skypunch is a service monitoring system which allows monitoring of cloud services for their availability and uptime. Skypunch can be configured to monitor any REST service and inform a user to the availability, or lack of, based on configurable notification parameters.  Skypunch supports the ability to access a REST service using various HTTP authentication methods including the usage of Openstack Keystone authentication tokens.

Design
------
Skypunch runs a system daemon using an SQL database for the definition of 'targets' to be monitored. Each target defined will be monitored at the defined REST URL and method at the defined frequency. As each target is monitored, skypunch will log the result details to a log file ,update the SQL database with the results and inform a configurable user on the occurrence of an error or recovery.

    Skypunch is made up of the following main areas:
    1) Python based monitoring code.
    Skypunch is implemented in Python and uses a number of Python libraries inclusing sqlalchemy for mysql access.
    2) MySQL datbase for defined 'targets' and 'notifiers'.
    SQL table schemas for the definition of targets to be monitored and users to be notified are defined in a mysql database. 
    The most recent monitored status is also updated to the target database for each target.
    3) Configuration file for main runtime configuration.
    A config file allows for global run time settings.
    4) Log file for run time information of each monitoring request.
    A log file captures all monitored call details.
    5) Simple Command Line Interface (CLI) for interacting with.
    A CLI allows inspecting the current status of each monitored target.

Skypunch Database
-----------------
At the core of skypunch are the database tables which the skypunch daeamon uses to monitor targets and inform notifiers. 

# targets 
CREATE TABLE targets ( 
    id                 BIGINT                   NOT NULL AUTO_INCREMENT,  # unique id for this target, generated by DB when record is created
    name               VARCHAR(128)             NOT NULL,                 # tenant assigned target name
    tenantid           VARCHAR(128)             NOT NULL,                 # tenant id who owns this target 
    status             VARCHAR(50)              NOT NULL,                 # current status (NEW, PASS, FAIL)
    status_description VARCHAR(128),                                      # description for status
    previous_status    VARCHAR(50)              NOT NULL,                 # previous status (used to determine edge status)
    last_updated       TIMESTAMP                NOT NULL,                 # time that this target was last updated
    url                VARCHAR(256)             NOT NULL,                 # URL of target to use
    method             VARCHAR(128)             NOT NULL,                 # method to use with URL (GET,POST,DELETE,PUT,HEAD,PATCH)
    authn              VARCHAR(128)             NOT NULL,                 # Authentication method (NONE,BASIC,OPENSTACK)
    authn_parms        VARCHAR(256),                                      # Auth params used e.g. user=xxxx,password=yyyy [osauthendpoint=zzzz,tenantid=tttttt]
    pass_result        INT                      NOT NULL,                 # result code for success ( e.g. 200 )
    frequency          INT                      NOT NULL,                 # frequency to punch this target in seconds
    timeout            INT                      NOT NULL,                 # timeout in seconds for this request
    pass_count         BIGINT                   NOT NULL,                 # times that this target was punched with success
    fail_count         BIGINT                   NOT NULL,                 # times that this target was punched with failure
    count200           BIGINT                   NOT NULL,                 # 200 series response count
    count300           BIGINT                   NOT NULL,                 # 300 series response count
    count400           BIGINT                   NOT NULL,                 # 400 series response count
    count500           BIGINT                   NOT NULL,                 # 500 series response count
    network_fails      BIGINT                   NOT NULL,                 # network connect or read errors or timeouts
    repeated_fails     BIGINT                   NOT NULL,                 # current number of repeated failures
    enabled            BOOLEAN                  NOT NULL,                 # is this target enabled to be checked? 
    PRIMARY KEY (id)                                                      # id of targets 
 ) DEFAULT CHARSET utf8 DEFAULT COLLATE utf8_general_ci;


# notifiers
CREATE TABLE notifiers (
    id                 BIGINT                   NOT NULL AUTO_INCREMENT,  # unique id for this notifier, generated by DB when record is created
    name               VARCHAR(128)             NOT NULL,                 # name of notifier
    type               VARCHAR(50)              NOT NULL,                 # type of notifier (SMTP)
    address            VARCHAR(128)             NOT NULL,                 # who to notify ( e.g. with SMTP this is the email address ) 
    params             VARCHAR(128)             NOT NULL,                 # params based on type user=xxxx,password=yyyy,server=zzzzz
    PRIMARY KEY (id)                                                      # id of notifier 
) DEFAULT CHARSET utf8 DEFAULT COLLATE utf8_general_ci;




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


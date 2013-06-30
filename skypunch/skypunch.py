#!/usr/bin/env python

# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Peter Erik Mellquist pemellquist@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__docstring__ ="""
Skypunch is a service monitoring system allowing the active monitoring and health
checking of web services including Openstack cloud services. 
"""
__version__ = '0.3.0'

import time
import logging
import signal
import sys
import daemon
import os
import skypunchconfig
from daemon import runner
from skypunchconfig import SkyPunchConfig 
from targetmodel import TargetModel
from notifiermodel import NotifierModel
from puncher import Puncher 
from skypunchcli import SkyPunchCLI

PROGNAME = 'skypunch'
PIDFILE = '/tmp/%s.pid' % PROGNAME
START = 'start'
STOP = 'stop'

class SkyPunch:

    # setup daemon
    def __init__(self,logger):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = PIDFILE 
        self.pidfile_timeout = 0	

    # go through all targets in db then sleep and do it all again and again
    def run(self):
        print 'starting %s ....' % PROGNAME
        logger.info('starting %s ....' % PROGNAME)
        config = SkyPunchConfig(logger)	
        targetmodel = TargetModel(logger,config)
        notifiermodel = NotifierModel(logger,config)
        puncher = Puncher(logger,targetmodel)
        while True:
            targetmodel.get_session()
            notifiermodel.get_session()
            ids = targetmodel.get_ids()
            for id in ids:
                target = targetmodel.get(id)
                if target.enabled:
                    puncher.punch(target,notifiermodel)
            targetmodel.close_session()
            notifiermodel.close_session()				
            time.sleep(config.getint(skypunchconfig.SETTINGS,skypunchconfig.MAINLOOPTOV))


    # shutdown
    def stop(self,signum,frame):
        print 'shutting down %s ...' % PROGNAME
        logger.info('shutting down %s ....' % PROGNAME)
        sys.exit(0)

# start, stop or respond to command
if __name__ == "__main__":
    # set up logging
    logger = logging.getLogger(PROGNAME)
    config = SkyPunchConfig(logger)
    hdlr = logging.FileHandler(config.getstr(skypunchconfig.SETTINGS,skypunchconfig.LOGFILEPATH))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # set up CLI processor
    skypunchcli = SkyPunchCLI(logger,config) 
    options = skypunchcli.get_options()

    if len(sys.argv) == 1:
        prog_options = 'usage: %s %s | %s ' % (PROGNAME,START,STOP)
        for option in options:
             prog_options += ' | %s' % option
        print 'version: %s' % __version__
        print prog_options 
        sys.exit(1)

    if sys.argv[1] != START and sys.argv[1] != STOP and not sys.argv[1] in options:
        print 'unknown option: %s ' % sys.argv[1]
        sys.exit(1) 

    # process CLI command
    if sys.argv[1] != START and sys.argv[1] != STOP:
        skypunchcli.process_commands(sys.argv)
        sys.exit(0)

    if sys.argv[1] == START and os.path.exists(PIDFILE):
        print '%s is already running' % PROGNAME
        sys.exit(0)
   
    # daemon  
    skypunch = SkyPunch(logger)
    sprunner = runner.DaemonRunner(skypunch)
    sprunner.daemon_context.files_preserve=[hdlr.stream]	
    sprunner.daemon_context.working_directory='./'
    sprunner.daemon_context.signal_map = { signal.SIGTERM: skypunch.stop }
    try:
        sprunner.do_action()
    except daemon.runner.DaemonRunnerStopFailureError:
        print '%s is not running' % PROGNAME
        sys.exit(0)

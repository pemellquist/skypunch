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

__docstring__ = """
SkyPunchConfig is a helper class which reads in configuration settings and makes these
available through an instance of SkyPunchConfig.
"""

SETTINGS = 'settings'
MAINLOOPTOV = 'mainlooptov'
LOGFILEPATH = 'logfilepath'
DATABASE = 'database'
USER = 'user'
PASSWORD = 'password'
LOCATION = 'location'
PORT = 'port'
DBNAME = 'dbname'

import ConfigParser

class SkyPunchConfig:

    # read in all settings from config file
    def __init__(self,logger):
        config = ConfigParser.ConfigParser()	
        config.read('./skypunch.config')
        self.config = {}
        self.logger = logger
        sections = config.sections()
        for section in sections:
            try:
                self.config[section] = {}
                options = config.options(section)
                for option in options:
                    self.config[section][option] = config.get(section,option) 
            except ConfigParser.Error:
                self.logger.error('config exception on %s %s' % (section,option))	
        logger.info(self.config)

    # return an int value
    def getint(self,section,option):
        return int(self.config[section][option])

    # return a string value
    def getstr(self,section,option):
        return self.config[section][option]

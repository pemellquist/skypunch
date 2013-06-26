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
from skypunchconfig import SkyPunchConfig
from targetmodel import TargetModel
from prettytable import *


__docstring__ = """
SkyPunchCLI CLI interface into the SkyPunch daemon and database
"""

class SkyPunchCLI:
    COMMANDS = ['list','disable','enable']

    def __init__(self,logger,config):
        self.logger = logger
        self.config = config

    def get_options(self):
        return self.COMMANDS

    # process CLI commands
    def process_commands(self,commands):
        if len(commands) == 2 and commands[1] == 'list':
            self.list_all()
        elif len(commands) > 2 and commands[1] == 'list':
            self.list_individual(commands[2]) 
        elif len(commands) > 2 and commands[1] == 'disable':
            self.enable(False,commands[2])
        elif len(commands) > 2 and commands[1] == 'enable':
            self.enable(True,commands[2])

    # disable a target
    def enable(self,enable,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid target id' % id
            return
        targetmodel = TargetModel(self.logger,self.config)
        target = targetmodel.get(i)
        if target == None:
            print('id: %d does not exist' % i)
            return
        
        target.enabled=enable
        targetmodel.commit() 
        print('Target: %s has been %s'% (target.name,'Enabled'if enable else 'Disabled')) 
         

    # list details for an individual target
    def list_individual(self,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid target id' % id
            return
        targetmodel = TargetModel(self.logger,self.config)
        target = targetmodel.get(i)
        if target == None:
            print('id: %d does not exist' % i)
            return        
        details = PrettyTable(['Name','Value'])
        details.align = 'l'
        details.hrules = ALL 
        details.header = False
        details.add_row(['ID',target.id])
        details.add_row(['Name',target.name])
        details.add_row(['Status',target.status])
        details.add_row(['Enabled','Yes' if target.enabled else 'No'])
        details.add_row(['Status Description',target.status_description])
        details.add_row(['Last Updated',target.last_updated])
        details.add_row(['Target URL',target.url])
        details.add_row(['Target Method',target.method])
        details.add_row(['Authentication',target.authn])
        details.add_row(['Expected Value',target.pass_result])
        details.add_row(['Frequency (sec)',target.frequency])
        details.add_row(['Timeout (sec)',target.timeout])
        details.add_row(['Pass Count',target.pass_count])
        details.add_row(['Fail Count',target.fail_count])
        details.add_row(['200 Status Count',target.count200])
        details.add_row(['300 Status Count',target.count300])
        details.add_row(['400 Status Count',target.count400])
        details.add_row(['500 Status Count',target.count500])
        details.add_row(['Network Fail Count',target.network_fails])
        details.add_row(['Repeated Fail Count',target.repeated_fails]) 
        print details 

    # list all targets 
    def list_all(self):
        targets = PrettyTable(['ID', 'Name', 'Status', 'LastUpdated','Enabled'])
        targets.align = 'l'
        targetmodel = TargetModel(self.logger,self.config)
        ids = targetmodel.get_ids()
        for id in ids:
            target = targetmodel.get(id)    
            row = []
            row.append(target.id)
            row.append(target.name)
            row.append(target.status)
            row.append(target.last_updated)   
            row.append('Yes' if target.enabled else 'No') 
            targets.add_row(row)
        print targets

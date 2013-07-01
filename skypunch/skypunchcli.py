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
from notifiermodel import NotifierModel
from prettytable import *

__docstring__ = """
SkyPunchCLI CLI interface into the SkyPunch daemon and database
"""
ENABLE = 'enable'
DISABLE = 'disable'
TARGETS = 'targets [id] [%s | %s]' % (ENABLE,DISABLE)
NOTIFIERS = 'notifiers [id] [%s | %s]' % (ENABLE,DISABLE)
COMMANDS = [TARGETS,NOTIFIERS]

class SkyPunchCLI:

    def __init__(self,logger,config):
        self.logger = logger
        self.config = config

    # process CLI commands
    def process_commands(self,commands):
        # targets
        if len(commands) == 2 and commands[1] == TARGETS.split(' ')[0]:
            self.list_all_targets()
        elif len(commands) == 3 and commands[1] == TARGETS.split(' ')[0]:
            self.list_individual_target(commands[2])
        elif len(commands) == 4 and commands[1] == TARGETS.split(' ')[0] and commands[3] == ENABLE:
            self.enable_target(True,commands[2])
        elif len(commands) == 4 and commands[1] == TARGETS.split(' ')[0] and commands[3] == DISABLE:
            self.enable_target(False,commands[2])

        # notifiers
        elif len(commands) == 2 and commands[1] == NOTIFIERS.split(' ')[0]:
           self.list_all_notifiers()
        elif len(commands) == 3 and commands[1] == NOTIFIERS.split(' ')[0]:
           self.list_individual_notifier(commands[2])
        elif len(commands) == 4 and commands[1] == NOTIFIERS.split(' ')[0] and commands[3] == ENABLE:
            self.enable_notifier(True,commands[2])
        elif len(commands) == 4 and commands[1] == NOTIFIERS.split(' ')[0] and commands[3] == DISABLE:
            self.enable_notifier(False,commands[2])

        else:
            print 'unrecognized command'

    # enable or diable notifier
    def enable_notifier(self,enable,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid id' % id
            return
        notifiermodel = NotifierModel(self.logger,self.config)
        notifier = notifiermodel.get(i)
        if notifier == None:
            print('id: %d does not exist' % i)
            return

        notifier.enabled=enable
        notifiermodel.commit()
        print('Notifier: %s has been %s'% (notifier.name,'Enabled'if enable else 'Disabled'))


    # enable or disable a target
    def enable_target(self,enable,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid id' % id
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
    def list_individual_target(self,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid id' % id
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

    # list individual notifier
    def list_individual_notifier(self,id):
        try:
            i = int(id)
        except ValueError:
            print '%s is not a valid id' % id
            return
        notifiermodel = NotifierModel(self.logger,self.config)
        notifier = notifiermodel.get(i)
        if notifier == None:
            print('id: %d does not exist' % i)
            return
        details = PrettyTable(['Name','Value'])
        details.align = 'l'
        details.hrules = ALL
        details.header = False
        details.add_row(['ID',notifier.id])
        details.add_row(['Name',notifier.name])
        details.add_row(['Enabled','Yes' if notifier.enabled else 'No'])
        details.add_row(['Type',notifier.type])
        details.add_row(['Address',notifier.address])
        details.add_row(['Pass Count',notifier.pass_count])
        details.add_row(['Fail Count',notifier.fail_count])
        print details
 

    # list all notifiers
    def list_all_notifiers(self):
        notifiers = PrettyTable(['ID', 'Name', 'Enabled', 'Type', 'Address'])
        notifiers.align = 'l'
        notifiermodel = NotifierModel(self.logger,self.config)
        ids = notifiermodel.get_ids()
        for id in ids:
            notifier = notifiermodel.get(id)
            row = []
            row.append(notifier.id)
            row.append(notifier.name)
            row.append('Yes' if notifier.enabled else 'No')
            row.append(notifier.type)
            row.append(notifier.address)
            notifiers.add_row(row)
        print notifiers

    # list all targets 
    def list_all_targets(self):
        targets = PrettyTable(['ID', 'Name', 'Status', 'LastUpdated','Enabled','Pass Count','Fail Count'])
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
            row.append(target.pass_count)
            row.append(target.fail_count)
            targets.add_row(row)
        print targets

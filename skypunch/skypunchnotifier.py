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

from   notifiermodel import NotifierModel
from   puncher import * 
import smtplib

__docstring__ = """
SkyPunchNotifier allows sending notifications based on events ( failures or recoveries )
"""

class SkyPunchNotifier:

    # setup logger
    def __init__(self,logger):
        self.logger=logger

    # make mail body
    def make_smtp_body(self,target):
        if target.status == 'FAIL': 
            body = '\nSkypunch service monitor has detected a FAILURE\n\n' 
        elif target.status == 'PASS':
            body = '\nSkypunch service monitor has detected SUCCESS\n\n'
        else:
            body = '\nSkypunch service monitor has detected .....\n\n'

        body += 'Name : %s\n' % target.name
        body += 'Status : %s\n' % target.status
        body += 'Details : %s\n' % target.status_description
        body += 'Time : %s\n' % target.last_updated
        body += 'URL : %s\n' % target.url
        body += 'Method : %s\n' % target.method
        body += 'Authn Type : %s\n' % target.authn
        body += 'Timeout (sec) : %d\n' % target.timeout
        body += 'Frequency (sec) : %d\n\n' % target.frequency

        body += 'Statistics\n'
        body += 'Pass Count :%d\n' % target.pass_count

        return body

    # SMTP notify
    def smtp_notify(self,notifier,target):
        user = None 
        password = None
        server = None
        params = notifier.params
        options = params.split(',')
        for option in options:
            kv=option.split('=')
            if kv[0] == 'user':
                user = kv[1]
            if kv[0] == 'password':
                password = kv[1]
            if kv[0] == 'server':
                server = kv[1]
        if user == None or password == None or server == None:
            raise SkyPunchAuthParamError('user or password or server not defined')
        self.logger.info('addr: %s user: %s pwd: %s server:%s' % ( notifier.address, user, password,server))
        smtpserver = smtplib.SMTP(server,587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo 
        smtpserver.login(user, password) 

        if target.status == 'FAIL':
            subject = 'Subject: Skypunch FAILURE detected for %s' % target.name
        elif target.status == 'PASS':
            subject = 'Subject: Skypunch SUCCESS detected for %s' % target.name 
        else:
            subject = 'Subject: Skypunch %s' % (target.status,target.name)
        header = 'To:' + notifier.address + '\n' + 'From: SkyPunch'  + '\n' + subject
        body = self.make_smtp_body(target)
        msg = header + body 
        smtpserver.sendmail(user, notifier.address, msg)


    # try to notify someone
    def notify(self,target,notifiermodel):
        if target.status != target.previous_status and target.previous_status != 'NEW':
            ids = notifiermodel.get_ids(target)
            for id in ids:
                notifier = notifiermodel.get(id)
                if notifier.type == 'SMTP':
                    try:
                        self.smtp_notify(notifier,target) 
                    except SkyPunchAuthParamError as spe:
                        self.logger.warn(spe)
                        return
                    except smtplib.SMTPException as smtpe:
                        self.logger.error(smtpe)
                        return
                else:
                    self.logger.warn('unrecognized notifier type: %s for : %s' % (notifier.type,notifier.name))

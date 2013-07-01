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
import sys

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
            body = 'Skypunch Service Monitor FAILURE\n'
            status = '<td bgcolor=#FF3C3C>%s</td>' % target.status
        elif target.status == 'PASS':
            body = 'Skypunch Service Monitor SUCCESS\n'
            status = '<td bgcolor=#0AFF0A>%s</td>' % target.status
        else:
            body = 'Skypunch Service Monitor\n'
            status = '<td>%s</td>' % target.status
             

        body += '<br><table border=1 cellpadding=2 cellspacing=0>'
        body += '<tr bgcolor=#F2F2F2><td>Name</td><td><b>%s</b></td></tr>' % target.name
        body += '<tr><td>Target ID</td><td>%d (%s)</td></tr>' % (target.id,'enabled' if target.enabled else 'disabled')
        body += '<tr bgcolor=#F2F2F2><td>Status</td>%s</tr>' % status
        body += '<tr><td>Reason</td><td>%s</td></tr>' % target.status_description
        body += '<tr bgcolor=#F2F2F2><td>Last Updated</td><td>%s</td></tr>' % target.last_updated 
        body += '<tr><td>URL</td><td>%s</td></tr>' % target.url
        body += '<tr bgcolor=#F2F2F2><td>Method</td><td>%s</td></tr>' % target.method
        body += '<tr><td>Authentication</td><td>%s</td></tr>' % target.authn
        body += '<tr bgcolor=#F2F2F2><td>Frequency</td><td>Once Every %d sec</td></tr>' % target.frequency
        body += '<tr><td>Timeout</td><td>%d sec</td></tr>' % target.timeout
        body += '<tr bgcolor=#F2F2F2><td>Required Result</td><td>%s</td></tr>' % target.pass_result 
        body += '</table>'

        body += '<br>Statistics<br>'
        body += '<table border=1 cellpadding=2 cellspacing=0>'
        body += '<tr bgcolor=#F2F2F2><td>Success Count</td><td>%d</td></tr>' % target.pass_count
        body += '<tr><td>Fail Count</td><td>%d</td></tr>' % target.fail_count
        body += '<tr bgcolor=#F2F2F2><td>2XX Count</td><td>%d</td></tr>' % target.count200 
        body += '<tr><td>3XX Count</td><td>%d</td></tr>' % target.count300
        body += '<tr bgcolor=#F2F2F2><td>4XX Count</td><td>%d</td></tr>' % target.count400
        body += '<tr><td>5XX Count</td><td>%d</td></tr>' % target.count500
        body += '<tr bgcolor=#F2F2F2><td>Repeated Fails</td><td>%d</td></tr>' % target.repeated_fails
        body += '<tr><td>Network Fails</td><td>%d</td></tr>' % target.network_fails
        body += '</table>'

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
        self.logger.info('notifying %s address: %s' % (notifier.name,notifier.address))
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
        header = 'To: ' + notifier.address + '\n' + 'From: SkyPunch'  + '\n' + 'MIME-Version: 1.0' + '\n' + 'Content-type: text/html' + '\n' + subject +'\n\n'
        body = self.make_smtp_body(target)
        msg = header + body 
        smtpserver.sendmail(user, notifier.address, msg)


    # try to notify someone
    def notify(self,target,notifiermodel):
        if target.status != target.previous_status and target.previous_status != 'NEW':
            ids = notifiermodel.get_ids()
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
                    except:
                        self.logger.error('unable to notify: %s error: %s' % (notifier.name,sys.exc_info()[0]))
                        return
                else:
                    self.logger.warn('unrecognized notifier type: %s for : %s' % (notifier.type,notifier.name))

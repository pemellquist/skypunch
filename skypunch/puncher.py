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
Puncher class performs the communication to the defined target,handles various authentication, records results
and sends notifications.
"""
from 	skypunchconfig import SkyPunchConfig
from    skypunchexceptions import * 
from 	targetmodel import TargetModel
from    targetmodel import update_target_counters
from    targetmodel import update_target_status
from    notifiermodel import NotifierModel
from    skypunchnotifier import SkyPunchNotifier
from 	sqlalchemy import *
from    basicauth import *
from    openstackauth import get_openstack_auth  
import 	time
import 	datetime
from 	urlparse import urlparse 
import 	httplib
import 	base64
import  json
import  sys
import  socket

TIMEOUT = 'timeout'
PROTOCOL_HTTP = 'http'
PROTOCOL_HTTPS = 'https'
STATUS_NEW = 'NEW'
STATUS_PASS = 'PASS'
STATUS_FAIL = 'FAIL'

class Puncher:

    # set up logger, config and db model
    def __init__(self,logger,targetmodel):
        self.logger = logger
        self.targetmodel = targetmodel

    # process error condition and message
    def process_error(self,target,message):
        self.logger.error(' [%d] %-30s %s' %(target.id,target.name,message))
        target.status = STATUS_FAIL
        target.status_description = message
        target.fail_count += 1
        target.repeated_fails += 1
        self.targetmodel.commit()
        return

    # log the result line
    def log_result(self,target):
        message = ' [%d] %-30s %s %s %s (%s)' % (target.id, target.name, target.method, target.url, target.status, target.status_description)
        if target.status == STATUS_PASS:
            self.logger.info(' %s' % message)
        else:
            self.logger.error(message)

    # punch a target right now
    def punch_it_now(self,target,notifiermodel):
        response = None
        failed = False
        try:
            # parse out the target URL
            url = urlparse(target.url)
            kwargs = {TIMEOUT: target.timeout}
            location = url.netloc
            locations = location.split(':')

            # connect to the target
            if url.scheme == PROTOCOL_HTTP:
                conn = httplib.HTTPConnection(locations[0],url.port,**kwargs)
            elif url.scheme == PROTOCOL_HTTPS:
                conn = httplib.HTTPSConnection(locations[0], url.port,**kwargs)
            else:
                self.logger.warn('target protocol %s not supported for %s' % (url.scheme,target.name))
                raise SkyPunchInvalidProtocolError('target protocol %s not supported for %s' % (url.scheme,target.name)) 
            conn.connect()
            request = conn.putrequest(target.method, url.path)
           
            # HTTP Basic authentication  
            if target.authn == 'BASIC':
                try:
                    auth = get_basic_auth(target)
                    conn.putheader("Authorization", "Basic %s" % auth) 
                except SkyPunchAuthParamError as spe:
                    # improperly defined target, log error but do not notify
                    self.process_error(target,'invalid BASIC authn params (user and password required)')                
                    return
            
            # Openstack Keystone token based authentication
            elif target.authn == 'OPENSTACK':
                try:
                    auth = get_openstack_auth(target)
                    conn.putheader("X-Auth-Token",auth)
                except SkyPunchAuthParamError:
                    # improperly defined target params, log error but do not notify
                    self.process_error(target,'invalid Openstack / Keystone authn params (user,password,tenantid,osauthendpoint)')
                    return
                except SkyPunchInvalidProtocolError:
                    # improperly defined target params, log error but do not notify
                    self.process_error(target,'invalid Openstack / Keystone endpoint protocol)')
                    return
                except SkyPunchKeystoneAuthError as spe:
                    update_target_status(target,STATUS_FAIL, str(spe)) 
                    failed = True

            if not failed:
                # add headers and issue request
                conn.endheaders()
                conn.send('')
                response = conn.getresponse()

                update_target_status(target,
                    STATUS_PASS if response.status == target.pass_result else STATUS_FAIL,
                    response.reason if response.status == target.pass_result else ('target status:%d != %d' % (response.status,target.pass_result))) 
        except SystemExit, e:
            sys.exit(e)
        except socket.error as se:
            update_target_status(target,STATUS_FAIL,str(se))
        except:
            update_target_status(target,STATUS_FAIL,sys.exc_info()[0])

        self.log_result(target)

        # notify 
        notifier = SkyPunchNotifier(self.logger)
        notifier.notify(target,notifiermodel)
        
        # update counters
        update_target_counters(target,response)
        
        # save back to db
        self.targetmodel.commit()

    # find a target to punch
    def punch(self,target,notifiermodel):
        # if it is new, test it right away
        if target.status == STATUS_NEW:
            self.punch_it_now(target,notifiermodel)
        # check if its time to test
        else:
            delta = datetime.datetime.now() - target.last_updated
            if delta.seconds > target.frequency:
                self.punch_it_now(target,notifiermodel)

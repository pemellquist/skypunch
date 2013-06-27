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
from    notifiermodel import NotifierModel
from    skypunchnotifier import SkyPunchNotifier
from 	sqlalchemy import *
import 	time
import 	datetime
from 	urlparse import urlparse 
import 	httplib
import 	base64
import  json
import  sys
import  socket

USER = 'user'
PASSWORD = 'password'
OSAUTHENDPOINT = 'osauthendpoint'
TENANTID = 'tenantid'
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

    # compute http basic auth value
    def get_basic_auth(self, target):
        user = None
        password = None	
        authnargs = target.authn_parms
        options = authnargs.split(',')
        for option in options:
            kv=option.split('=')
            if kv[0] == USER:
                user = kv[1]
            if kv[0] == PASSWORD:
                password = kv[1]
        if user == None or password == None:
            raise SkyPunchAuthParamError('user or password not defined')	
        return base64.encodestring('%s:%s' % (user, password)).replace('\n', '')

    # get Openstack token from Keystone auth endpoint
    def get_openstack_auth(self,target):
        user = None
        password = None
        os_auth_endpoint = None
        tenantid = None
        authnargs = target.authn_parms
        options = authnargs.split(',')
        for option in options:
            kv=option.split('=')
            if kv[0] == USER:
                user = kv[1]
            if kv[0] == PASSWORD:
                password = kv[1]
            if kv[0] == OSAUTHENDPOINT:
                os_auth_endpoint = kv[1]
            if kv[0] == TENANTID :
                tenantid = kv[1]
        if user == None or password == None or os_auth_endpoint == None or tenantid == None:
            raise SkyPunchAuthParamError('user or password or osauthendpoint or tenantid not defined')
        try:        
            url = urlparse(os_auth_endpoint)
        except:
            self.logger.warn('target protocol %s not supported for %s' % (url.scheme, os_auth_endpoint)) 
            raise SkyPunchInvalidProtocolError('target protocol %s not supported for %s' % (url.scheme, os_auth_endpoint)) 
        location = url.netloc
        locations = location.split(':')
        kwargs = {TIMEOUT: target.timeout}
        if url.scheme == PROTOCOL_HTTP:
            conn = httplib.HTTPConnection(locations[0],url.port,**kwargs)
        elif url.scheme == PROTOCOL_HTTPS:
            conn = httplib.HTTPSConnection(locations[0], url.port,**kwargs)
        else:
            raise SkyPunchInvalidProtocolError('target protocol not supported')
        conn.connect()
        request = conn.putrequest('POST',url.path)
        login = '{ \"auth\":{ \"passwordCredentials\": { \"username":\"%s\",\"password\":\"%s\" }, \"tenantId\":\"%s\" } }' % (user,password,tenantid)
        conn.putheader("Content-Length",len(login))
        conn.putheader("Content-Type","application/json")	
        conn.endheaders()
        conn.send(login)
        response = conn.getresponse()
        if response.status != 200:
             raise SkyPunchKeystoneAuthError('Openstack keystone auth failure %d %s' % (response.status,response.reason)) 
        data = response.read()
        json_login = json.loads(data)
        keystone_token = json_login['access']['token']['id']	
        return keystone_token 

    # punch a target right now
    def punch_it_now(self,target,notifiermodel):
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
                    auth = self.get_basic_auth(target)
                    conn.putheader("Authorization", "Basic %s" % auth) 
                except SkyPunchAuthParamError as spe:
                    self.logger.error('[%d] %-30s invalid BASIC authn params (user and password required)' % (target.id, target.name))
                    target.status = STATUS_FAIL
                    target.status_description = 'invalid BASIC authn params (user and password required)'
                    target.fail_count += 1
                    target.repeated_fails += 1
                    self.targetmodel.commit()
                    return
            # Openstack Keystone token based authentication
            elif target.authn == 'OPENSTACK':
                try:
                    auth = self.get_openstack_auth(target)
                    conn.putheader("X-Auth-Token",auth)
                except SkyPunchAuthParamError:
                    self.logger.error('[%d] %-30s invalid Openstack Keystone authn params (user,password,tenantid,osauthendpoint)' % (target.id, target.name))
                    target.status = STATUS_FAIL
                    target.status_description = 'invalid Openstack / Keystone authn params (user,password,tenantid,osauthendpoint)'
                    target.fail_count += 1
                    target.repeated_fails += 1
                    self.targetmodel.commit()
                    return
                except SkyPunchInvalidProtocolError:
                    self.logger.error('[%d] %-30s invalid Openstack Keystone endpoint' % (target.id, target.name))
                    target.status = STATUS_FAIL
                    target.status_description = 'invalid Openstack / Keystone endpoint protocol)'
                    target.fail_count += 1
                    target.repeated_fails += 1
                    self.targetmodel.commit()
                    return
                except SkyPunchKeystoneAuthError as spe:
                    self.logger.error('[%d] %-30s %s' % (target.id, target.name, spe))
                    target.status = STATUS_FAIL
                    target.status_description = 'Openstack Keystone authn failure' 
                    target.fail_count += 1
                    target.repeated_fails += 1
                    self.targetmodel.commit()
                    return

            # add headers and issue request
            conn.endheaders()
            conn.send('')
            response = conn.getresponse()

            # check response, update counters and commit to db 
            if response.status == target.pass_result:
                target.previous_status = target.status
                target.status = STATUS_PASS 
                target.status_description = response.reason 
                target.pass_count += 1
                target.repeated_fails = 0
            else:
                target.previous_status = target.status
                target.status = STATUS_FAIL 
                target.status_description = 'target status:%d != %d' % ( response.status, target.pass_result)
                target.fail_count += 1
                target.repeated_fails += 1
            httpStatus = response.status
        except socket.error:
            target.previous_status = target.status
            target.status = STATUS_FAIL 
            target.fail_count +=1
            target.repeated_fails += 1
            target.status_description = 'network error to target' 
            httpStatus = 600
        except:
            target.previous_status = target.status
            target.status = STATUS_FAIL
            target.fail_count +=1
            target.repeated_fails += 1
            target.status_description = 'unable to read target response' 
            httpStatus = 600
        message = '[%d] %-30s %s %s %s (%s)' % (target.id, target.name, target.method, target.url, target.status, target.status_description)
        
        if target.status == STATUS_PASS:
            self.logger.info(' %s' % message)
        else:
            self.logger.error(message)

        # notify 
        notifier = SkyPunchNotifier(self.logger)
        notifier.notify(target,notifiermodel)
        
        # update counters
        self.update_counters(target,httpStatus)
        
        # save back to db
        self.targetmodel.commit()

    # update target counters
    def update_counters(self,target,status):
	if status >=200 and status < 300:
            target.count200 += 1
        elif status >= 300 and status < 400:
            target.count300 += 1
        elif status >= 400 and status < 500:
            target.count400 += 1
        elif status >= 500 and status < 600:
            target.count500 += 1
        else:
            target.network_fails += 1

    # find a target to punch
    def punch(self,target,notifiermodel):
        if target.status == STATUS_NEW:
            self.punch_it_now(target,notifiermodel)
        else:
            delta = datetime.datetime.now() - target.last_updated
            if delta.seconds>target.frequency:
                self.punch_it_now(target,notifiermodel)

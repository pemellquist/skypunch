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
Obtain Openstack Keystone auth token from defined Keystone endpoint and auth parameters
"""

from    skypunchexceptions import *
from    targetmodel import TargetModel
from    urlparse import urlparse
import  httplib
import  sys
import  socket
import  json

USER = 'user'
PASSWORD = 'password'
OSAUTHENDPOINT = 'osauthendpoint'
TENANTID = 'tenantid'
TIMEOUT = 'timeout'
PROTOCOL_HTTP = 'http'
PROTOCOL_HTTPS = 'https'

# get Openstack token from Keystone auth endpoint
def get_openstack_auth(target):
    user = None
    password = None
    os_auth_endpoint = None
    tenantid = None
    authnargs = target.authn_parms
    options = authnargs.split(',')
    # try to extract all params from target authn params
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
    # connect to OS endpoint and issue POST
    conn.connect()
    request = conn.putrequest('POST',url.path)
    login = '{ \"auth\":{ \"passwordCredentials\": { \"username":\"%s\",\"password\":\"%s\" }, \"tenantId\":\"%s\" } }' % (user,password,tenantid)
    conn.putheader("Content-Length",len(login))
    conn.putheader("Content-Type","application/json")
    conn.endheaders()
    conn.send(login)
    # read response
    response = conn.getresponse()
    # check for success
    if response.status != 200:
        spe =  SkyPunchKeystoneAuthError('Openstack keystone auth failure %d %s' % (response.status,response.reason))
        spe.status = response.status
        raise spe
    data = response.read()
    json_login = json.loads(data)
    # extract token from JSON response
    keystone_token = json_login['access']['token']['id']
    return keystone_token



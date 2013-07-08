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
Compute HTTP basic authentication value from target auth parameters
"""

from    skypunchexceptions import *
from    targetmodel import TargetModel
import  base64

USER = 'user'
PASSWORD = 'password'

# compute http basic auth value
def get_basic_auth(target):
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


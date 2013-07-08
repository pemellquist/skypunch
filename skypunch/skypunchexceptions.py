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
Skypunch exception classes
"""

# base class 
class SkyPunchError(Exception):
    pass

# bad auth parameters
class SkyPunchAuthParamError(SkyPunchError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# invalid protocol in target URL
class SkyPunchInvalidProtocolError(SkyPunchError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# Openstack Keystone authentication error
class SkyPunchKeystoneAuthError(SkyPunchError):
    def __init__(self, value):
        self.value = value
        self.status = 0

    def __str__(self):
        return repr(self.value)



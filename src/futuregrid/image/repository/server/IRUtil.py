# -------------------------------------------------------------------------- #
# Copyright 2010-2011, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #
"""
utility class for static methods
"""

import sys,os
from random import randrange
import hashlib

from futuregrid.utils import FGTypes,FGAuth

############################################################
# getImgId
############################################################
def getImgId():
    imgId = str(randrange(999999999999999999999999))
    return imgId

############################################################
# auth
############################################################
def auth(userId, cred):
    return FGAuth.auth(userId, cred)

if __name__ == "__main__":
    m = hashlib.md5()
    m.update("REMOVED")
    passwd_input = m.hexdigest()
    cred = FGTypes.FGCredential("ldappassmd5", passwd_input)
    if(auth("USER", cred)):
        print "logged in"
    else:
        print "access denied"

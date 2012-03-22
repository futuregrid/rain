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
This program is to terminate Twister on FutureGrid automatically
"""
#written by Bingjing Zhang

#
# no comment provided
#
# no logging used but print for debug/output
#
# no completion mesage provided if termination was succesful
#
# no error catching domne in case something goes wrong

import os
from fg_euca_twister_util import get_nodes

lines = get_nodes()

num_nodes = len(lines)

#print lines
print "Get", num_nodes, "instances,", "try to terminate them..."

#euca-terminate-instances i-4FC40839

for i in range(num_nodes):
    items = lines[i].split("\t")
    cmd = "euca-terminate-instances " + items[1].strip()
    print cmd
    os.system(cmd)

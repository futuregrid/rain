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
import os

instance_id = "emi-F3E41594"

#
# why is this a predifined instance, would that not be passed as a parameter as part of a test?
#
# no comment provided
# no namespace
#

def get_nodes():
    #get the ip addresses, test if they are ready
    text = os.popen('euca-describe-instances').read()
    lines = text.split("\n")

    #remove unrelated information
    remove_lines = []
    for line in lines:
        if line.find(instance_id) == -1:
            remove_lines.append(line)

    for line in remove_lines:
        lines.remove(line)

    return lines


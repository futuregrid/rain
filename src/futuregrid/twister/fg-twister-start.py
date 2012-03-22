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
This program is to setup Twister on FutureGrid automatically
"""
#written by Bingjing Zhang

#
# do not use _ in command anmes, relace with -
#
# no documentation provided
#
# no logging mechanism provied, e.g. print is used instead of logging for debug output
#
# no use of getopts or argparse
#
#
import os
import sys
import time
from datetime import datetime
from fg_euca_twister_util import instance_id, get_nodes
#import subprocess

args = sys.argv

if len(args) != 9:
    print "Usage: python fg_euca_start_twister.py [-k user key] [-i public key file path] [-n number of instances][-t instance type]"
    sys.exit()

#support this command and provide key, type as parameter
#instance type is twister image 
#euca-run-instances -k userkey -n 1   emi-0B951139 -t c1.medium

#intialize args
key_tag = "-k"
key = ""
pem_tag = "-i"
pem = ""
num_tag = "-n"
num = 1
type_tag = "-t"
instance_type = "c1.medium"

for i in range(len(args)):
    if cmp(args[i], key_tag) == 0:
        key = args[i + 1]
    if cmp(args[i], pem_tag) == 0:
        pem = args[i + 1]
    if cmp(args[i], num_tag) == 0:
        num = args[i + 1]
    if cmp(args[i], type_tag) == 0:
        instance_type = args[i + 1]

#print
print "User key:", key
print "User pem:", pem
print "Number of nodes:", num
print "Instance type:", instance_type





print "\n### Future Grid Euca Twister Starts...###"

#run euca-run-instances -k userkey -n 1   emi-0B951139 -t c1.medium
print "euca-run-instances -k " + key + " -n " + num + " " + instance_id + " -t " + instance_type
os.system("euca-run-instances -k " + key + " -n " + num + " " + instance_id + " -t " + instance_type)

lines = get_nodes()
num_nodes = len(lines)

if num_nodes == 0:
    print "\nNo available Twister nodes..."
    sys.exit()

print "\nGet", num_nodes, "instances,", "checking if they are all ready, please wait... (possibly needs several minutes)"
tstart = datetime.now()
ready = False
ready_count = 0

while not ready:
    lines = get_nodes()
    #print lines
    for i in range(num_nodes):
        if lines[i].find("running") != -1:
            ready_count = ready_count + 1

    #print ready_count
    if ready_count == num_nodes:
        ready = True
        break

    time.sleep(10)

tdiff = datetime.now() - tstart
print "Time used:", tdiff.seconds , "seconds."

print "Are nodes ready?", ready

#examine node information, get the ip addresses
lines = get_nodes()
ip_dict = {}
for i in range(num_nodes):
        items = lines[i].split("\t")
        #inner ip as key, outer ip as value
        ip_dict[items[4].strip()] = items[3].strip()


# output them to a file named nodes
print "Now write IP addresses to nodes file..."
home_dir = os.popen("echo $HOME").read()
home_dir = home_dir[:len(home_dir) - 1]
fp = open(home_dir + '/nodes', 'w')
for ip in ip_dict.keys():
    fp.write(ip + "\n")
fp.close()

#get a node's Twister home, scp nodes file to that directory
os.system("euca-authorize -P tcp -p 22 -s 0.0.0.0/0   default")

#get TWISTER_HOME
# the key point here is to use single quotation marks for commands
#print "ssh -i " + userkey + ".pem root@" + ip_dict.keys()[0] + " 'echo $TWISTER_HOME'"
twister_home = os.popen("ssh -i " + pem + " -o StrictHostKeyChecking=no root@" + ip_dict.values()[0] + " 'echo $TWISTER_HOME'").read()
#remove /n
twister_home = twister_home[:len(twister_home) - 1]
#twister_home = "/opt/Twister/"
print "Remote Twister Home is", twister_home

#do scp
print "Copy node file to remote..."
os.system("scp -i " + pem + " " + home_dir + "/nodes root@" + ip_dict.values()[0] + ":" + twister_home + "/bin/")

#kill all java processes
print "\n### Kill potential Twister processes...###"
os.system("ssh -i " + pem + " root@" + ip_dict.values()[0] + " 'cd " + twister_home + "/bin/; ./kill_all_java_processes.sh root'")





#log to the node,run TwisterPowerMakeUp.sh 
#print "ssh -i " + pem + ".pem root@" + ip_dict.values()[0] + " 'cd " + twister_home + "bin/; TwisterPowerMakeUp.sh'"
print "\n### Twister Auto Configuration Starts...###"
cmd_line = "ssh -i " + pem + " root@" + ip_dict.values()[0] + " 'cd " + twister_home + "/bin/; TwisterPowerMakeUp.sh'"
#print cmd_line
configuration = os.popen(cmd_line).read()
#p = subprocess.Popen(cmd_line,  shell=True, stdout=subprocess.PIPE)
#configuration = p.stdout.read() 
#print configuration
#p.wait() 
print configuration

broker_address = ""
conf_lines = configuration.split("\n")
for line in conf_lines:
    if line.find("ActiveMQ") != -1:
        for ip in ip_dict.keys():
            if line.find(ip) != -1:
                broker_address = ip_dict[ip]
                break
    if cmp(broker_address, "") != 0:
        break

print "### Notice...###"
print "Please log in to " + broker_address + " and start ActiveMQ broker."


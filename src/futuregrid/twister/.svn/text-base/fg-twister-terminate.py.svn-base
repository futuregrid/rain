#This program is to terminate Twister on FutureGrid automatically
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

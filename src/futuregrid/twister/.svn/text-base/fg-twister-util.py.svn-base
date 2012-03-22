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


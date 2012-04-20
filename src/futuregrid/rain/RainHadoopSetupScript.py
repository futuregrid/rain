#!/usr/bin/env python
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
Script to setup the Hadoop cluster.
"""

__author__ = 'Thilina Gunarathne, Javier Diaz'

from optparse import OptionParser
import xml.dom.minidom
import os
import subprocess
import sys
from subprocess import *
#
# no comments provided
#
# no man page provided, e.g. there shoudl be a README.txt that at
# least points to the man page in the portal
#     > This is an internal utility script 
#
# no failsaves provided if specified dirs already exist
#     > They are in the temp dir..So ok to override. Also we use job name
#     > in the dir name...
#
# is cleanup needed?
#

# ========================
#
#=========================

def get_config_document():
    # TODO handle if the file already exists
    doc = xml.dom.minidom.Document()
    config_element = doc.createElement("configuration")
    doc.appendChild(config_element)
    return doc, config_element

def create_property(name, value, doc):
    property_element = doc.createElement("property")

    name_element = doc.createElement("name")
    name_text_node = doc.createTextNode(name)
    name_element.appendChild(name_text_node)

    value_element = doc.createElement("value")
    value_text_node = doc.createTextNode(value)
    value_element.appendChild(value_text_node)

    property_element.appendChild(name_element)
    property_element.appendChild(value_element)
    return property_element


def create_hdfs_site(dfs_name_dir, dfs_data_dir):
    doc, config_element = get_config_document()
    config_element.appendChild(create_property("dfs.name.dir", dfs_name_dir, doc))
    config_element.appendChild(create_property("dfs.data.dir", dfs_data_dir, doc))
    return doc

def create_mapred_site(master_node_ip, mapred_local_dir):
    doc, config_element = get_config_document()
    #doc, dfs_name_property =  create_property("dfs.name.dir", "/tmp/matlab/name", doc)
    config_element.appendChild(create_property("mapred.job.tracker", master_node_ip + ":53777", doc))
    config_element.appendChild(create_property("mapred.local.dir", mapred_local_dir, doc))
    config_element.appendChild(create_property("mapreduce.map.java.opts", "-Xmx2018m", doc))
    return doc

def create_core_site(master_node_ip):
    doc, config_element = get_config_document()
    #doc, dfs_name_property =  create_property("dfs.name.dir", "/tmp/matlab/name", doc)
    config_element.appendChild(create_property("fs.default.name", "hdfs://"+master_node_ip + ":55450/", doc))
    return doc

def write_xmldoc_to_screen(doc):
    prettyString = doc.toprettyxml();
    print prettyString;

def write_xmldoc_to_file(doc, filename):
    prettyString = doc.toprettyxml();
    xml_file = open(filename, "w")
    xml_file.write(prettyString)
    xml_file.close()

# local_base_dir - dir to store 
def generate_hadoop_configs(nodes, local_base_dir, conf_dir):
    if local_base_dir != "None":
        local_base_dir = local_base_dir + os.sep
    else:
        local_base_dir = "/tmp/"
    
    confenviron = os.getenv('HADOOP_CONF_DIR')
    if conf_dir:
        conf_dir = conf_dir + os.sep
    elif confenviron:
        conf_dir = confenviron
    else:        
        cmd = "which hadoop" 
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        std = p.communicate()  
        conf_dir = std[0]
    
    master_node = nodes[0].rstrip('\n')

    masters_file_name = conf_dir + "/masters"
    masters_file = open(masters_file_name, "w")
    masters_file.write(master_node)
    masters_file.close()

    slaves_file_name = conf_dir + "/slaves"
    slaves_file = open(slaves_file_name, "w")
    slaves_file.writelines(x.rstrip('\n') + '\n' for x in nodes[1:])
    slaves_file.close()

    hdfs_site_doc = create_hdfs_site(local_base_dir + "name", local_base_dir + "data")
    write_xmldoc_to_file(hdfs_site_doc, conf_dir + "/hdfs-site.xml")

    core_site_doc = create_core_site(master_node)
    write_xmldoc_to_file(core_site_doc, conf_dir + "/core-site.xml")

    mapred_site_doc = create_mapred_site(master_node, local_base_dir + "local")
    write_xmldoc_to_file(mapred_site_doc, conf_dir + "/mapred-site.xml")

    return hdfs_site_doc, core_site_doc, mapred_site_doc

def main():
    
    parser = OptionParser()
    parser.add_option("--hostfile", dest="hostfile", help="File with the list of machines")
    parser.add_option("--hdfs", dest="hdfsdir", help="Directory to create the HDFS directory")
    parser.add_option("--confdir", dest="confdir", help="Configuration Directory")

    (options, args) = parser.parse_args()
    
    nodes_file = open(options.hostfile, "r")
    nodes = nodes_file.readlines()
    local_base_dir = options.hdfsdir
    hadoop_conf_dir = options.confdir

    generate_hadoop_configs(nodes, local_base_dir, hadoop_conf_dir)

if __name__ == "__main__":
    main()

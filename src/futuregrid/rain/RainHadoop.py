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
A shell command to dynamically deploy an Apache Hadoop environments on FG.

This command line tool deploys Apache Hadoop in to a FutureGrid resource 
and executes the given job. Users can specify a directory containing input 
data, which will get uploaded to the HDFS under the "input" directory. 
Users can also specify a directory to download the output data (contents 
of the "output" directory) from HDFS. HADOOP_HOME environment variable, 
pointing to the Hadoop distribution, needs to be set before running this 
command.
"""

__author__ = 'Thilina Gunarathne, Javier Diaz'

import subprocess
import time
import sys
import os
import argparse
from random import randrange

# TODO : Configure the conf location
class RainHadoop:

    def __init__(self):        
        super(RainHadoop, self).__init__()                   

        self._hpc = False
        self._hdfsDir = None        #In this directory we create another one that will be formated using hdfs
        self._dataInputDir = None   #user directory where input is
        self._dataOutputDir = None  #user directory where output will be
        self._hadoopDir = None      # path to the executable
        self._hadoopConfDir = None  # path to the conf directory. Typically <hadoopdir>/conf

    def setHpc(self, hpc):
        self._hpc = hpc
    
    def getHpc(self):
        return self._hpc
        
    def setHdfsDir(self, hdfsDir):
        dirtemp = str(randrange(999999999)) + "-fg-hadoop/"
        if hdfsDir:
            self._hdfsDir = hdfsDir + "/" + dirtemp
        else:
            self._hdfsDir = "/tmp/" + dirtemp            
            
    def setHadoopConfDir(self, hadoopConfDir):
        self._hadoopConfDir = hadoopConfDir
    def setDataInputDir(self, dataInputDir):
        self._dataInputDir = dataInputDir
    def setDataOutputDir(self, dataOutputDir):
        self._dataOutputDir = dataOutputDir
    def setHadoopDir(self, hadoopDir):
        self._hadoopDir = hadoopDir
    
    def generate_shutdown(self):
        job_script = "stop-mapred.sh" + "\n"
        job_script += "stop-dfs.sh" + "\n"
        return job_script


    def generate_runjob(self, hadoop_command):
        job_script = "";
        if (self._dataInputDir):
            job_script += "hadoop fs -put "
            job_script += self._dataInputDir + " " + os.path.basename(self._dataInputDir.rstrip("/")) + " \n"        
        job_script += "echo Running the hadoop job  \n"
        job_script += "hadoop " + hadoop_command + "\n \n"
        if (self._dataOutputDir):
            job_script += "hadoop fs -get " + os.path.basename(self._dataOutputDir.rstrip("/")) + " "
            job_script += self._dataOutputDir + " \n"
        return job_script

    def generate_start_hadoop(self):
        job_script = "echo Generating Configuration Scripts \n"
        job_script += "python $HOME/RainHadoopSetupScript.py --hostfile "
        if self._hpc:
            job_script += " $PBS_NODEFILE "
        else:
            job_script += " $HOME/machines "
        job_script += str(self._hdfsDir) + " \n " #+ str(self._hadoopConfDir) + " \n\n"
        job_script += "echo Formatting HDFS  \n"
        job_script += "hadoop namenode -format   \n\n"
        job_script += "echo Starting the cluster  \n"
        job_script += "start-dfs.sh \n"
        job_script += "echo Waiting in the safemode  \n"
        job_script += "hadoop dfsadmin -safemode wait \n"
        job_script += "echo Starting MapReduce daemons  \n"
        job_script += "start-mapred.sh  \n"        
        return job_script


    def save_job_script(self, job_name, job_script):
        job_script_name = job_name
        job_script_file = open(job_script_name, "w")
        job_script_file.write(job_script)
        job_script_file.close()
        return job_script_name

"""
    def generate_PBS_directives(self, job_name, walltime, num_nodes, queue):
        job_script = "#!/bin/bash \n"
        job_script += "#PBS -l nodes=" + str(num_nodes) + ":ppn=8 \n"
        if (walltime):
            job_script += "#PBS -l walltime=" + walltime + " \n"
        job_script += "#PBS -N " + job_name + " \n"
        if (queue):
            job_script += "#PBS -q " + queue + " \n"
        job_script += "#PBS -V \n"
        job_script += "#PBS -o " + job_name + ".$PBS_JOBID.out \n \n"
        return job_script

    
    def runJob(self, args, hadoop_cmd, jobname):
        hadoop_home = os.environ.get("HADOOP_HOME")
        if (not hadoop_home):
            print("HADOOP_HOME is not set.")
        else :
            local_storage_dir = "/tmp/$PBS_JOBID-fg-hadoop"
            # gvl: tmp dir must be able to be specified. is probably globally set?
            hadoop_conf_dir = "$HADOOP_HOME/conf"

            job_script = self.generate_PBS_directives(jobname, args.walltime, args.nodes, args.queue)
            job_script += self.generate_start_hadoop(local_storage_dir, hadoop_conf_dir)
            job_script += self.generate_runjob(hadoop_cmd, args.inputdir, args.outputdir)
            job_script += self.generate_shutdown()
            job_script_name = self.save_job_script(jobname, job_script)

            print("Generated Job Script :" + job_script_name)
            #subprocess.call("qsub " + job_script_name, shell = True)
"""

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
FutureGrid Command Line Interface

FG-Hadoop
"""
__author__ = 'Thilina Gunarathne'

import os
#import cmd
import readline
import sys
from futuregrid.shell import fgShellUtils
from futuregrid.hadoop.fgHadoop import fgHadoop
from futuregrid.image.repository.client import IRTypes
import logging
from futuregrid.utils import fgLog
from cmd2 import Cmd
from cmd2 import options
from cmd2 import make_option


class fgShellHadoop(Cmd):

    ############################################################
    # init
    ############################################################
    def __init__(self):
        self._fgHadoop = fgHadoop()

    ############################################################
    # hadooprunjob
    ############################################################

    @options([make_option('-j', '--jobname',
                          help = 'Provide a name for the job.'),
              make_option('-i', '--inputdir',
                          help = 'Directory containing the input data for the job'),
              make_option('-o', '--outputdir',
                          help = 'Directory to store the output data from the job'),
              make_option('-q', '--queue',
                          help = 'Queue to submit the job',
                          default = "batch"),
              make_option('-w', '--walltime',
                          help = 'Walltime for the job (hh:mm:ss)',
                          default = '00:20:00'),
              make_option('-n', '--nodes',
                          help = 'Number of nodes for the job',
                          default = 2, type = int)    ])
    def do_hadooprunjob(self, args, opts):
        """Run a hadoop job"""
        hadoop_home = os.environ.get("HADOOP_HOME")
        job_name = opts.jobname

        if (not hadoop_home):
            print("HADOOP_HOME is not set.")
        elif(not job_name):
            print("Job name (-j or --jobname) is required.")
        else :
            hadoop_cmd = ''.join(args)
            # for some reason __init__() does not get called..Hence putting this here 
            #self._fgHadoop = fgHadoop()
            self._fgHadoop.runJob(opts, hadoop_cmd, job_name)
            #self._log.error("SHElll test in fgshell repo")


    @options([make_option('-j', '--jobname',
                          help = 'Provide a name for the job.'),
              make_option('-q', '--queue',
                          help = 'Queue to submit the job',
                          default = "batch"),
              make_option('-w', '--walltime',
                          help = 'Walltime for the job (hh:mm:ss)',
                          default = '00:20:00'),
              make_option('-n', '--nodes',
                          help = 'Number of nodes for the job',
                          default = 2, type = int)    ])
    def do_hadooprunscript(self, args, opts):
        """Run a hadoop job"""
        hadoop_home = os.environ.get("HADOOP_HOME")
        job_name = opts.jobname

        if (not hadoop_home):
            print("HADOOP_HOME is not set.")
        elif(not job_name):
            print("Job name (-j or --jobname) is required.")
        else :
            hadoop_cmd = ''.join(args)
            self._fgHadoop.runScript(opts, hadoop_cmd, job_name)
            #self._log.error("SHElll test in fgshell repo")

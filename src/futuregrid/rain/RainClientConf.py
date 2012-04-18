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
Class to read Rain Client configuration
"""

__author__ = 'Javier Diaz'

import os
import ConfigParser
import string
import sys
import logging

configFileName = "fg-client.conf"

class RainClientConf(object):

    ############################################################
    # init
    ############################################################

    def __init__(self):
        super(RainClientConf, self).__init__()

        ###################################
        #These should be sent from the Shell. We leave it for now to have an independent IR.   
        self._fgpath = ""
        try:
            self._fgpath = os.environ['FG_PATH']
        except KeyError:
            self._fgpath = os.path.dirname(__file__) + "/../"

        ##DEFAULT VALUES##
        self._localpath = "~/.fg/"
        
        self._configfile = os.path.expanduser(self._localpath) + "/" + configFileName
        #print self._configfile
        if not os.path.isfile(self._configfile):
            self._configfile = "/etc/futuregrid/" + configFileName
            #print self._configfile
            #if not os.path.isfile(self._configfile):
            #    self._configfile = os.path.expanduser(os.path.dirname(__file__)) + "/" + configFileName
                #print self._configfile

            if not os.path.isfile(self._configfile):   
                print "ERROR: configuration file "+configFileName+" not found"
                sys.exit(1)
        
        ####################################

        self._refresh = 0
        self._moab_max_wait = 0
        self._moab_images_file = ""
        self._loginnode = ""
        self._logfile = "" #self._localpath__+"/fg.log"
        self._logLevel = "DEBUG"
        self._logType = ["DEBUG", "INFO", "WARNING", "ERROR"]

        self.loadConfig()



    def getConfigFile(self):
        return self._configfile

    def getMoabMaxWait(self):
        return self._moab_max_wait
    
    def getMoabImagesFile(self):
        return self._moab_images_file
    
    def getLoginNode(self):
        return self._loginnode
    
    def getRefresh(self):
        return self._refresh

    def getLogFile(self):
        return self._logfile

    def getLogLevel(self):
        return self._logLevel


    ############################################################
    # loadConfig
    ############################################################
    def loadConfig(self):
        section = 'Rain'
        config = ConfigParser.ConfigParser()
        if(os.path.isfile(self._configfile)):
            config.read(self._configfile)
        else:
            print "Error: Config file not found" + self._configfile
            sys.exit(1)
        
        try:
            self._moab_max_wait = int(config.get(section, 'moab_max_wait', 0))
        except ConfigParser.NoOptionError:
            print "Error: No moab_max_wait option found in section " + section + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "Error: no section "+section+" found in the "+self._configfile+" config file"
            sys.exit(1)
        try:
            self._moab_images_file = os.path.expanduser(config.get(section, 'moab_images_file', 0))
        except ConfigParser.NoOptionError:
            print "Error: No moab_images_file option found in section "+section + " file " + self._configfile
            sys.exit(1)        
        try:
            self._refresh = int(config.get(section, 'refresh', 0))
        except ConfigParser.NoOptionError:
            print "Error: No refresh option found in section " + section + " file " + self._configfile
            sys.exit(1)   
        try:
            self._loginnode = config.get(section, 'loginnode', 0)
        except ConfigParser.NoOptionError:
            print "Error: No loginnode option found in section "+section + " file " + self._configfile
            sys.exit(1)           
        try:
            self._logfile = os.path.expanduser(config.get(section, 'log', 0))
        except ConfigParser.NoOptionError:
            print "Error: No log option found in section "+section + " file " + self._configfile
            sys.exit(1)
        
        #dir=os.path.dirname(self._logfile)
        #if not (os.path.isdir(dir)):
        #    os.system("mkdir -p " + dir)
        ##Log
        try:
            tempLevel = string.upper(config.get(section, 'log_level', 0))
        except ConfigParser.NoOptionError:
            tempLevel = self._LogLevel

        if not (tempLevel in self._logType):
            print "Log level " + tempLevel + " not supported. Using the default one " + self._logLevel
            tempLevel=self._logLevel
        self._logLevel = eval("logging." + tempLevel)

        
       

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
Class to read Image Management Client configuration
"""

__author__ = 'Javier Diaz'

import os
import ConfigParser
import string
import sys
import logging

configFileName = "fg-client.conf"

class IMClientConf(object):

    ############################################################
    # init
    ############################################################

    def __init__(self):
        super(IMClientConf, self).__init__()

 
        self._fgpath = ""
        try:
            self._fgpath = os.environ['FG_PATH']
        except KeyError:
            self._fgpath = os.path.dirname(__file__) + "/../../"

        ##DEFAULT VALUES##
        self._localpath = "~/.fg/"

        self._configfile = os.path.expanduser(self._localpath) + "/" + configFileName
        #print self._configfile
        if not os.path.isfile(self._configfile):
            self._configfile = "/etc/futuregrid/" + configFileName #os.path.expanduser(self._fgpath) + "/etc/" + configFileName
            #print self._configfile
            #if not os.path.isfile(self._configfile):
            #    self._configfile = os.path.expanduser(os.path.dirname(__file__)) + "/" + configFileName
                #print self._configfile

            if not os.path.isfile(self._configfile):   
                print "ERROR: configuration file " + configFileName + " not found"
                sys.exit(1)
                    
        self._logLevel_default = "DEBUG"
        self._logType = ["DEBUG", "INFO", "WARNING", "ERROR"]

        #image generation
        self._serveraddr = ""
        self._gen_port = 0        
        self._ca_certs_gen = ""
        self._certfile_gen = ""
        self._keyfile_gen = ""
        self._logFileGen = ""
        self._logLevelGen = ""
        
        #image Register
        self._xcat_port = 0
        self._moab_port = 0
        self._iaas_serveraddr = ""
        self._iaas_port = 0
        self._http_server = ""
        self._ca_certs_dep = ""
        self._certfile_dep = ""
        self._keyfile_dep = ""
        self._logFileRegister = ""
        self._logLevelRegister = ""
        self._tempdirRegister = ""

        #Register-machines        
        self._loginmachine = ""
        self._moabmachine = ""
        self._xcatmachine = ""

        self._config = ConfigParser.ConfigParser()
        self._config.read(self._configfile)

    ############################################################
    # getConfigFile
    ############################################################
    def getConfigFile(self):
        return self._configfile
    
    #Image Generation
    def getServeraddr(self):
        return self._serveraddr
    def getGenPort(self):
        return self._gen_port
    def getCaCertsGen(self):
        return self._ca_certs_gen
    def getCertFileGen(self): 
        return self._certfile_gen
    def getKeyFileGen(self): 
        return self._keyfile_gen
    def getLogFileGen(self):
        return self._logFileGen
    def getLogLevelGen(self):
        return self._logLevelGen
    
    #Image registration
    def getXcatPort(self):
        return self._xcat_port
    def getMoabPort(self):
        return self._moab_port
    def getIaasServerAddr(self):
        return self._iaas_serveraddr
    def getIaasPort(self):
        return self._iaas_port
    def getHttpServer(self):
        return self._http_server
    def getCaCertsDep(self):
        return self._ca_certs_dep
    def getCertFileDep(self): 
        return self._certfile_dep
    def getKeyFileDep(self): 
        return self._keyfile_dep    
    def getLogFileRegister(self):
        return self._logFileRegister
    def getLogLevelRegister(self):
        return self._logLevelRegister
    def getTempDirRegister(self):
        return self._tempdirRegister

    #Machines information
#    def getSharedDir(self):
#        return self._shareddir
    def getLoginMachine(self):
        return self._loginmachine
    def getMoabMachine(self):
        return self._moabmachine
    def getXcatMachine(self):
        return self._xcatmachine
    
    
    ############################################################
    # load_generationConfig
    ############################################################
    def load_generationConfig(self):        
        
        section = "Generation"
        try:
            self._serveraddr = self._config.get(section, 'serveraddr', 0)
        except ConfigParser.NoOptionError:
            print "Error: No serveraddr option found in section " + section + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "Error: no section " + section + " found in the " + self._configfile + " config file"
            sys.exit(1)
        #Server address        
        try:
            self._gen_port = int(self._config.get(section, 'port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No port option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            self._ca_certs_gen = os.path.expanduser(self._config.get(section, 'ca_cert', 0))
        except ConfigParser.NoOptionError:
            print "Error: No ca_cert option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._ca_certs_gen):
            print "Error: ca_cert file not found in " + self._ca_certs_gen 
            sys.exit(1)
        try:
            self._certfile_gen = os.path.expanduser(self._config.get(section, 'certfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No certfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._certfile_gen):
            print "Error: certfile file not found in " + self._certfile_gen 
            sys.exit(1)
        try:
            self._keyfile_gen = os.path.expanduser(self._config.get(section, 'keyfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No keyfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._keyfile_gen):
            print "Error: keyfile file not found in " + self._keyfile_gen 
            sys.exit(1)
        try:
            self._logFileGen = os.path.expanduser(self._config.get(section, 'log', 0))
        except ConfigParser.NoOptionError:
            print "Error: No log option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            tempLevel = string.upper(self._config.get(section, 'log_level', 0))
        except ConfigParser.NoOptionError:
            tempLevel = self._logLevel_default
        if not (tempLevel in self._logType):
            print "Log level " + tempLevel + " not supported. Using the default one " + self._logLevel_default
            tempLevel = self._logLevel_default
        self._logLevelGen = eval("logging." + tempLevel)


    ############################################################
    # load_RegisterConfig
    ############################################################
    def load_registerConfig(self):
        
        section = "Register"        
        try:
            self._xcat_port = int(self._config.get(section, 'xcat_port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No xcat_port option found in section " + section + " file " + self._configfile
            sys.exit(1)  
        except ConfigParser.NoSectionError:
            print "Error: no section " + section + " found in the " + self._configfile + " config file"
            sys.exit(1)      
        try:
            self._moab_port = int(self._config.get(section, 'moab_port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No moab_port option found in section " + section + " file " + self._configfile
            sys.exit(1)   
        try:
            self._iaas_serveraddr = self._config.get(section, 'iaas_serveraddr', 0)
        except ConfigParser.NoOptionError:
            print "Error: No iaas_serveraddr option found in section " + section
            sys.exit(1)
        try:
            self._iaas_port = int(self._config.get(section, 'iaas_port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No iaas_port option found in section " + section + " file " + self._configfile
            sys.exit(1)                      
        try:
            self._http_server = self._config.get(section, 'http_server', 0)
        except ConfigParser.NoOptionError:
            print "Error: No http_server option found in section " + section + " file " + self._configfile
            sys.exit(1)        
        try:
            self._tempdirRegister = os.path.expanduser(self._config.get(section, 'tempdir', 0))
        except ConfigParser.NoOptionError:
            self._tempdirRegister = "./"
        try:
            self._ca_certs_dep = os.path.expanduser(self._config.get(section, 'ca_cert', 0))
        except ConfigParser.NoOptionError:
            print "Error: No ca_cert option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._ca_certs_dep):
            print "Error: ca_cert file not found in " + self._ca_certs_dep 
            sys.exit(1)
        try:
            self._certfile_dep = os.path.expanduser(self._config.get(section, 'certfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No certfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._certfile_dep):
            print "Error: certfile file not found in " + self._certfile_dep 
            sys.exit(1)
        try:
            self._keyfile_dep = os.path.expanduser(self._config.get(section, 'keyfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No keyfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._keyfile_dep):
            print "Error: keyfile file not found in " + self._keyfile_dep 
            sys.exit(1)
        try:
            self._logFileRegister = os.path.expanduser(self._config.get(section, 'log', 0))
        except ConfigParser.NoOptionError:
            print "Error: No log option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            tempLevel = string.upper(self._config.get(section, 'log_level', 0))
        except ConfigParser.NoOptionError:
            tempLevel = self._logLevel_default
        if not (tempLevel in self._logType):
            print "Log level " + tempLevel + " not supported. Using the default one " + self._logLevel_default
            tempLevel = self._logLevel_default
        self._logLevelRegister = eval("logging." + tempLevel)

    ############################################################
    # load_machineConfig
    ############################################################
    def load_machineConfig(self, machine):
        
        try:
            self._loginmachine = self._config.get(machine, 'loginmachine', 0)
        except ConfigParser.NoOptionError:
            print "Error: No loginmachine option found in section " + machine + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "Error: no section " + machine + " found in the " + self._configfile + " config file"
            sys.exit(1)              
        try:
            self._moabmachine = self._config.get(machine, 'moabmachine', 0)
        except ConfigParser.NoOptionError:
            print "Error: No moabmachine option found in section " + machine + " file " + self._configfile
            sys.exit(1)
        try:
            self._xcatmachine = self._config.get(machine, 'xcatmachine', 0)
        except ConfigParser.NoOptionError:
            print "Error: No xcatmachine option found in section " + machine + " file " + self._configfile
            sys.exit(1) 


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
Class to read Image Repository Client configuration
"""

__author__ = 'Javier Diaz'

import os
import ConfigParser
import string
import sys
import logging

configFileName = "fg-client.conf"

class IRClientConf(object):

    ############################################################
    # init
    ############################################################

    def __init__(self):
        super(IRClientConf, self).__init__()

        ###################################
        #These should be sent from the Shell. We leave it for now to have an independent IR.   
        self._fgpath = ""
        try:
            self._fgpath = os.environ['FG_PATH']
        except KeyError:
            self._fgpath = os.path.dirname(__file__) + "/../../../"

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
                print "ERROR: configuration file "+configFileName+" not found"
                sys.exit(1)
        
        ####################################

        #IR Server Config file
        #self._irconfig = ".IRconfig"
        self._port = 0
        self._serveraddr = ""
        self._ca_certs = ""
        self._certfile = ""
        self._keyfile = ""
        #IR Client Config
        #self._backend = ""
        #self._fgirimgstore = ""

        self._logfile = "" #self._localpath__+"/fg.log"
        self._logLevel = "DEBUG"
        self._logType = ["DEBUG", "INFO", "WARNING", "ERROR"]

        self.loadConfig()

        #self._backends = ["mongodb", "mysql", "swiftmysql", "swiftmongo", "cumulusmysql", "cumulusmongo"] #available backends
        #self._setupBackend()

        ###TODO ADD SSH KEY TO SSH-ADD


    ############################################################
    # getLogHistDir
    ############################################################
    def getLogHistDir(self):
        return self._localpath

    ############################################################
    # getConfigFile
    ############################################################
    def getConfigFile(self):
        return self._configfile

    ############################################################
    # getLogFile
    ############################################################
    def getLogFile(self):
        return self._logfile

    ############################################################
    # getLogLevel
    ############################################################
    def getLogLevel(self):
        return self._logLevel

    def getCaCerts(self):
        return self._ca_certs
    def getCertFile(self): 
        return self._certfile
    def getKeyFile(self): 
        return self._keyfile   
    ############################################################
    # getIrconfig
    ############################################################
    #def getIrconfig(self):
    #    return self._irconfig

    ############################################################
    # getBackend
    ############################################################
    #def getBackend(self):
    #    return self._backend

    ############################################################
    # getFgirimgstore
    ############################################################
    #def getFgirimgstore(self):
    #    return self._fgirimgstore

    ############################################################
    # getServerdir
    ############################################################
    def getPort(self):
        return self._port

    ############################################################
    # getServeraddr
    ############################################################
    def getServeraddr(self):
        return self._serveraddr

    ############################################################
    # loadConfig
    ############################################################
    def loadConfig(self):
        section = 'Repo'
        config = ConfigParser.ConfigParser()
        if(os.path.isfile(self._configfile)):
            config.read(self._configfile)
        else:
            print "Error: Config file not found" + self._configfile
            sys.exit(1)
                
        try:
            self._logfile = os.path.expanduser(config.get(section, 'log', 0))
        except ConfigParser.NoOptionError:
            print "Error: No log option found in section "+section + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "Error: no section "+section+" found in the "+self._configfile+" config file"
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

        #Server dir
        try:
            self._port = int(config.get(section, 'port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No port option found in section "+section + " file " + self._configfile
            sys.exit(1)
        #Server address
        try:
            self._serveraddr = os.path.expanduser(config.get(section, 'serveraddr', 0))
        except ConfigParser.NoOptionError:
            print "Error: No serveraddr option found in section "+section + " file " + self._configfile
            sys.exit(1)
        
        try:
            self._ca_certs = os.path.expanduser(config.get(section, 'ca_cert', 0))
        except ConfigParser.NoOptionError:
            print "Error: No ca_cert option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._ca_certs):
            print "Error: ca_cert file not found in "  + self._ca_certs 
            sys.exit(1)
        try:
            self._certfile = os.path.expanduser(config.get(section, 'certfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No certfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._certfile):
            print "Error: certfile file not found in "  + self._certfile 
            sys.exit(1)
        try:
            self._keyfile = os.path.expanduser(config.get(section, 'keyfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No keyfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._keyfile):
            print "Error: keyfile file not found in "  + self._keyfile 
            sys.exit(1)
        
        #try:
        #    self._irconfig = os.path.expanduser(config.get('Repo', 'IRConfig', 0))
        #except ConfigParser.NoOptionError:
        #    print "Error: No IRconfig option found in section Repo"
        #    sys.exit(1)
            
        #dir=os.path.dirname(self._irconfig)
        #if not (os.path.isdir(dir)):
        #    os.system("mkdir -p " + dir)

    ############################################################
    # _setupBackend 
    ############################################################
    """
    def _setupBackend (self):
        userId = os.popen('whoami', 'r').read().strip()
        if not os.path.isfile(self._irconfig):
            cmdexec = " '" + self._serverdir + \
                    "IRService.py --getBackend " + userId + "'"

            print "Requesting Respository Server Config"
            #aux=self._rExec(userId, cmdexec)
            cmdssh = "ssh " + userId + "@" + self._serveraddr
            aux = os.popen(cmdssh + cmdexec).read().strip()
            aux = aux.split("\n")

            self._backend = aux[0].strip()
            self._fgirimgstore = aux[1].strip()
            try:
                f = open(self._irconfig, "w")
                f.write(self._backend + '\n')
                f.write(self._fgirimgstore)
                f.close()
            except(IOError), e:
                print "Unable to open the file", self._irconfig, "Ending program.\n", e
        else:
            print "Reading Repository Server Config from " + self._irconfig
            try:
                f = open(self._irconfig, "r")
                self._backend = f.readline()
                if not (self._backend.strip() in self._backends):
                    print "Error in local config. Please remove file: " + self._irconfig
                    sys.exit(1)
                self._fgirimgstore = f.readline()
                f.close()
            except(IOError), e:
                print "Unable to open the file", self._irconfig, "Ending program.\n", e
        print "Repository Information Read"
    """

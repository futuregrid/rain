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
utility class for static methods
"""

import logging
import sys, os
import ConfigParser
import string
################
#BACKEND CONFIG
################

configFileName = "fg-server.conf"

class IRServerConf(object):

    ############################################################
    # init
    ############################################################

    def __init__(self):
        super(IRServerConf, self).__init__()
        
        #we configure this log because the server is executed remotly
        
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
                self._log.error("ERROR: configuration file " + configFileName + " not found")
                sys.exit(1)
                    
        #image repo server
        self._port = 0
        self._proc_max = 0
        self._refresh_status = 0
        #image repo server
        self._nopasswdusers = {}  #dic {'user':['ip','ip1'],..}
        self._authorizedUsers = []
        self._backend = ""
        self._log_repo = ""
        self._logLevel_repo = ""
        #self._idp = ""
        self._ca_certs = ""
        self._certfile = ""
        self._keyfile = ""
        #image repo server backends
        self._address = ""
        self._userAdmin = ""
        self._configFile = ""
        self._addressS = ""
        self._userAdminS = ""
        self._configFileS = ""
        self._imgStore = ""
        
        #image rest interface
        self._confRestFile = ""
               
        self._logLevel_default = "DEBUG"
        self._logType = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        self._config = ConfigParser.ConfigParser()
        self._config.read(self._configfile)
               
    def getServerConfig(self):
        return self._configfile
    def getLogRepo(self):
        return self._log_repo
    def getLogLevelRepo(self):
        return self._logLevel_repo
    
    #image generation server
    def getPort(self):
        return self._port
    def getProcMax(self):
        return self._proc_max
    def getRefreshStatus(self):
        return self._refresh_status
    
    def getNoPasswdUsers(self):
        return self._nopasswdusers    
    def getAuthorizedUsers(self):
        return self._authorizedUsers    
    def getBackend(self):
        return self._backend
    #def getIdp(self):
    #    return self._idp
    def getCaCerts(self):
        return self._ca_certs
    def getCertFile(self): 
        return self._certfile
    def getKeyFile(self): 
        return self._keyfile   
    
    
    def getAddress(self):
        return self._address
    def getUserAdmin(self):
        return self._userAdmin
    def getConfigFile(self):
        return self._configFile
    def getAddressS(self):
        return self._addressS
    def getUserAdminS(self):
        return self._userAdminS
    def getConfigFileS(self):
        return self._configFileS
    def getImgStore(self):
        return self._imgStore
    
    def getRestConfFile(self):
        return self._restConfFile
    
    ############################################################
    # loadConfig
    ############################################################
    def loadRepoServerConfig(self):
        section = "RepoServer"
        try:
            self._port = int(self._config.get(section, 'port', 0))
        except ConfigParser.NoOptionError:
            print "Error: No port option found in section " + section + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "Error: no section " + section + " found in the " + self._configfile + " config file"
            sys.exit(1)
        try:
            self._proc_max = int(self._config.get(section, 'proc_max', 0))
        except ConfigParser.NoOptionError:
            print "Error: No proc_max option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            self._refresh_status = int(self._config.get(section, 'refresh', 0))            
        except ConfigParser.NoOptionError:
            print "Error: No refresh option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            aux = self._config.get(section, 'authorizedusers', 0)
            aux1 = aux.split(",")
            for i in aux1:
                if (i.strip() != ""):
                    self._authorizedUsers.append(i.strip())
        except ConfigParser.NoOptionError:
            #print "No authorizedusers option found in section " + section + " file " + self._configfile
            #sys.exit(1)
            pass  
        try:
            aux = self._config.get(section, 'nopasswdusers', 0).strip()
            aux = "".join(aux.split()) #REMOVE ALL WHITESPACES
            parts = aux.split(";")
            for i in parts:         
                temp = i.split(":")                    
                self._nopasswdusers[temp[0]] = temp[1].split(",")            
        except ConfigParser.NoOptionError:            
            pass          
        try:
            self._backend = self._config.get(section, 'backend', 0)
        except ConfigParser.NoOptionError:
            print "No backend option found in section " + section + " file " + self._configfile
            sys.exit(1)          
        #try:
        #    self._idp = self._config.get(section, 'idp', 0)
        #except ConfigParser.NoOptionError:
        #    print "No idp option found in section " + section + " file " + self._configfile
        #    sys.exit(1)  
        #except ConfigParser.NoSectionError:
        #    print "no section "+section+" found in the "+self._configfile+" config file"
        #    sys.exit(1)
        try:
            self._log_repo = os.path.expanduser(self._config.get(section, 'log', 0))
        except ConfigParser.NoOptionError:
            print "No log option found in section " + section + " file " + self._configfile
            sys.exit(1)
        try:
            tempLevel = string.upper(self._config.get(section, 'log_level', 0))
        except ConfigParser.NoOptionError:
            tempLevel = self._logLevel_default
        if not (tempLevel in self._logType):
            print "Warning: Log level " + tempLevel + " not supported. Using the default one " + self._logLevel_default
            tempLevel = self._logLevel_default
        self._logLevel_repo = eval("logging." + tempLevel)
        try:
            self._ca_certs = os.path.expanduser(self._config.get(section, 'ca_cert', 0))
        except ConfigParser.NoOptionError:
            print "Error: No ca_cert option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._ca_certs):
            print "Error: ca_cert file not found in " + self._ca_certs 
            sys.exit(1)
        try:
            self._certfile = os.path.expanduser(self._config.get(section, 'certfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No certfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._certfile):
            print "Error: certfile file not found in " + self._certfile 
            sys.exit(1)
        try:
            self._keyfile = os.path.expanduser(self._config.get(section, 'keyfile', 0))
        except ConfigParser.NoOptionError:
            print "Error: No keyfile option found in section " + section + " file " + self._configfile
            sys.exit(1)
        if not os.path.isfile(self._keyfile):
            print "Error: keyfile file not found in " + self._keyfile 
            sys.exit(1)
        try:
            self._restConfFile = os.path.expanduser(self._config.get(section, 'restConfFile', 0))
        except ConfigParser.NoOptionError:
            print "Warning: No option restConfFile in section " + section + ". You will not be able to use the rest interface"      
        #load backend storage configuration
        try:
            self._address = self._config.get(self._backend, 'address', 0)
        except ConfigParser.NoOptionError:
            print "No option address in section " + self._backend + " file " + self._configfile
            sys.exit(1)
        except ConfigParser.NoSectionError:
            print "No section " + self._backend + " found in the " + self._configfile + " config file"
            sys.exit(1)   
        try:
            self._userAdmin = self._config.get(self._backend, 'userAdmin', 0)
        except ConfigParser.NoOptionError:
            print "No option userAdmin in section " + self._backend + " file " + self._configfile
            sys.exit(1)
        try:
            self._configFile = os.path.expanduser(self._config.get(self._backend, 'configFile', 0))
        except ConfigParser.NoOptionError:
            print "No option configFile in section " + self._backend + " file " + self._configfile
            sys.exit(1)
        #only for those config with secondary service
        if (self._backend != "mongodb" and self._backend != "mysql"):
            try:
                self._addressS = self._config.get(self._backend, 'addressS', 0)
            except ConfigParser.NoOptionError:
                print "No option addressS in section " + self._backend + " file " + self._configfile
                sys.exit(1)
            try:
                self._userAdminS = self._config.get(self._backend, 'userAdminS', 0)
            except ConfigParser.NoOptionError:
                print "No option userAdminS in section " + self._backend + " file " + self._configfile
                sys.exit(1)
            try:
                self._configFileS = os.path.expanduser(self._config.get(self._backend, 'configFileS', 0))
            except ConfigParser.NoOptionError:
                print "No option configFileS in section " + self._backend + " file " + self._configfile
                sys.exit(1)        
        try:
            self._imgStore = os.path.expanduser(self._config.get(self._backend, 'imgStore', 0))
        except ConfigParser.NoOptionError:
            print "No option imgStore in section " + self._backend + " file " + self._configfile
            sys.exit(1)  
    
        
                



#!/usr/bin/python

import sys
import os
import os.path
import cherrypy
from cherrypy.lib import cptools

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname( os.path.realpath( __file__ ) )+'/../server/')
from utils import fgLog
from subprocess import Popen
from subprocess import PIPE

import IRUtil


## Class distributions 
class distributions() :

    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        self._log = fgLog.fgLog(IRUtil.getLogFile(), IRUtil.getLogLevel(), "getDistributions", False)
        self.returnCode = 0
        kernel = self.runCmd('uname -s')
        if kernel == "Darwin\n" :
            self._log.info("Using Darwin kernel ")
            self.openssl_dist = 'http://www.openssl.org/source/openssl-1.0.0d.tar.gz'
            self.openssl_dir = 'openssl-1.0.0d'
            self.cherrypy_dist = 'http://download.cherrypy.org/cherrypy/3.2.0/CherryPy-3.2.0.tar.gz'
            self.cherrypy_dir = 'CherryPy-3.2.0'
            cmdOutput = 'x86_64\n'#runCmd('uname -p')
        if cmdOutput == "i386\n" :
            self.mongo_dist = 'http://fastdl.mongodb.org/osx/mongodb-osx-i386-1.8.2.tgz'
            self.mongo_dir = 'mongodb-osx-i386-1.8.2'
        elif cmdOutput == 'x86_64\n' :
            self._log.info('Using osx x86_64')
            self.mongo_dist = 'http://fastdl.mongodb.org/osx/mongodb-osx-x86_64-1.8.2.tgz'
            self.mongo_dir = 'mongodb-osx-x86_64-1.8.2'            
        elif kernel == "Linux\n" :
            self.info('Using Linux kernel')
            self.openssl_dist = 'http://www.openssl.org/source/openssl-1.0.0d.tar.gz'
            self.openssl_dir = 'openssl-1.0.0d'
            self.cherrypy_dist = 'http://download.cherrypy.org/cherrypy/3.2.0/CherryPy-3.2.0.tar.gz'
            self.cherrypy_dir = 'CherryPy-3.2.0'
            cmdOutput = 'x86_64\n' #runCmd('uname -p')
            if cmdOutput == "i386\n" :
                self.mongo_dist = 'http://fastdl.mongodb.org/linux/mongodb-linux-i686-1.8.2.tgz'
                self.mongo_dir = 'mongodb-linux-i686-1.8.2'
            elif cmdOutput == "x86_64\n" :
                self.mongo_dist = 'http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-1.8.2.tgz'
                self.mongo_dir = 'mongodb-linux-x86_64-1.8.2'

    ## Execute shell based command
    # @param cmd the command string
    def runCmd(self, cmd, isShell = False):
        print("Executing command " + cmd)
        if isShell == True :
            p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE, shell = True)
        else :
            p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)

        std = p.communicate()
        self.returnCode = p.returncode
        if len(std[0]) > 0:
            self._log.debug('stdout: '+std[0])
        
        if p.returncode != 0:
            self._log.error('Command: '+cmd+' failed, status: '+str(p.returnCode)+' --- '+std[1])

        return std[0]


    ## Retrieve openssl distribution
    # Return code 0:  succesful installation,  return code 1:  unsuccessful
    def getopenssl(self) :
        install_dir = 'ssl'
        path_name = '/usr/local/ssl/bin/openssl'
        exitStat = 2
        # Retrieve distribution
        self.runCmd('wget ' + self.openssl_dist)
        if (self.returnCode != 0) :
            return self.returnCode
        self.runCmd('tar -xvf ' + self.openssl_dir + '.tar.gz')
        if (self.returnCode != 0) :
            return self.returnCode        
        cmd = 'mv -f ' + self.openssl_dir + ' ' + install_dir
        return self.returnCode

    ## Retrieve openssl distribution
    # Return code 0 - succesful installation, return code 1 unsucessful
    def getmongo(self):
        install_dir = 'mongodb'
        self.runCmd('wget ' + self.mongo_dist)
        if (self.returnCode != 0) :
            return self.returnCode
        self.runCmd('tar -xvf ' + self.mongo_dir + '.tgz')
        if (self.returnCode != 0) :
            return self.returnCode
        cmd = 'mv -f ' + mongo_dir + ' ' + install_dir
        self.runCmd(cmd)
        if (self.returnCode != 0) :
            return self.returnCode

        return 0

    ## Retrieve cherrypy distribution
    # Return code 0 - succesful installation, return code 1 unsuccesful
    def getcherrypy(self):
        install_dir = 'cherrypy'
        try : 
            import cherrypy
        except ImportError:
            print ("---RETRIEVING CHERRYPY DISTRIBUTION-----")
            self.runCmd('wget ' + self.cherrypy_dist)
            if (self.returnCode != 0) :
                return self.returnCode
            self.runCmd('tar -xvf ' + self.cherrypy_dir + '.tar.gz')
            cmd = 'mv -f ' + self.cherrypy_dir + ' ' + install_dir
            self.runCmd(cmd)
            if (self.returnCode != 0) :
                return self.returnCode

        try :
            import cherrypy
        except ImportError:
            print("unable to install cheryypy")
            return 1
        return 0

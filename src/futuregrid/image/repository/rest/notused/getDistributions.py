#!/usr/bin/python


#from optparse import OptionParser
import sys
import os
#from types import *
#import socket
from subprocess import *
import logging
import logging.handlers
#from xml.dom.minidom import Document,parse
path_name = None
logger = None
exitStat = 2
#dbserver = None

def main():

    log_filename = 'key.log'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(log_filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.basicConfig(level = logging.INFO)


#----------------------  Determining kernel ----------------------------------------
    kernel = runCmd('uname -s')
    if kernel == "Darwin\n" :
        logger.info("Using Darwin kernel ")
        openssl_dist = 'http://www.openssl.org/source/openssl-1.0.0d.tar.gz'
        openssl_dir = 'openssl-1.0.0d'
        cherrypy_dist = 'http://download.cherrypy.org/cherrypy/0.1/cherrypy-0.1.tar.gz'
        cherrypy_dir = 'cherrypy-0.1'
        cmdOutput = 'x86_64\n'#runCmd('uname -p')
        if cmdOutput == "i386\n" :
            mongo_dist = 'http://fastdl.mongodb.org/osx/mongodb-osx-i386-1.8.2.tgz'
            mongo_dir = 'mongodb-osx-i386-1.8.2'
        elif cmdOutput == 'x86_64\n' :
            logger.info('Using osx x86_64')
            mongo_dist = 'http://fastdl.mongodb.org/osx/mongodb-osx-x86_64-1.8.2.tgz'
            mongo_dir = 'mongodb-osx-x86_64-1.8.2'
    elif kernel == "Linux\n" :
        logger.info('Using Linux kernel')
        openssl_dist = 'http://www.openssl.org/source/openssl-1.0.0d.tar.gz'
        openssl_dir = 'openssl-1.0.0d'
        cherrypy_dist = 'http://download.cherrypy.org/cherrypy/0.1/cherrypy-0.1.tar.gz'
        cherrypy_dir = 'cherrypy-0.1'
        cmdOutput = 'x86_64\n' #runCmd('uname -p')
        if cmdOutput == "i386\n" :
            mongo_dist = 'http://fastdl.mongodb.org/linux/mongodb-linux-i686-1.8.2.tgz'
            mongo_dir = 'mongodb-linux-i686-1.8.2'
        elif cmdOutput == "x86_64\n" :
            mongo_dist = 'http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-1.8.2.tgz'
            mongo_dir = 'mongodb-linux-x86_64-1.8.2'



#------------------ INSTALLING OPEN SSL ----------------------------------

    install_dir = 'ssl'
    path_name = '/usr/local/ssl/bin/openssl'
    exitStat = 2
    print("openSSL")
    if not os.path.isfile(path_name) :
        if not os.path.isdir(install_dir) :
            # Retrieve distribution
            runCmd('wget ' + openssl_dist)
            runCmd('tar -xvf ' + openssl_dir + '.tar.gz')
            cmd = 'mv -f ' + openssl_dir + ' ' + install_dir
            runCmd(cmd)

#---------------------------------------------------------------------------

    """
#------------------- INSTALLING MONGODB -------------------------------------
    install_dir = 'mongodb'
    path_name = '/usr/local/mongodb/bin/mongod'
    print ("-----MONGODB-------")
    if ( not os.path.isfile(path_name)) :
        print("mongod does not exist in /usr/local")
        exitStat = 1
        if (not os.path.isdir('./mongodb')) :
            # Retrive distribution
            runCmd('wget ' + mongo_dist)
            runCmd('tar -xvf ' + mongo_dir + '.tgz')
            cmd = 'mv -f ' + mongo_dir + ' ' + install_dir
            runCmd(cmd)

    print("determine if pymongo exists")
    # Determining if pymongo exists if not then installing pymongo
    try :
        import pymongo
    except ImportError:
        # To use easy install on linux make sure you have the python-setuptools:   sudo apt-get install python-setuptools
        runCmd('sudo easy_install pymongo')

    try :
        import pymongo
    except ImportError:
        print("unable to install pymongo")
        sys.exit(0)
#------------------------------------------------------------------------------
    """
#----------------------- INSTALLING CHERRYPY ----------------------------------
    install_dir = 'cherrypy'
    try :
        import cherrypy
    except ImportError:
        runCmd('wget ' + cherrypy_dist)
        runCmd('tar -xvf ' + cherrpy_dir + '.tar.gz')
        cmd = 'mv -f ' + cherrypy_dir + ' ' + install_dir
        runCmd(cmd)
        cmd = 'cd ' + cherrypy_dir + ' ; ' + 'sudo python setup.py install'
        runCmd(cmd)

    try :
        import cherrypy
    except ImportError:
        print("unable to install cheryypy")
        sys.exit(0)
#------------------------------------------------------------------------------
    print(exitStat)
    print("Exiting , exit stat: ")
    sys.exit(exitStat)


def runCmd(cmd, isShell = False):
    cmdLog = logging.getLogger('exec')
    cmdLog.debug(cmd)
    print("Executing command " + cmd)
    if isShell == True :
        p = Popen(cmd.split(' '), stdout = PIPE, stderr = PIPE, shell = True)
    else :
        p = Popen(cmd.split(' '), stdout = PIPE, stderr = PIPE)

    std = p.communicate()
    if len(std[0]) > 0:
        cmdLog.debug('stdout: ' + std[0])
        cmdOutput = std[0]
        return std[0]
    #cmdLog.debug('stderr: '+std[1])                                                                                                                                      

    #cmdLog.debug('Ret status: '+str(p.returncode))                                                                                                                       
    if p.returncode != 0:
        cmdLog.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])
        sys.exit(p.returncode)


if __name__ == "__main__":
    main()
#END                                                                                                                                                                     

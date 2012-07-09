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
Command line front end for image generator
"""
__author__ = 'Javier Diaz, Andrew Younge'

import argparse
from types import *
import re
import logging
import logging.handlers
import glob
import random
import os
import sys
import socket, ssl
from subprocess import *
import textwrap
#from xml.dom.ext import *
#from xml.dom.minidom import Document, parse
import time
from getpass import getpass
import hashlib

from futuregrid.image.management.IMClientConf import IMClientConf
from futuregrid.utils import fgLog

class IMGenerate(object):
    def __init__(self, arch, OS, version, user, software, givenname, desc, getimg, passwd, verbose, printLogStdout, baseimage, scratch, size):
        super(IMGenerate, self).__init__()
        
        self.arch = arch
        self.OS = OS
        self.version = version
        self.user = user
        self.passwd = passwd
        self.software = software
        self.givenname = givenname
        self.desc = desc
        self.getimg = getimg
        self._verbose = verbose
        self.printLogStdout = printLogStdout
        self.baseimage=baseimage
        self.scratch=scratch
        self.size=size
        
        #Load Configuration from file
        self._genConf = IMClientConf()
        self._genConf.load_generationConfig()        
        self.serveraddr = self._genConf.getServeraddr()
        self.gen_port = self._genConf.getGenPort()
        
        self._ca_certs = self._genConf.getCaCertsGen()
        self._certfile = self._genConf.getCertFileGen()
        self._keyfile = self._genConf.getKeyFileGen()
        
        self._log = fgLog.fgLog(self._genConf.getLogFileGen(), self._genConf.getLogLevelGen(), "GenerateClient", printLogStdout)

    def setArch(self, arch):
        self.arch = arch
    def setOs(self, os):
        self.OS = os
    def setVersion(self, version):
        self.version = version
    def setSoftware(self, software):
        self.software = software
    def setGivenname(self, givenname):
        self.givenname = givenname        
    def setDesc(self, desc):
        self.desc = desc
    def setGetimg(self, getimg):
        self.getimg = getimg
    def setDebug(self, printLogStdout):
        self.printLogStdout = printLogStdout
    def setBaseImage(self, baseimage):
        self.baseimage=baseimage
    def setScratch(self, scratch):
        self.scratch=scratch
    def setSize(self, size):
        self.size=size

    def check_auth(self, socket_conn, checkauthstat):
        endloop = False
        passed = False
        while not endloop:
            ret = socket_conn.read(1024)
            if (ret == "OK"):
                if self._verbose:
                    print "Authentication OK. Your image request is being processed"
                self._log.debug("Authentication OK")
                endloop = True
                passed = True
            elif (ret == "TryAuthAgain"):
                msg = "ERROR: Permission denied, please try again. User is " + self.user                    
                self._log.error(msg)
                if self._verbose:
                    print msg                            
                m = hashlib.md5()
                m.update(getpass())
                passwd = m.hexdigest()
                socket_conn.write(passwd)
                self.passwd = passwd
            elif ret == "NoActive":
                msg="ERROR: The status of the user "+ self.user + " is not active"
                checkauthstat.append(str(msg))
                self._log.error(msg)
                #if self._verbose:
                #    print msg            
                endloop = True
                passed = False          
            elif ret == "NoUser":
                msg="ERROR: User "+ self.user + " does not exist"
                checkauthstat.append(str(msg))
                self._log.error(msg)
                #if self._verbose:
                #    print msg + " WE"  
                endloop = True
                passed = False
            else:                
                self._log.error(str(ret))
                #if self._verbose:
                #    print ret
                checkauthstat.append(str(ret))
                endloop = True
                passed = False
        return passed

    def generate(self):
        start_all = time.time()
        #generate string with options separated by | character
        output = None
        checkauthstat = []
        #params[0] is user
        #params[1] is operating system
        #params[2] is version
        #params[3] is arch
        #params[4] is software
        #params[5] is givenname
        #params[6] is the description
        #params[7] is to retrieve the image or to upload in the repo (true or false, respectively)
        #params[8] is the user password
        #params[9] is the type of password
        #params[10] is to generate only a base image
        #params[11] is to do not use a cached based image
               
        
        options = str(self.user) + "|" + str(self.OS) + "|" + str(self.version) + "|" + str(self.arch) + "|" + \
                str(self.software) + "|" + str(self.givenname) + "|" + str(self.desc) + "|" + str(self.getimg) + \
                "|" + str(self.passwd) + "|ldappassmd5|" + str(self.baseimage) + "|"+ str(self.scratch) + "|" + str(self.size)
        
        #self._log.debug("string to send: "+options)
        
        #Notify xCAT deployment to finish the job
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            genServer = ssl.wrap_socket(s,
                                        ca_certs=self._ca_certs,
                                        certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            self._log.debug("Connecting server: " + self.serveraddr + ":" + str(self.gen_port))
            if self._verbose:
                print "Connecting server: " + self.serveraddr + ":" + str(self.gen_port)
            genServer.connect((self.serveraddr, self.gen_port))            
        except ssl.SSLError:
            self._log.error("CANNOT establish SSL connection. EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish SSL connection. EXIT"

        genServer.write(options)
        #check if the server received all parameters
        if self._verbose:
            print "Your image request is in the queue to be processed after authentication"
                
        if self.check_auth(genServer, checkauthstat):
            if self._verbose:
                print "Generating the image"
            ret = genServer.read(2048)
            
            if (re.search('^ERROR', ret)):
                self._log.error('The image has not been generated properly. Exit error:' + ret)
                if self._verbose:
                    print "ERROR: The image has not been generated properly. Exit error:" + ret    
            else:
                self._log.debug("Returned string: " + str(ret))
                
                if self.getimg:            
                    output = self._retrieveImg(ret, "./")                    
                    genServer.write('end')
                else:
                    
                    if (re.search('^ERROR', ret)):
                        self._log.error('The image has not been generated properly. Exit error:' + ret)
                        if self._verbose:
                            print "ERROR: The image has not been generated properly. Exit error:" + ret
                    else:
                        self._log.debug("The image ID is: " + str(ret))
                        output = str(ret)
        else:       
            self._log.error(str(checkauthstat[0]))
            if self._verbose:
                print checkauthstat[0]
            return
        
        end_all = time.time()
        self._log.info('TIME walltime image generate client:' + str(end_all - start_all))
        
        #server return addr of the img and metafile compressed in a tgz, imgId or None if error
        return output
    """
    ############################################################
    # _rExec
    ############################################################
    def _rExec(self, cmdexec):
    
        #TODO: do we want to use the .format statement from python to make code more readable?
        #Set up random string    
        random.seed()
        randid = str(random.getrandbits(32))
        
        cmdssh = "ssh " + self.serveraddr
        tmpFile = "/tmp/" + str(time()) + str(randid)
        #print tmpFile
        cmdexec = cmdexec + " > " + tmpFile
        cmd = cmdssh + cmdexec
    
        self._log.debug(str(cmd))
    
        stat = os.system(cmd)
        if (str(stat) != "0"):
            #print stat
            self._log.debug(str(stat))
        f = open(tmpFile, "r")
        outputs = f.readlines()
        f.close()
        os.system("rm -f " + tmpFile)
        #output = ""
        #for line in outputs:
        #    output += line.strip()
        #print outputs
        return outputs
    """
    ############################################################
    # _retrieveImg
    ############################################################
    def _retrieveImg(self, dir, dest):
        imgURI = self.serveraddr + ":" + dir
        imgIds = imgURI.split("/")
        imgId = imgIds[len(imgIds) - 1]
    
        cmdscp = ""
        if self._verbose:            
            cmdscp = "scp " + self.user + "@" + imgURI + " " + dest
        else:#this is the case where another application call it. So no password or passphrase is allowed
            cmdscp = "scp -q -oBatchMode=yes " + self.user + "@" + imgURI + " " + dest
        output = ""
        try:
            if self._verbose:
                print 'Retrieving image. You may be asked for ssh/passphrase password'
            self._log.debug(cmdscp)
            stat = os.system(cmdscp)
            stat = 0
            if (stat == 0):
                output = dest + "/" + imgId
            else:
                self._log.error("Error retrieving the image. Exit status " + str(stat))
                if self._verbose:
                    print "Error retrieving the image. Exit status " + str(stat)
                output = None
                #remove the temporal file
        except os.error:
            self._log.error("Error, The image cannot be retieved" + str(sys.exc_info()))
            if self._verbose:
                print "Error, The image cannot be retieved" + str(sys.exc_info())
            output = None
    
        return output

def extra_help():
   msg = "Useful information about the software. Currently, we do not parse the packages names provided within the -s/--software option" +\
         "Therefore, if some package name is wrong, it won't be installed. Here we provide a list of useful packages names from the official repositories: \n" +\
         "CentOS: mpich2, python26, java-1.6.0-openjdk. More packages names can be found in http://mirror.centos.org/ \n" +\
         "Ubuntu: mpich2, openjdk-6-jre, openjdk-6-jdk. More packages names can be found in http://packages.ubuntu.com/ \n\n" +\
         "FutureGrid Performance packages (currently only for CentOS 5): fg-intel-compilers, intel-compilerpro-common, " +\
         "intel-compilerpro-devel, intel-compilerproc, intel-compilerproc-common, intel-compilerproc-devel " +\
         "intel-compilerprof, intel-compilerprof-common, intel-compilerprof-devel, intel-openmp, intel-openmp-devel, openmpi-intel"
   return msg
   
def main():

    #Default params
    base_os = ""
    spacer = "-"
    default_ubuntu = "maverick"
    default_debian = "lenny"
    default_rhel = "5.5"
    default_centos = "5.6"
    default_fedora = "13"
    #kernel = "2.6.27.21-0.1-xen"

    #ubuntu-distro = ['lucid', 'karmic', 'jaunty']
    #debian-distro = ['squeeze', 'lenny', 'etch']
    #rhel-distro = ['5.5', '5.4', '4.8']
    #fedora-distro = ['14','12']

    parser = argparse.ArgumentParser(prog="fg-generate", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Generation Help",
                                     epilog=textwrap.dedent(extra_help()))    
    parser.add_argument('-u', '--user', dest='user', required=True, help='FutureGrid User name')
    parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
    parser.add_argument("-o", "--os", dest="OS", required=True, metavar='OSName', help="Specify the desired Operating System for the new image. Currently, Centos and Ubuntu are supported")
    parser.add_argument("-v", "--version", dest="version", metavar='OSversion', help="Operating System version. In the case of Centos, it can be 5 or 6. In the case of Ubuntu, it can be karmic(9.10), lucid(10.04), maverick(10.10), natty (11.04)")
    parser.add_argument("-a", "--arch", dest="arch", metavar='arch', help="Destination hardware architecture")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("--baseimage", dest="baseimage", default=False, action="store_true", help="Generate a Base Image that will be used to generate other images. In this way, the image generation process will be faster.")    
    group1.add_argument("-s", "--software", dest="software", metavar='software', help="List of software packages, separated by commas, that will be installed in the image.")
    parser.add_argument("--scratch", dest="scratch", default=False, action="store_true", help="Generate the image from scratch without using any Base Image from the repository.")
    parser.add_argument("-n", "--name", dest="givenname", metavar='givenname', help="Desired recognizable name of the image")
    parser.add_argument("-e", "--description", dest="desc", metavar='description', help="Short description of the image and its purpose")
    parser.add_argument("-g", "--getimg", dest="getimg", default=False, action="store_true", help="Retrieve the image instead of uploading to the image repository")
    parser.add_argument("-z", "--size", default=1.5, dest="size", help="Specify size of the Image in GigaBytes. The size must be large enough to install all the software required. The default and minimum size is 1.5GB, which is enough for most cases.")
    parser.add_argument('--nopasswd', dest='nopasswd', action="store_true", default=False, help='If this option is used, the password is not requested. This is intended for systems daemons like Inca')
    
    args = parser.parse_args()

    print 'Image generator client...'
    
    verbose = True

    if args.nopasswd == False:    
        print "Please insert the password for the user " + args.user + ""
        m = hashlib.md5()
        m.update(getpass())
        passwd = m.hexdigest()
    else:        
        passwd = "None"
    
    if args.size.isdigit():
        if args.size < 1.5:
            args.size=1.5
    else:
        print "The size has to be a number"
        sys.exit(1)
    
    arch = "x86_64" #Default to 64-bit

    #Parse arch command line arg
    if args.arch != None:
        if args.arch == "i386" or args.arch == "i686":
            arch = "i386"
        elif args.arch == "amd64" or args.arch == "x86_64":
            arch = "x86_64"
        else:
            print "ERROR: Incorrect architecture type specified (i386|x86_64)"
            sys.exit(1)

    print 'Selected Architecture: ' + arch

    # Build the image
    version = ""
    #Parse OS and version command line args
    OS = ""
    if args.OS == "Ubuntu" or args.OS == "ubuntu":
        OS = "ubuntu"
        supported_versions = ["karmic", "lucid", "maverick", "natty"]
        if type(args.version) is NoneType:
            version = default_ubuntu
        elif args.version == "9.10" or args.version == "karmic":
            version = "karmic"
        elif args.version == "10.04" or args.version == "lucid":
            version = "lucid"
        elif args.version == "10.10" or args.version == "maverick":
            version = "maverick"
        elif args.version == "11.04" or args.version == "natty":
            version = "natty"
        elif args.version == "11.10" or args.version == "oneiric":
            version = "oneiric"
        elif args.version == "12.04" or args.version == "precise":
            version = "precise"
        else:
            print "ERROR: Incorrect OS version specified. Supported OS version for " + OS + " are " + str(supported_versions)
            sys.exit(1)
    #elif args.OS == "Debian" or args.OS == "debian":
    #    OS = "debian"
    #    version = default_debian
    #elif args.OS == "Redhat" or args.OS == "redhat" or args.OS == "rhel":
    #    OS = "rhel"
    #    version = default_rhel
    elif args.OS == "CentOS" or args.OS == "CentOS" or args.OS == "centos":
        OS = "centos"        
        supported_versions = ["5", "6"]
        if type(args.version) is NoneType:
            version = default_centos            
        elif re.search("^5", str(args.version)):
            version = "5"
        elif re.search("^6", str(args.version)):
            version = "6"
        else:
            print "ERROR: Incorrect OS version specified. Supported OS version for " + OS + " are " + str(supported_versions)
            sys.exit(1)
            
    #elif args.OS == "Fedora" or args.OS == "fedora":
    #    OS = "fedora"
    #    version = default_fedora
    else:
        print "ERROR: Incorrect OS type specified. Currently only Centos and Ubuntu are supported"
        sys.exit(1)
        
        
    imgen = IMGenerate(arch, OS, version, args.user, args.software, args.givenname, args.desc, args.getimg, passwd, verbose, args.debug, args.baseimage, args.scratch, args.size)
    status = imgen.generate()
    
    if status != None:
        if args.getimg:
            print "The image is located in " + str(status)
        else:
            print "Your image has be uploaded in the repository with ID=" + str(status)
        if not args.baseimage:
            print '\n The image and the manifest generated are packaged in a tgz file.' + \
              '\n Please be aware that this FutureGrid image does not have kernel and fstab. Thus, ' + \
              'it is not built for any infrastructure. To register the new image, use the IMRegister command.'
        else:
            print '\n The image and the manifest generated are packaged in a tgz file.' + \
              '\n Please be aware that this Base Image is not ready for registration. This is intended to be used for generating other images'


if __name__ == "__main__":
    main()





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
Command line front end for image registration
"""

__author__ = 'Javier Diaz, Andrew Younge'

import argparse
import sys
import os
from types import *
import socket, ssl
from subprocess import *
import logging
from xml.dom.minidom import Document, parse
import re
from getpass import getpass
import hashlib
import time
import boto.ec2
import boto
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from random import randrange

from futuregrid.image.management.IMClientConf import IMClientConf
from futuregrid.image.management.IMEc2Environ import IMEc2Environ
from futuregrid.utils import fgLog 
from futuregrid.image.repository.client.IRServiceProxy import IRServiceProxy
    
class IMRegister(object):
    ############################################################
    # __init__
    ############################################################
    def __init__(self, kernel, user, passwd, verbose, printLogStdout):
        super(IMRegister, self).__init__()

        
        self.kernel = kernel
        self.user = user
        self.passwd = passwd
        self._verbose = verbose
        self.printLogStdout = printLogStdout
        
        self.machine = ""  #(india or minicluster or ...)
        self.loginmachine = ""
        self.shareddirserver = "" 
        
        #Load Configuration from file
        self._registerConf = IMClientConf()
        self._registerConf.load_registerConfig()        
        self._xcat_port = self._registerConf.getXcatPort()
        self._moab_port = self._registerConf.getMoabPort()
        self._http_server = self._registerConf.getHttpServer()        
        self._ca_certs = self._registerConf.getCaCertsDep()
        self._certfile = self._registerConf.getCertFileDep()
        self._keyfile = self._registerConf.getKeyFileDep()
        self._tempdir = self._registerConf.getTempDirRegister()

        self.iaasmachine = self._registerConf.getIaasServerAddr()
        self._iaas_port = self._registerConf.getIaasPort()
        
        self._log = fgLog.fgLog(self._registerConf.getLogFileRegister(), self._registerConf.getLogLevelRegister(), "RegisterClient", printLogStdout)
        

    def setKernel(self, kernel):
        self.kernel = kernel
    def setDebug(self, printLogStdout):
        self.printLogStdout = printLogStdout
    def setVerbose(self, verbose):
        self._verbose = verbose
    

    def check_auth(self, socket_conn, checkauthstat):
        endloop = False
        passed = False
        while not endloop:
            ret = socket_conn.read(1024)
            if (ret == "OK"):
                if self._verbose:
                    print "Authentication OK. Your request is being processed \n"
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
                msg = "ERROR: The status of the user " + self.user + " is not active"
                checkauthstat.append(str(msg))
                self._log.error(msg)
                #if self._verbose:
                #    print msg            
                endloop = True
                passed = False          
            elif ret == "NoUser":
                msg = "ERROR: User " + self.user + " does not exist"
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
    
    def iaas_justregister(self, machinename, image, image_source, ramdisk, iaas_type, varfile, wait):
        """
        This method gets the image and registers it in the cloud infrastructure.
        """
        start_all = time.time()
        
        auxdir = str(randrange(999999999999999999999999))
        localtempdir = self._tempdir + "/" + auxdir + "_0"
        while os.path.isdir(localtempdir):
            auxdir = str(randrange(999999999999999999999999))
            localtempdir = self._tempdir + "/" + auxdir + "_0"
        cmd = 'mkdir -p ' + localtempdir
        self.runCmd(cmd)
        self.runCmd("chmod 777 " + localtempdir)
        
        stat = 0
        uncompress = False
        delorigin = True
        if image_source == "disk":
            delorigin = False
            extension = os.path.splitext(image)[1].strip()            
            if extension == ".tgz" or extension == ".gz":
                uncompress = True
                imagefile = image
            else:                
                realnameimg = image                             
        else:            
            verbose = True
            printLogStdout = False
            reposervice = IRServiceProxy(verbose, printLogStdout)
            #GET IMAGE from repo
            if not reposervice.connection():
                msg = "ERROR: Connection with the Image Repository failed"
                self._log.error(msg)
                if self._verbose:
                    print msg
                stat = 1
            else:
                print "Retrieving image from repository"
                imagefile = reposervice.get(self.user, self.passwd, self.user, "img", image, localtempdir)                  
                if imagefile == None:
                    msg = "ERROR: Cannot get access to the image with imgId " + str(image)
                    self._log.error(msg)
                    if self._verbose:
                        print msg
                    self.runCmd("rm -rf " + localtempdir)
                    stat = 1
                else:
                    extension = os.path.splitext(imagefile)[1].strip()            
                    if extension == ".tgz" or extension == ".gz":      
                        uncompress = True
                    else:
                        realnameimg = imagefile
                    reposervice.disconnect()
        if uncompress:
            #uncompres
            if self._verbose:
                print "Uncompressing Image"
            cmd = "tar xvfz " + imagefile + " -C " + localtempdir                        
            p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
            std = p.communicate()                
            if len(std[0]) > 0:
                realnameimg = localtempdir + "/" + std[0].split("\n")[0].strip().split(".")[0] + ".img"                        
            if p.returncode != 0:
                if self._verbose:
                    msg = 'ERROR: Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1]                    
                    self._log.error(msg)
                    if self._verbose:
                        print msg
                self.runCmd("rm -rf " + localtempdir)
                stat = 1
                
            if image_source != "disk":
                cmd = 'rm -f ' + imagefile
                status = self.runCmd(cmd)       
                            
        if stat == 0:           

            start = time.time()
            operatingsystem = None  # this is not used
            getimg = False          # this is not used
            output = eval("self." + iaas_type + "_method(\"" + str(realnameimg) + "\",\"" + str(self.kernel) + "\",\"" + str(ramdisk) + "\",\"" + 
                            str(operatingsystem) + "\",\"" + str(machinename) + "\",\"" + str(varfile) + "\",\"" + str(getimg) + "\",\"" + str(wait) + "\",\"" + 
                            str(delorigin) + "\")")
            end = time.time()
            self._log.info('TIME uploading image to cloud framework:' + str(end - start))
            
            #wait until image is in available status
            if wait:
                self.wait_available(iaas_type, varfile, output)                            
        
            end_all = time.time()
            self._log.info('TIME walltime image register cloud:' + str(end_all - start_all))
            
            if self._verbose:
                print "Image Registered successfully"
                        
            self.runCmd("rm -rf " + localtempdir)
            
            return output
        else:
            return
            



    def iaas_generic(self, machinename, image, image_source, iaas_type, varfile, getimg, ldap, wait):
        """
        This method calls the server to adapt the image and then it register the image in the cloud infrastructure.
        """
        start_all = time.time()
        checkauthstat = []     
        if self._verbose:
            print 'Connecting to IaaS server'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            iaasServer = ssl.wrap_socket(s,
                                        ca_certs=self._ca_certs,
                                        certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            
            iaasServer.connect((self.iaasmachine, self._iaas_port))
            
            msg = str(image) + ',' + str(image_source) + ',' + str(machinename) + "," + str(iaas_type) + ',' + str(self.kernel) + ',' + str(self.user) + \
                  ',' + str(self.passwd) + ",ldappassmd5" + ',' + str(ldap) 
            #self._log.debug('Sending message: ' + msg)
            
            iaasServer.write(msg)
            
            if self._verbose:
                print "Your request is in the queue to be processed after authentication"
            
            if self.check_auth(iaasServer, checkauthstat):                                
                if image == "kernels":
                    start = time.time()
                    kernelslist = iaasServer.read(4096)
                    self._log.debug("Getting " + iaas_type + " kernel list:" + kernelslist)        
                    end = time.time()
                    self._log.info('TIME get list of kernels:' + str(end - start))            
                    return kernelslist
                elif image == "infosites":
                    start = time.time()
                    infosites = iaasServer.read(4096)
                    self._log.debug("Getting services information of supported sites:" + infosites)        
                    end = time.time()
                    self._log.info('TIME get Cloud info sites:' + str(end - start))            
                    return infosites
                else:
                    start = time.time()
                    if self._verbose:
                        print "Customizing image for the selected cloud framework: " + iaas_type
                    
                    if image_source == "disk":
                        ret = iaasServer.read(2048)
                        if re.search("^ERROR", ret):
                            self._log.error(ret)
                            if self._verbose:
                                print ret
                            return
                        cmd = ''
                        status = ''
                        if (self.iaasmachine == "localhost" or self.iaasmachine == "127.0.0.1"):
                            self._log.info('Copying the image to the right directory')
                            cmd = 'cp ' + image + ' ' + ret                        
                            status = self.runCmd(cmd)
                        else:                    
                            self._log.info('Uploading image.')
                            if self._verbose:
                                print 'Uploading image. You may be asked for ssh/passphrase password'
                                cmd = 'scp ' + image + ' ' + self.user + '@' + self.iaasmachine + ':' + ret
                            else:#this is the case where another application call it. So no password or passphrase is allowed              
                                cmd = 'scp -q -oBatchMode=yes ' + image + ' ' + self.user + '@' + self.iaasmachine + ':' + ret
                            status = self.runCmd(cmd)
                        
                        if status == 0:
                            iaasServer.write('OK,' + os.path.split(image)[1].strip())
                        else:                    
                            iaasServer.write('ERROR from client, ')
                            self._log.error("ERROR sending image to server via scp. EXIT.")
                            if self._verbose:
                                print "ERROR sending image to server via scp. EXIT."
                            return                        
                                             
                    #print msg
                    ret = iaasServer.read(1024)
                    
                    end = time.time()
                    self._log.info('TIME customize image in server side for an iaas:' + str(end - start))
                    
                    if (re.search('^ERROR', ret)):
                        self._log.error('The image has not been registered properly. Exit error:' + ret)
                        if self._verbose:
                            print "ERROR: The image has not been registered properly. Exit error:" + ret    
                    else:                           
                        results = ret.split(",")
                        if len(results) == 4:
                            imgURIinServer = results[0].strip()
                            eki = results[1].strip()
                            eri = results[2].strip()
                            operatingsystem = results[3].strip()
                            #imagebackpath = retrieve   
                            localpath = "./"
                            
                            start = time.time()
                                                    
                            imagebackpath = self._retrieveImg(imgURIinServer, localpath)
                            
                            end = time.time()
                            self._log.info('TIME retrieve image from server side:' + str(end - start))
                            #if we want to introduce retries we need to put next line after checking that the image is actually here
                            iaasServer.write('OK')                        
                            if imagebackpath != None:        
                                                                
                                start = time.time()
                                delorigin = True  # This is always true here because we have to delete the temporal image.
                                output = eval("self." + iaas_type + "_method(\"" + str(imagebackpath) + "\",\"" + str(eki) + "\",\"" + str(eri) + "\",\"" + 
                                      str(operatingsystem) + "\",\"" + str(machinename) + "\",\"" + str(varfile) + "\",\"" + str(getimg) + "\",\"" + str(wait) + "\",\"" + 
                                      str(delorigin) + "\")")
                                
                                end = time.time()
                                self._log.info('TIME uploading image to cloud framework:' + str(end - start))
                                
                                #wait until image is in available status
                                if wait:
                                    self.wait_available(iaas_type, varfile, output)                            
                        
                                end_all = time.time()
                                self._log.info('TIME walltime image register cloud:' + str(end_all - start_all))
                                
                                if self._verbose:
                                    print "Image Registered successfully"
                                
                                return output
                            else:
                                self._log.error("CANNOT retrieve the image from server. EXIT.")
                                if self._verbose:
                                    print "ERROR: CANNOT retrieve the image from server. EXIT."
                        else:
                            self._log.error("Incorrect reply from server. EXIT.")
                            if self._verbose:
                                print "ERROR: Incorrect reply from server. EXIT."
                                    
            else:       
                self._log.error(str(checkauthstat[0]))
                if self._verbose:
                    print checkauthstat[0]
                return
                            
        except ssl.SSLError:
            self._log.error("CANNOT establish SSL connection. EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish SSL connection."
        except socket.error:
            self._log.error("CANNOT establish connection with IMRegisterServerIaas service. EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish connection with IMRegisterServerIaas service."
    
    def openstack_environ(self, varfile):
        openstackEnv = IMEc2Environ()
        
        nova_key_dir = os.path.dirname(varfile)            
        if nova_key_dir.strip() == "":
            nova_key_dir = "."
        os.environ["NOVA_KEY_DIR"] = nova_key_dir
        
        #read variables
        f = open(varfile, 'r')
        for line in f:
            if re.search("^export ", line):
                line = line.split()[1]                    
                parts = line.split("=")
                #parts[0] is the variable name
                #parts[1] is the value
                parts[0] = parts[0].strip()
                value = ""
                for i in range(1, len(parts)):
                    parts[i] = parts[i].strip()
                    parts[i] = os.path.expanduser(os.path.expandvars(parts[i]))                    
                    value += parts[i] + "="
                value = value.rstrip("=")
                value = value.strip('"')
                value = value.strip("'") 
                os.environ[parts[0]] = value
        f.close()
             
        openstackEnv.setEc2_url(os.getenv("EC2_URL"))
        openstackEnv.setS3_url(os.getenv("S3_URL"))
        
        path = "/services/Cloud"
        region = "nova"       
        openstackEnv.setPath(path) 
        openstackEnv.setRegion(region)
        
        try:
            openstackEnv.setEc2_port(int(openstackEnv.getEc2_url().lstrip("http://").split(":")[1].split("/")[0]))
            openstackEnv.setS3_port(int(openstackEnv.getS3_url().lstrip("http://").split(":")[1].split("/")[0]))
        except:
            msg = "ERROR: Obtaining Ec2 or S3 port. " + str(sys.exc_info())
            self._log.error(msg)            
            return msg
        
        openstackEnv.setS3id(str(os.getenv("EC2_ACCESS_KEY")))
        openstackEnv.setS3key(str(os.getenv("EC2_SECRET_KEY")))
                         
        return openstackEnv
        
        
    def euca_environ(self, varfile):
        eucaEnv = IMEc2Environ()
               
        euca_key_dir = os.path.dirname(varfile)            
        if euca_key_dir.strip() == "":
            euca_key_dir = "."
        os.environ["EUCA_KEY_DIR"] = euca_key_dir
                    
        #read variables
        f = open(varfile, 'r')
        for line in f:
            if re.search("^export ", line):
                line = line.split()[1]                    
                parts = line.split("=")
                #parts[0] is the variable name
                #parts[1] is the value
                parts[0] = parts[0].strip()
                value = ""
                for i in range(1, len(parts)):
                    parts[i] = parts[i].strip()
                    parts[i] = os.path.expanduser(os.path.expandvars(parts[i]))                    
                    value += parts[i] + "="
                value = value.rstrip("=")
                value = value.strip('"')
                value = value.strip("'") 
                os.environ[parts[0]] = value
        f.close()
            
           
        eucaEnv.setEc2_url(os.getenv("EC2_URL"))
        eucaEnv.setS3_url(os.getenv("S3_URL"))
        
        path = "/services/Eucalyptus"
        region = "eucalyptus"        
        eucaEnv.setPath(path) 
        eucaEnv.setRegion(region)
        
        try:
            eucaEnv.setEc2_port(int(eucaEnv.getEc2_url().lstrip("http://").split(":")[1].split("/")[0]))
            eucaEnv.setS3_port(int(eucaEnv.getS3_url().lstrip("http://").split(":")[1].split("/")[0]))
        except:
            msg = "ERROR: Obtaining Ec2 or S3 port. " + str(sys.exc_info())
            self._log.error(msg)            
            return msg
        eucaEnv.setS3id(str(os.getenv("EC2_ACCESS_KEY")))
        eucaEnv.setS3key(str(os.getenv("EC2_SECRET_KEY")))
                         
        return eucaEnv
    
    def nimbus_environ(self, varfile):
        
        nimbusEnv = IMEc2Environ()
        ec2_address = ""
        s3_address = ""
        
        nimbus_key_dir = os.path.dirname(varfile)            
        if nimbus_key_dir.strip() == "":
            nimbus_key_dir = "."
        try:
            #read variables
            f = open(varfile, 'r')
            for line in f:
                line = line.strip()
                if re.search("^vws.factory=", line):                        
                    parts = line.split("=")[1].split(":")               
                    ec2_address = parts[0].strip()
                    #int(parts[1].strip())
                    nimbusEnv.setEc2_port(8444)#hardcoded because it is not in the config file
                elif re.search("^vws.repository=", line):     
                    parts = line.split("=")[1].split(":")               
                    s3_address = parts[0].strip()                    
                    nimbusEnv.setS3_port(int(parts[1].strip())) 
                elif re.search("^vws.repository.s3bucket=", line):
                    nimbusEnv.setBucket(line.split("=")[1])
                elif re.search("^vws.repository.s3basekey=", line):
                    nimbusEnv.setBase_key(line.split("=")[1])
                elif re.search("^vws.repository.s3id=", line):
                    nimbusEnv.setS3id(line.split("=")[1])
                elif re.search("^vws.repository.s3key=", line):
                    nimbusEnv.setS3key(line.split("=")[1])
                elif re.search("^vws.repository.canonicalid=", line):
                    nimbusEnv.setCannonicalId(line.split("=")[1])
            f.close()
        except:            
            msg = "ERROR: Reading Configuration File" + str(sys.exc_info())
            self._log.error(msg)            
            return msg
        

        ec2_url = "https://" + ec2_address + ":" + str(nimbusEnv.getEc2_port())
        os.environ["EC2_URL"] = ec2_url
        s3_url = "http://" + s3_address + ":" + str(nimbusEnv.getS3_port())
        os.environ["S3_URL"] = s3_url
        nimbusEnv.setEc2_url(ec2_url)
        nimbusEnv.setS3_url(s3_url)
            
        nimbusEnv.setPath("") 
        nimbusEnv.setRegion("nimbus")
        
        os.environ["EC2_ACCESS_KEY"] = nimbusEnv.getS3id()
        os.environ["EC2_SECRET_KEY"] = nimbusEnv.getS3key()
        
        return nimbusEnv
  
    def ec2connection(self, iaas_type, varfile):
        connEnv = None     
        secure = False      
        
        if iaas_type == "openstack":
            connEnv = self.openstack_environ(varfile)
            secure = False                    
        elif iaas_type == "euca":
            connEnv = self.euca_environ(varfile)
            secure = False
        elif iaas_type == "nimbus":
            connEnv = self.nimbus_environ(varfile)
            secure = True
        
        if not isinstance(connEnv, IMEc2Environ):
            msg = "ERROR: Parsing Configuration File. " + str(connEnv)
            self._log.error(msg)                        
            return msg
           
        endpoint = connEnv.getEc2_url().lstrip("http://").split(":")[0]
        
        self._log.debug("Getting Region")
        region = None        
        try:  
            region = boto.ec2.regioninfo.RegionInfo(name=connEnv.getRegion(), endpoint=endpoint)
        except:
            msg = "ERROR: getting region information " + str(sys.exc_info())
            self._log.error(msg)                        
            return msg
        
        self._log.debug("Connecting EC2")
        connection = None        
        try:
            connection = boto.connect_ec2(connEnv.getS3id(), connEnv.getS3key(), is_secure=secure, region=region, port=connEnv.getEc2_port(), path=connEnv.getPath())
        except:
            msg = "ERROR:connecting to EC2 interface. " + str(sys.exc_info())
            self._log.error(msg)                        
            return msg
        
        return connection
        
    def cloudlist(self, machinename, iaas_type, varfile):
        
        connection = self.ec2connection(iaas_type, varfile)
        
        if not isinstance(connection, boto.ec2.connection.EC2Connection):
            msg = "ERROR: Connecting Ec2. " + str(connection)
            self._log.error(msg)                        
            return msg
        
        self._log.debug("Getting Image List")
        images = None
        try:
            images = connection.get_all_images()     
            #print images
        except:
            msg = "ERROR: getting image list " + str(sys.exc_info())
            self._log.error(msg)            
            return msg
        imagelist = []
        for i in images:
            imagelist.append(str(i).split(":")[1] + "  -  " + str(i.location))
        
        return imagelist
    
    def cloudremove(self, machinename, iaas_type, varfile, removeimg):
        
        connection = self.ec2connection(iaas_type, varfile)
        
        if not isinstance(connection, boto.ec2.connection.EC2Connection):
            msg = "ERROR: Connecting Ec2. " + str(connection)
            self._log.error(msg)                        
            return msg
        
        self._log.debug("Removing image " + removeimg)
        output = False
        try:
            output = connection.deregister_image(removeimg)     
            #print images
        except:
            msg = "ERROR: removing image " + str(sys.exc_info())
            self._log.error(msg)            
            return msg
                
        return output
    
    def wait_available(self, iaas_type, varfile, imageId):
        #Verify that the image is in available status        
        start = time.time()
        available = False
        retry = 0
        fails = 0
        max_retry = 100 #wait around 15 minutes. plus the time it takes to execute the command, that in openstack can be several seconds 
        max_fails = 5
        stat = 0
        if self._verbose:
            print "Verify that the requested image is in available status or wait until it is available"
        
        connection = self.ec2connection(iaas_type, varfile)
        
        while not available and retry < max_retry and fails < max_fails:
            
            try:
                image = connection.get_image(imageId)
                if str(image.state) == "available":
                    available = True
                else:
                    retry += 1
                    time.sleep(10)                
            except:
                fails += 1
            
        if stat == 1:
            msg = "ERROR: checking image status"
            self._log.error(msg)            
            return msg
        elif not available:
            msg = "ERROR: Timeout, image is not in available status"
            self._log.error(msg)            
            return msg

        end = time.time()
        self._log.info('TIME Image available:' + str(end - start))    
    
    def nimbus_method(self, imagebackpath, eki, eri, operatingsystem, machinename, varfile, getimg, wait, delorigin):
        if not eval(getimg):
            nimbusEnv = self.nimbus_environ(varfile)
            if isinstance(nimbusEnv, IMEc2Environ):
                cf = OrdinaryCallingFormat()
                try:
                    s3conn = S3Connection(nimbusEnv.getS3id(), nimbusEnv.getS3key(), host=nimbusEnv.getS3_url().lstrip("http://").split(":")[0],
                                          port=nimbusEnv.getS3_port(), is_secure=False, calling_format=cf)
                except:
                    msg = "ERROR:connecting to S3 interface. " + str(sys.exc_info())
                    self._log.error(msg)                        
                    return msg
                try:
                    bucket = s3conn.get_bucket(nimbusEnv.getBucket())
                    k = Key(bucket)
                    k.key = nimbusEnv.getBase_key() + "/" + nimbusEnv.getCannonicalId() + "/" + os.path.basename(imagebackpath)       
                    if self._verbose:
                        print "Uploading Image..."
                    k.set_contents_from_filename(imagebackpath)
                    
                    if delorigin == "True":                    
                        cmd = "rm -f " + imagebackpath
                        os.system(cmd)
                except:
                    msg = "ERROR:uploading image. " + str(sys.exc_info())
                    self._log.error(msg)                        
                    return msg
                
                print "Your image has been registered on Nimbus. The image id is the name of the image: " + os.path.basename(imagebackpath) + " \n" + \
                      "To launch a VM you can cloud-client.sh --run --name <image_name> --hours <# hours> --kernel vmlinuz-" + eki + "  \n" + \
                      "More information is provided in https://portal.futuregrid.org/tutorials/nimbus \n" 
            else:
                return nimbusEnv  #error message
        else:            
            print "Your Nimbus image is located in " + str(imagebackpath) + " \n" + \
            "The kernel to use is vmlinuz-" + eki + " and the ramdisk will be according to that \n" + \
            "More information is provided in https://portal.futuregrid.org/tutorials/nimbus \n"
            return None
        
    def euca_method(self, imagebackpath, eki, eri, operatingsystem, machinename, varfile, getimg, wait, delorigin):
        #TODO: Pick kernel and ramdisk from available eki and eri
        
        errormsg = "An error occured when uploading image to Eucalyptus. Your image is located in " + str(imagebackpath) + " so you can upload it manually \n" + \
                "The kernel and ramdisk to use are " + eki + " and " + eri + " respectively \n" + \
                "Remember to load you Eucalyptus environment before you run the instance (source eucarc) \n" + \
                "More information is provided in https://portal.futuregrid.org/tutorials/eucalyptus \n"
        msg=""
        #hardcoded for now
        #eki = 'eki-78EF12D2'
        #eri = 'eri-5BB61255'
        path = ""
        region = ""
        imageId = None
        if not eval(getimg):            
            eucaEnv = self.euca_environ(varfile)
            
            filename = os.path.split(imagebackpath)[1].strip()    
            print filename

            tempdir = "/tmp/" + str(randrange(999999999999999999999999)) + str(time.time()) + "/"
            os.system("mkdir -p " + tempdir)

            #Bundle Image
            #cmd = 'euca-bundle-image --image ' + imagebackpath + ' --kernel ' + eki + ' --ramdisk ' + eri
            cmd = "euca-bundle-image --cert " + str(os.getenv("EC2_CERT")) + " --privatekey " + str(os.getenv("EC2_PRIVATE_KEY")) + \
                  " --user " + str(os.getenv("EC2_USER_ID")) + " --ec2cert " + str(os.getenv("EUCALYPTUS_CERT")) + " --url " + str(eucaEnv.getEc2_url()) + \
                  " -a " + str(os.getenv("EC2_ACCESS_KEY")) + " -s " + str(os.getenv("EC2_SECRET_KEY")) + \
                  " --image " + str(imagebackpath) + " --destination " + tempdir 
                  
            if eki != "None":
                cmd += " --kernel " + str(eki)
            if eri != "None":
                cmd += " --ramdisk " + str(eri) 
                                    
            print cmd
            self._log.debug(cmd)
            stat = os.system(cmd)
            if stat != 0:
                msg = "ERROR: in euca-bundle-image. " + str(sys.exc_info())
                self._log.error(msg)
                return msg + "\n " + errormsg
            
            #Upload bundled image
            #cmd = 'euca-upload-bundle --bucket ' + self.user + ' --manifest ' + '/tmp/' + filename + '.manifest.xml'
            cmd = "euca-upload-bundle -a " + os.getenv("EC2_ACCESS_KEY") + " -s " + os.getenv("EC2_SECRET_KEY") + \
                " --url " + eucaEnv.getS3_url() + " --ec2cert " + os.getenv("EUCALYPTUS_CERT") + " --bucket " + self.user + " --manifest " + \
                tempdir + filename + ".manifest.xml"
            print cmd      
            self._log.debug(cmd)  
            stat = os.system(cmd)
            if stat != 0:
                msg = "ERROR: in euca-upload-bundle. " + str(sys.exc_info())
                self._log.error(msg)
                return msg + "\n " + errormsg
    
            #Register image
            cmd = 'euca-register  --url ' + eucaEnv.getEc2_url() + " " + self.user + '/' + filename + '.manifest.xml'
            #cmd = "euca-register -a " + os.getenv("euc    ") + " -s " + os.getenv("EC2_SECRET_KEY") + \
            #    " --url " + eucaEnv.getEc2_url() + " " + self.user + '/' + filename + '.manifest.xml'        
            print cmd
            self._log.debug(cmd)
            #stat = os.system(cmd) #execute this with Popen to get the output
            p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            std = p.communicate()
            stat = 0            
            if p.returncode != 0:
                msg = "ERROR: in euca-regsiter. " + str(sys.exc_info())
                self._log.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])
                stat = 1
            else:
                if len(std[0]) > 0:
                    self._log.debug('stdout: ' + std[0])
                    self._log.debug('stderr: ' + std[1])
                    print std[0]
                    imageId = std[0].split("IMAGE")[1].strip()
            
            os.system("rm -rf " + tempdir)
            
            cmd = "rm -f " + imagebackpath
            if stat == 0:
                if delorigin == "True":
                    print cmd
                    self._log.debug(cmd)
                    os.system(cmd)
                
                print "Your image has been registered on Eucalyptus with the id printed in the previous line (IMAGE  id) \n" + \
                  "You can also use fg-rain (launch command if you are inside fg-shell) to run instances of this image \n" + \
                  "Or you can use euca-run-instances -k keyfile -n <#instances> id  \n" + \
                  "Remember to load you Eucalyptus environment before you run the instance (source eucarc) \n " + \
                  "More information is provided in https://portal.futuregrid.org/tutorials/eucalyptus \n" 
                                 
            else:
                return msg + "\n " + errormsg 
                           
              
            return imageId              
        else:            
            print "Your Eucalyptus image is located in " + str(imagebackpath) + " \n" + \
            "The kernel and ramdisk to use are " + eki + " and " + eri + " respectively \n" + \
            "Remember to load you Eucalyptus environment before you run the instance (source eucarc) \n" + \
            "More information is provided in https://portal.futuregrid.org/tutorials/eucalyptus \n"
            return None
                       
        
    def openstack_method(self, imagebackpath, eki, eri, operatingsystem, machinename, varfile, getimg, wait, delorigin):
        

        errormsg = "An error occured when uploading image to OpenStack. Your image is located in " + str(imagebackpath) + " so you can upload it manually \n" + \
                "The kernel and ramdisk to use are " + eki + " and " + eri + " respectively \n" + \
                "Remember to load you OpenStack environment before you run the instance (source novarc) \n" + \
                "More information is provided in https://portal.futuregrid.org/tutorials/openstack " + \
                " and in https://portal.futuregrid.org/tutorials/eucalyptus\n"

        #hardcoded for now
        #eki = 'aki-00000026'
        #eri = 'ari-00000027'
        imageId = None
        path = ""
        region = ""
        if not eval(getimg):            
            openstackEnv = self.openstack_environ(varfile)
                        
            filename = os.path.split(imagebackpath)[1].strip()
    
            print filename
            
            tempdir = "/tmp/" + str(randrange(999999999999999999999999)) + str(time.time()) + "/"
            os.system("mkdir -p " + tempdir)
    
            #Bundle Image
            #cmd = 'euca-bundle-image --image ' + imagebackpath + ' --kernel ' + eki + ' --ramdisk ' + eri
            cmd = "euca-bundle-image --cert " + os.path.expanduser(os.path.expandvars(os.getenv("EC2_CERT"))) + " --privatekey " + os.path.expanduser(os.path.expandvars(os.getenv("EC2_PRIVATE_KEY"))) + \
                  " --user " + str(os.getenv("EC2_USER_ID")) + " --ec2cert " + str(os.getenv("EUCALYPTUS_CERT")) + " --url " + str(openstackEnv.getEc2_url()) + \
                  " -a " + str(os.getenv("EC2_ACCESS_KEY")) + " -s " + str(os.getenv("EC2_SECRET_KEY")) + \
                  " --image " + str(imagebackpath) + " --destination " + tempdir

            if eki != "None":
                cmd += " --kernel " + str(eki)
            if eri != "None":
                cmd += " --ramdisk " + str(eri) 
                  
            print cmd
            self._log.debug(cmd)
            stat = os.system(cmd)
            if stat != 0:
                msg = "ERROR: in euca-bundle-image. " + str(sys.exc_info())
                self._log.error(msg)
                return msg + "\n " + errormsg
            #Upload bundled image
            #cmd = 'euca-upload-bundle --bucket ' + self.user + ' --manifest ' + '/tmp/' + filename + '.manifest.xml'
            cmd = "euca-upload-bundle -a " + os.getenv("EC2_ACCESS_KEY") + " -s " + os.getenv("EC2_SECRET_KEY") + \
                " --url " + openstackEnv.getS3_url() + " --ec2cert " + os.getenv("EUCALYPTUS_CERT") + " --bucket " + self.user + " --manifest " + \
                tempdir + filename + ".manifest.xml"
            print cmd      
            self._log.debug(cmd)  
            stat = os.system(cmd)
            if stat != 0:
                msg = "ERROR: in euca-upload-image. " + str(sys.exc_info())
                self._log.error(msg)
                return msg + "\n " + errormsg
            
            #Register image
            cmd = 'euca-register --url ' + openstackEnv.getEc2_url() + " " + self.user + '/' + filename + '.manifest.xml'
            #cmd = "euca-register -a " + os.getenv("EC2_ACCESS_KEY") + " -s " + os.getenv("EC2_SECRET_KEY") + \
            #    " --url " + openstackEnv.getEc2_url() + " " + self.user + '/' + filename + '.manifest.xml'    
            print cmd
            self._log.debug(cmd)
            #stat = os.system(cmd) #execute this with Popen to get the output
            
            p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
            std = p.communicate()
            stat = 0            
            if p.returncode != 0:
                msg = "ERROR: in euca-regsiter. " + str(sys.exc_info())
                self._log.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])
                stat = 1
            else:
                if len(std[0]) > 0:
                    self._log.debug('stdout: ' + std[0])
                    self._log.debug('stderr: ' + std[1])
                    print std[0]
                    try:
                        imageId = std[0].split("IMAGE")[1].strip()
                    except:
                        self._log.error("Trying to get imageId. " + str(sys.exc_info()))
                        stat = 1
            
            os.system("rm -rf " + tempdir)
                
            cmd = "rm -f " + imagebackpath            
            if stat == 0:
                if delorigin == "True":
                    print cmd
                    self._log.debug(cmd)
                    os.system(cmd)
            
                print "Your image has been registered on OpenStack with the id " + imageId + " \n" + \
                      "You can also use fg-rain (launch command if you are inside fg-shell) to run instances of this image \n" + \
                      "Or you can use euca-run-instances -k keyfile -n <#instances> id \n" + \
                      "Remember to load you OpenStack environment before you run the instance (source novarc) \n " + \
                      "More information is provided in https://portal.futuregrid.org/tutorials/openstack " + \
                      "and in https://portal.futuregrid.org/tutorials/eucalyptus\n"
                                     
            else:
                return msg + "\n " + errormsg
                
            
            return imageId
        else:
            print "Your OpenStack image is located in " + str(imagebackpath) + " \n" + \
            "The kernel and ramdisk to use are " + eki + " and " + eri + " respectively \n" + \
            "Remember to load you OpenStack environment before you run the instance (source novarc) \n" + \
            "More information is provided in https://portal.futuregrid.org/tutorials/openstack " + \
            " and in https://portal.futuregrid.org/tutorials/eucalyptus\n"
            return None
        
    def opennebula_method(self, imagebackpath, eki, eri, operatingsystem, machinename, varfile, getimg, wait):
        
        filename = os.path.split(imagebackpath)[1].strip()

        print filename
        
        name = operatingsystem + "-" + filename.split(".")[0] + "-" + self.user
        print name
        
        f = open(filename + ".one", 'w')
        f.write("NAME          = \"" + name + "\" \n" 
        "PATH          = " + imagebackpath + " \n"
        "PUBLIC        = NO \n")
        f.close()
        
        self._log.debug("Authenticating against OpenNebula")
        if self._verbose:
            print "Authenticating against OpenNebula"
        cmd = "oneauth login " + self.user
        #oneuser in OpenNebula 3.0
        print cmd
        #os.system(cmd)
        
        self._log.debug("Uploading image to OpenNebula")
        if self._verbose:
            print "Uploading image to OpenNebula"
        cmd = "oneimage register " + filename + ".one"
        print cmd
        #os.system(cmd)
        
        cmd = "rm -f " + filename + ".one"
        print cmd
        #os.system(cmd)
        
        f = open(filename + "_template.one", 'w')     
        #On OpenNebula 3.0 NETWORK_ID and IMAGE_ID  
        if (operatingsystem == "centos"):                        
            f.write("#--------------------------------------- \n"
                    "# VM definition example \n"
                    "#--------------------------------------- \n"            
                    "NAME = \"" + name + "\" \n"
                    "\n"
                    "CPU    = 0.5\n"
                    "MEMORY = 2048\n"
                    "\n"
                    "OS = [ \n"
                    "  arch=\"x86_64\", \n"
                    "  kernel=\"" + eki + "\", \n"
                    "  initrd=\"" + eri + ".img\", \n"
                    "  root=\"hda\" \n"
                    "  ] \n"
                    " \n"
                    "DISK = [ \n"
                    "  image   = \"" + name + "\",\n"
                    "  target   = \"hda\",\n"
                    "  readonly = \"no\"]\n"
                    "\n"
                    "NIC = [ NETWORK=\"Virt LAN\"]\n"
                    "NIC = [ NETWORK=\"Large LAN\"]\n"
                    "\n"                    
                    "FEATURES=[ acpi=\"no\" ]\n"
                    "\n"
                    "CONTEXT = [\n"
                    "   files = \"/srv/cloud/images/centos/init.sh /tmp/id_rsa.pub\",\n"
                    "   target = \"hdc\",\n"
                    "   root_pubkey = \"id_rsa.pub\"\n"
                    "]\n"
                    "\n"                    
                    "GRAPHICS = [\n"
                    "  type    = \"vnc\",\n"
                    "  listen  = \"127.0.0.1\"\n"
                    "  ]\n")
                
        elif (operatingsystem == "ubuntu"):
            f.write("#--------------------------------------- \n"
                    "# VM definition example \n"
                    "#--------------------------------------- \n"            
                    "NAME = \"" + name + "\" \n"
                    "\n"
                    "CPU    = 0.5\n"
                    "MEMORY = 2048\n"
                    "\n"
                    "OS = [ \n"
                    "  arch=\"x86_64\", \n"
                    "  kernel=\"" + eki + "\", \n"
                    "  initrd=\"" + eri + "\", \n"
                    "  root=\"sda\" \n"
                    "  ] \n"
                    " \n"
                    "DISK = [ \n"
                    "  image   = \"" + name + "\",\n"
                    "  target  = \"hda\",\n"
                    "  bus     = \"ide\",\n"
                    "  readonly = \"no\"]\n"
                    "\n"
                    "NIC = [ NETWORK=\"Virt LAN\"]\n"
                    "NIC = [ NETWORK=\"Large LAN\"]\n"
                    "\n"                    
                    "FEATURES=[ acpi=\"no\" ]\n"
                    "\n"
                    "CONTEXT = [\n"
                    "   files = \"/srv/cloud/images/ubuntu/init.sh /tmp/id_rsa.pub\",\n"
                    "   target = \"hdc\",\n"
                    "   root_pubkey = \"id_rsa.pub\"\n"
                    "]\n"
                    "\n"                    
                    "GRAPHICS = [\n"
                    "  type    = \"vnc\",\n"
                    "  listen  = \"127.0.0.1\"\n"
                    "  ]\n")
        
        f.close()
        
        print "The file " + filename + "_template.one is an example of the template that it is needed to launch a VM \n" + \
        "You need to modify the kernel and initrd path to indiacte their location in your particular system\n" + \
        "To see the availabe networks you can use onevnet list\n" + \
        "To launch a VM you can use onevm create " + filename + "_template.one \n" 
        
        #create template to upload image to opennebula repository
        
        #create script to boot image and tell user how to use it
   
   
    def xcat_sites(self):
        sitelist = self._registerConf.listHpcSites()
        sitesdic = {}
        for i in sitelist:
            xcatstatus, moabstatus = self.xcat_method(i, None, "infosites")
            if xcatstatus == "True":
                xcatstatus = "Active"
            else:
                xcatstatus = "Not Active"
            if moabstatus == "True":
                moabstatus = "Active"
            else:
                moabstatus = "Not Active"
            sitesdic[i] = [xcatstatus, moabstatus]
        return sitesdic

    def xcat_method(self, xcat, image, operation):
        start_all = time.time()
        checkauthstat = []
        
        xcat_status = "" #this is for infosite
        moab_status = "" #this is for infosite
        
        #Load Machines configuration
        xcat = xcat.lower()
        if (xcat == "india" or xcat == "india.futuregrid.org"):
            self.machine = "india"
        elif (xcat == "minicluster" or xcat == "tm1r" or xcat == "tm1r.tidp.iu.futuregrid.org"):
            self.machine = "minicluster"
        else:
            self._log.error("Site name not recognized")
            if self._verbose:
                print "ERROR: Site name not recognized. Please use the --listsites to list the available sites."
            sys.exit(1)
        
        self._registerConf.load_machineConfig(self.machine)
        self.loginmachine = self._registerConf.getLoginMachine()
        self.xcatmachine = self._registerConf.getXcatMachine()
        self.moabmachine = self._registerConf.getMoabMachine()        
        
        self._log.debug("login machine " + self.loginmachine)
        self._log.debug("xcat machine " + self.xcatmachine)
        self._log.debug("moab machine " + self.moabmachine)        
        #################
        
        """
        urlparts = image.split("/")
        self._log.debug(str(urlparts))
        if len(urlparts) == 1:
            nameimg = urlparts[0].split(".")[0]
        elif len(urlparts) == 2:
            nameimg = urlparts[1].split(".")[0]
        else:
            nameimg = urlparts[len(urlparts) - 1].split(".")[0]

        
        #REMOVE THIS. WE ONLY ALLOW register IMAGES FROM REPOSITORY
        #NOW IT IS NOT NEEDED THE SHAREDDIRSERVER.
        
        #Copy the image to the Shared directory.
        if (self.loginmachine == "localhost" or self.loginmachine == "127.0.0.1"):
            self._log.info('Copying the image to the right directory')
            cmd = 'cp ' + image + ' ' + self.shareddirserver + '/' + nameimg + '.tgz'
            self._log.info(cmd)
            self.runCmd(cmd)
        else:                    
            self._log.info('Uploading image. You may be asked for ssh/passphrase password')
            cmd = 'scp ' + image + ' ' + self.user + '@' + self.loginmachine + ':' + self.shareddirserver + '/' + nameimg + '.tgz'
            self._log.info(cmd)
            self.runCmd(cmd)
        """
        
        #xCAT server                
        txt = 'Connecting to xCAT server'
        if self._verbose:
            print txt
        self._log.debug(txt + ":" + self.xcatmachine + " port:" + str(self._xcat_port))
        #msg = self.name + ',' + self.operatingsystem + ',' + self.version + ',' + self.arch + ',' + self.kernel + ',' + self.shareddirserver + ',' + self.machine
        
        #self.shareddirserver + '/' + nameimg + '.tgz, '
        moabstring = ""
        #Notify xCAT registration to finish the job
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            xcatServer = ssl.wrap_socket(s,
                                        ca_certs=self._ca_certs,
                                        certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            
            xcatServer.connect((self.xcatmachine, self._xcat_port))
            
            msg = str(image) + "," + str(operation) + ',' + str(self.kernel) + ',' + self.machine + ',' + str(self.user) + ',' + str(self.passwd) + ",ldappassmd5" 
            #self._log.debug('Sending message: ' + msg)
            
            xcatServer.write(msg)

            if self._verbose:
                print "Your request is in the queue to be processed after authentication"

            if self.check_auth(xcatServer, checkauthstat):

                if operation == "list":                    
                    xcatimagelist = xcatServer.read(4096)
                    self._log.debug("Getting xCAT image list:" + xcatimagelist)
                    xcatimagelist = xcatimagelist.split(",")
                    moabstring = 'list,list,list,list,list'
                elif operation == "kernels":
                    defaultkernelslist = xcatServer.read(4096)
                    self._log.debug("Getting xCAT default kernel list:" + defaultkernelslist)
                    kernelslist = xcatServer.read(4096)
                    self._log.debug("Getting xCAT kernel list:" + kernelslist)                                        
                    moabstring = 'kernellist'
                    imagename = str(defaultkernelslist) + "&" + str(kernelslist)
                elif operation == "infosites":
                    start = time.time()
                    xcat_status = xcatServer.read(4096).strip()
                    self._log.debug("Getting services information of supported sites:" + xcat_status)        
                    end = time.time()
                    self._log.info('TIME get xCAT HPC info sites:' + str(end - start))
                    moabstring = 'infosites,infosites,infosites,infosites,infosites'
                elif operation == "remove":
                    start = time.time()
                    xcat_status = xcatServer.read(4096)
                    self._log.debug("Removing image from Moab")        
                    end = time.time()
                    self._log.info('TIME remove image from xCAT:' + str(end - start))
                    moabstring = 'remove,' + image + ',remove,remove,remove'

                    if xcat_status.strip() != "Done":
                        return xcat_status

                else:
                    if self._verbose:
                        print "Customizing and registering image on xCAT"
                    
                    ret = xcatServer.read(1024)
                    #check if the server did all right
                    if ret != 'OK':
                        self._log.error('Reply Server: ' + str(ret))
                        if self._verbose:
                            print 'Reply Server: ' + str(ret)
                        return
                    #recieve the prefix parameter from xcat server
                    moabstring = xcatServer.read(2048)
                    self._log.debug("String received from xcat server " + moabstring)
                    params = moabstring.split(',')
                    imagename = params[0] + '' + params[2] + '' + params[1]                    	    
                    moabstring += ',' + self.machine
            else:
                self._log.error(str(checkauthstat[0]))
                if self._verbose:
                    print checkauthstat[0]
                return
        
                    
        except ssl.SSLError:
            self._log.error("CANNOT establish SSL connection with IMRegisterServerXcat service " + self.xcatmachine + ". EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish SSL connection with IMRegisterServerXcat service " + self.xcatmachine + "."
            if operation == "infosites":
                return None,None
            else:
                return
        except socket.error:
            self._log.error("CANNOT establish connection with IMRegisterServerXcat service " + self.xcatmachine + ". EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish connection with IMRegisterServerXcat service " + self.xcatmachine + "."
            if operation == "infosites":
                return None,None
            else:
                return
        
        
        if operation != "kernels":            
            #Moab part
            txt = 'Connecting to Moab server'
            if self._verbose:
                print txt
            self._log.debug(txt + ":" + self.moabmachine+ " port:" + str(self._moab_port))
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                moabServer = ssl.wrap_socket(s,
                                            ca_certs=self._ca_certs,
                                            certfile=self._certfile,
                                            keyfile=self._keyfile,
                                            cert_reqs=ssl.CERT_REQUIRED,
                                            ssl_version=ssl.PROTOCOL_TLSv1)

                moabServer.connect((self.moabmachine, self._moab_port))
                
                self._log.debug('Sending message: ' + moabstring)
                moabServer.write(moabstring)
                
                if operation == "list":                                
                    moabimageslist = moabServer.read(4096)
                    self._log.debug("Getting Moab image list:" + moabimageslist)
                    moabimageslist = moabimageslist.split(",")                
                    setmoab = set(moabimageslist)
                    setxcat = set(xcatimagelist)
                    setand = setmoab & setxcat                
                    imagename = list(setand)
                elif operation == "infosites":
                    start = time.time()
                    moab_status = moabServer.read(4096)
                    self._log.debug("Getting services information of supported sites:" + moab_status)        
                    end = time.time()
                    self._log.info('TIME get Moab HPC info sites:' + str(end - start)) 
                elif operation == "remove":
                    self._log.debug("Removing image from Moab")
                    start = time.time()
                    moab_status = moabServer.read(4096)
                    if moab_status != 'OK':
                        self._log.error('Reply Moab server:' + str(moab_status))
                        if self._verbose:
                            print 'Reply Moab server:' + str(moab_status)
                        return  
                    end = time.time()
                    self._log.info('TIME remove image from Moab:' + str(end - start)) 
                    imagename = ""
                else:
                    ret = moabServer.read(100)
                    if ret != 'OK':
                        self._log.error('Reply Moab server:' + str(ret))
                        if self._verbose:
                            print 'Reply Moab server:' + str(ret)
                        return                               
                
            except ssl.SSLError:
                self._log.error("CANNOT establish SSL connection with IMRegisterServerMoab service " + self.moabmachine + ". EXIT")
                if self._verbose:
                    print "ERROR: CANNOT establish SSL connection with IMRegisterServerMoab service " + self.moabmachine + ". EXIT"
                if operation == "infosites":
                    return xcat_status,None
                else:
                    return
            except socket.error:
                self._log.error("CANNOT establish connection with IMRegisterServerMoab service " + self.moabmachine + ". EXIT")
                if self._verbose:
                    print "ERROR: CANNOT establish connection with IMRegisterServerMoab service " + self.moabmachine + "."
                if operation == "infosites":
                    return xcat_status,None
                else:
                    return
            
        #return image registered or list of images
        end_all = time.time()
        self._log.info('TIME walltime image register xcat/moab: ' + str(end_all - start_all))
        
        if operation == "infosites":
            return xcat_status, moab_status
        else:
            return imagename
    ############################################################
    # _retrieveImg
    ############################################################
    def _retrieveImg(self, imgURI, dest):
        
        filename = os.path.split(imgURI)[1]        
        
        fulldestpath = dest + "/" + filename
                
        if os.path.isfile(fulldestpath):
            exists = True
            i = 0       
            while (exists):            
                aux = fulldestpath + "_" + i.__str__()
                if os.path.isfile(aux):
                    i += 1
                else:
                    exists = False
                    fulldestpath = aux
                
    
        if self._verbose:
            cmdscp = "scp " + self.iaasmachine + ":" + imgURI + " " + fulldestpath
        else: #this is the case where another application call it. So no password or passphrase is allowed
            cmdscp = "scp -q -oBatchMode=yes " + self.iaasmachine + ":" + imgURI + " " + fulldestpath
        #print cmdscp
        output = ""
        try:
            self._log.debug('Retrieving image')
            if self._verbose:
                print 'Retrieving image. You may be asked for ssh/passphrase password'
            stat = os.system(cmdscp)
            if (stat == 0):
                output = fulldestpath                
            else:
                self._log.error("Error retrieving the image. Exit status " + str(stat))
                if self._verbose:
                    print "Error retrieving the image. Exit status " + str(stat)
                #remove the temporal file
        except os.error:
            self._log("Error, The image cannot be retieved" + str(sys.exc_info()))
            if self._verbose:
                print "Error, The image cannot be retieved" + str(sys.exc_info())
            output = None

        return output


    def runCmd(self, cmd):        
        cmdLog = logging.getLogger('RegisterClient.exec')
        cmdLog.debug(cmd)
        p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
        std = p.communicate()
        status = 0
        if len(std[0]) > 0:
            cmdLog.debug('stdout: ' + std[0])
            cmdLog.debug('stderr: ' + std[1])
        if p.returncode != 0:
            cmdLog.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])
            status = 1
            #sys.exit(p.returncode)
        return status


def main():

    parser = argparse.ArgumentParser(prog="fg-register", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Registration Help ")    
    parser.add_argument('-u', '--user', dest='user', required=True, metavar='user', help='FutureGrid User name')
    parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--image', dest='image', metavar='ImgFile', help='Select the image to register by specifying its location. The image is a tgz file that contains the manifest and image files.')    
    #group.add_argument('-i', '--image', dest='image', metavar='ImgFile', help='Select the image to register by specifying its location. In general, the image is a tgz file that contains the manifest and image files. If no customization required (must use -j option), you do not need the manifest and can specify the location of the image file.')
    group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Select the image to register by specifying its Id in the repository.')
    group.add_argument('-l', '--list', dest='list', action="store_true", help='List images registered in xCAT/Moab or in the Cloud infrastructures')
    group.add_argument('-t', '--listkernels', dest='listkernels', action="store_true", help='List kernels available for HPC or Cloud infrastructures')
    group.add_argument('--listsites', dest='listsites', action="store_true", help='List supported sites with their respective HPC and Cloud services')
    group.add_argument('--deregister', dest='deregister', metavar='ImgId', help='Deregister an image from the specified infrastructure.')
    parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel. "
                        "Case a) if the image has to be adapted (any image generated with fg-generate) this option can be used to select one of the available kernels. Both kernelId and ramdiskId will be selected according to the selected kernel. This case is for any infrastructure. "
                        "Case b) if the image is ready to be registered, you may need to specify the id of the kernel in the infrastructure. This case is when -j/--justregister is used and only for cloud infrastructures.")
    parser.add_argument('-a', '--ramdisk', dest="ramdisk", metavar='ramdiskId', help="Specify the desired ramdisk that will be associated to "
                        "your image in the cloud infrastructure. This option is only needed if -j/--justregister is used.")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-x', '--xcat', dest='xcat', metavar='SiteName', help='Select the HPC infrastructure named SiteName (minicluster, india ...).')
    group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...)')
    group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', help='Select the OpenNebula Infrastructure located in SiteName (india, sierra...)')
    group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimbus Infrastructure located in SiteName (hotel, alamo, foxtrot...)')
    group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure  located in SiteName (india, sierra...).')
    parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files.  Currently this is used by Eucalyptus, OpenStack and Nimbus.')
    parser.add_argument('-g', '--getimg', dest='getimg', action="store_true", default=False, help='Customize the image for a particular cloud framework but does not register it. So the user gets the image file.')
    parser.add_argument('-p', '--noldap', dest='ldap', action="store_false", default=True, help='If this option is active, FutureGrid LDAP will not be configured in the image. This option only works for Cloud registrations. LDAP configuration is needed to run jobs using fg-rain.')
    parser.add_argument('-w', '--wait', dest='wait', action="store_true", help='Wait until the image is available in the targeted infrastructure. Currently this is used by Eucalyptus and OpenStack')
    parser.add_argument('--nopasswd', dest='nopasswd', action="store_true", default=False, help='If this option is used, the password is not requested. This is intended for systems daemons like Inca')
    parser.add_argument('-j', '--justregister', dest='justregister', action="store_true", default=False, help='It assumes that the image is ready to run in the selected infrastructure. '
                        'Thus, no additional configuration will be performed. Only valid for Cloud infrastructures. (This is basically a wrapper of the tools that register images into the cloud infrastructures)')
    
    args = parser.parse_args()
    
    print 'Starting Image Register Client...'
    
    verbose = True #to activate the print
    
    if args.nopasswd == False:    
        print "Please insert the password for the user " + args.user + ""
        m = hashlib.md5()
        m.update(getpass())
        passwd = m.hexdigest()
    else:        
        passwd = "None"
    
    imgregister = IMRegister(args.kernel, args.user, passwd, verbose, args.debug)

    used_args = sys.argv[1:]
    
    image_source = "repo"
    image = args.imgid    
    if args.image != None:
        image_source = "disk"
        image = args.image
        if not  os.path.isfile(args.image):            
            print 'ERROR: Image file not found'            
            sys.exit(1)
    
    if args.listsites:
        
        cloudinfo = imgregister.iaas_generic(None, "infosites", "", "", "", None, False, False)
        if cloudinfo != None:
            cloudinfo_dic = eval(cloudinfo)
            print "Supported Sites Information"
            print "===========================\n"
            print "Cloud Information"
            print "-----------------"
            for i in cloudinfo_dic:
                print "SiteName: " + i
                print "  Description: " + cloudinfo_dic[i][0]
                print "  Infrastructures supported: " + str(cloudinfo_dic[i][1:])
        
        imgregister.setVerbose(False)
        
        hpcinfo_dic = imgregister.xcat_sites()
        if len(hpcinfo_dic) != 0:
            print "\nHPC Information (baremetal)"
            print "---------------------------"
            for i in hpcinfo_dic:
                print "SiteName: " + i
                print "  RegisterXcat Service Status: " + hpcinfo_dic[i][0]
                print "  RegisterMoab Service Status: " + hpcinfo_dic[i][1]
        imgregister.setVerbose(True)    
        
    #XCAT
    elif args.xcat != None:
        if args.imgid != None:
            imagename = imgregister.xcat_method(args.xcat, args.imgid, "register")  
            if imagename != None:
                if re.search("^ERROR", imagename):
                    print imagename
                else:        
                    print 'Your image has been registered in xCAT as ' + str(imagename) + '\n Please allow a few minutes for xCAT to register the image before attempting to use it.'
                    print 'To run a job in a machine using your image you use the fg-rain command'
                    print 'You can also do it by executing the next command: qsub -l os=<imagename> <scriptfile>' 
                    print 'In the second case you can check the status of the job with the checkjob and showq commands'
        elif args.list:
            hpcimagelist = imgregister.xcat_method(args.xcat, None, "list")
            if hpcimagelist != None:
                print "The list of available images on xCAT/Moab is:"
                for i in hpcimagelist:
                    print "  " + i
                print "You can get more details by querying the image repository using fg-repo -q command and the query string: \"* where tag=imagename\". \n" + \
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username."
            else:
                print "ERROR: No image list has been returned"
        elif args.listkernels:
            kernelslist = imgregister.xcat_method(args.xcat, None, "kernels")
            if kernelslist != None:
                print "The list of available kernels for HPC is:"
                output = kernelslist.split("&")
                defaultkernels = eval(output[0])
                kernels = eval(output[1])
                print "\nDefault Kernels"
                print "---------------"
                for i in defaultkernels:
                    print i
                    print defaultkernels[i]
                print "\nAuthorized Kernels"
                print "-------------------"
                for i in kernels:
                    print i
                    print kernels[i]
        elif args.deregister:
            imagename = imgregister.xcat_method(args.xcat, args.deregister, "remove")
            if imagename != None:  
                if re.search("^ERROR", imagename):
                    print imagename
                else:
                    print "The image " + args.deregister + " has been deleted successfully."
            else:
                print "ERROR: removing image"          
                  
        else:            
            print "ERROR: You need to specify the id of the image that you want to register (-r/--imgid option) or the -q/--list option to list the registered images"
            print "The parameter -i/--image cannot be used with this type of registration"
            sys.exit(1)
    else:
        ldap = args.ldap 
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))
        #EUCALYPTUS    
        if ('-e' in used_args or '--euca' in used_args) and checkVarFile(varfile, args.getimg, args.listkernels, "Eucalyptus"):
            if args.listkernels:
                kernelslist = imgregister.iaas_generic(args.euca, "kernels", image_source, "euca", varfile, args.getimg, ldap, args.wait)
                if kernelslist != None:
                    kernelslist_dic = eval(kernelslist)
                    defaultkernels = kernelslist_dic["Default"]
                    kernels = kernelslist_dic["Authorized"]
                    if defaultkernels != "" and kernels:
                        print "The list of available kernels for Eucalyptus on " + str(args.euca) + " is:"
                        print "\nDefault Kernels"
                        print "---------------"                          
                        print defaultkernels
                        print "\nAuthorized Kernels"
                        print "-------------------"
                        kernelsout = []                                
                        for i in kernels:          
                            kernelsout.append(i)
                        print kernelsout
                    else:
                        print "ERROR: Eucalytpus is not supported on " + str(args.euca) + "\n"
            elif args.list:
                output = imgregister.cloudlist(str(args.euca), "euca", varfile)                
                if output != None:
                    if not isinstance(output, list):
                        print output
                    else:
                        print "The list of available images on Eucalyptus " + str(args.euca) + " is:"                        
                        for i in output:                       
                            print i    
                        print "You can get more details by querying the image repository using fg-repo -q command and the query string: \"* where tag=imagename\". \n" + \
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img.manifest.xml"
            elif args.justregister:
                output = imgregister.iaas_justregister(args.euca, image, image_source, args.ramdisk, "euca", varfile, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
            elif args.deregister:
                output = imgregister.cloudremove(str(args.euca), "euca",varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output
            else:
                output = imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, args.getimg, ldap, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
        #OpenNebula
        elif ('-o' in used_args or '--opennebula' in used_args):
            if args.listkernels:
                kernelslist = imgregister.iaas_generic(args.opennebula, "kernels", image_source, "opennebula", varfile, args.getimg, ldap, args.wait)
                if kernelslist != None:
                    kernelslist_dic = eval(kernelslist)
                    defaultkernels = kernelslist_dic["Default"]
                    kernels = kernelslist_dic["Authorized"]
                    if defaultkernels != "" and kernels:
                        print "The list of available kernels for OpenNebula " + str(args.opennebula) + " is:"
                        print "\nDefault Kernels"
                        print "---------------"                
                        print defaultkernels
                        print "\nAuthorized Kernels"
                        print "-------------------"
                        kernelsout = []                                
                        for i in kernels:          
                            kernelsout.append(i)
                        print kernelsout
                    else:
                        print "ERROR: OpenNebula is not supported on " + str(args.nimbus) + "\n"
            else:
                output = imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, args.getimg, ldap, args.wait)
        #NIMBUS
        elif ('-n' in used_args or '--nimbus' in used_args) and checkVarFile(varfile, args.getimg, args.listkernels, "Nimbus"):
            if args.listkernels:
                kernelslist = imgregister.iaas_generic(args.nimbus, "kernels", image_source, "nimbus", varfile, args.getimg, ldap, args.wait)
                if kernelslist != None:
                    kernelslist_dic = eval(kernelslist)
                    defaultkernels = kernelslist_dic["Default"]
                    kernels = kernelslist_dic["Authorized"]
                    if defaultkernels != "" and kernels:
                        print "The list of available kernels for the Nimbus located on " + str(args.nimbus) + " is:"
                        print "\nDefault Kernels"
                        print "---------------"                
                        print defaultkernels
                        print "\nAuthorized Kernels"
                        print "-------------------"
                        kernelsout = []                                
                        for i in kernels:          
                            kernelsout.append(i)
                        print kernelsout
                    else:
                        print "ERROR: Nimbus is not supported on " + str(args.nimbus) + "\n"
            elif args.list:
                output = imgregister.cloudlist(str(args.nimbus), "nimbus", varfile)                
                if output != None:
                    if not isinstance(output, list):
                        print output
                    else:
                        print "The list of available images on the Nimbus located on " + str(args.nimbus) + " is:"
                        for i in output:                       
                            print i  
                        print "You can get more details by querying the image repository using fg-repo -q command and the query string: \"* where tag=imagename\". \n" + \
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img"
            elif args.justregister:
                output = imgregister.iaas_justregister(args.nimbus, image, image_source, args.ramdisk, "nimbus", varfile, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
            elif args.deregister:
                output = imgregister.cloudremove(str(args.euca), "nimbus",varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output
            else:    
                output = imgregister.iaas_generic(args.nimbus, image, image_source, "nimbus", varfile, args.getimg, ldap, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
        elif ('-s' in used_args or '--openstack' in used_args) and checkVarFile(varfile, args.getimg, args.listkernels, "OpenStack"):
            if args.listkernels:
                kernelslist = imgregister.iaas_generic(args.openstack, "kernels", image_source, "openstack", varfile, args.getimg, ldap, args.wait)
                if kernelslist != None:                                 
                    kernelslist_dic = eval(kernelslist)
                    defaultkernels = kernelslist_dic["Default"]                    
                    kernels = kernelslist_dic["Authorized"]
                    if defaultkernels != "" and kernels:
                        print "The list of available kernels for the OpenStack located on " + str(args.openstack) + " is:"
                        print "\nDefault Kernels"
                        print "---------------"                
                        print defaultkernels
                        print "\nAuthorized Kernels"
                        print "-------------------"
                        kernelsout = []                                
                        for i in kernels:          
                            kernelsout.append(i)
                        print kernelsout
                    else:
                        print "ERROR: OpenStack is not supported on " + str(args.openstack) + "\n"
            elif args.list:
                output = imgregister.cloudlist(str(args.openstack), "openstack", varfile)                
                if output != None:
                    if not isinstance(output, list):
                        print output
                    else:
                        print "The list of available images on the OpenStack located on " + str(args.openstack) + " is:"
                        for i in output:                       
                            print i  
                        print "You can get more details by querying the image repository using fg-repo -q command and the query string: \"* where tag=imagename\". \n" + \
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img.manifest.xml"
            elif args.justregister:
                output = imgregister.iaas_justregister(args.openstack, image, image_source, args.ramdisk, "openstack", varfile, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
            elif args.deregister:
                output = imgregister.cloudremove(str(args.euca), "openstack",varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output
            else:    
                output = imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, args.getimg, ldap, args.wait)
                if output != None:
                    if re.search("^ERROR", output):
                        print output
        else:
            print "ERROR: You need to specify the targeted infrastructure where your image will be registered"

def checkVarFile(varfile, getimg, listkernels, text):
    if not getimg and not listkernels:
        if varfile == "":
            print "ERROR: You need to specify the path of the file with the " + text + " environment variables"
            sys.exit(1)
        elif not os.path.isfile(varfile):
            print "ERROR: Variable files not found. You need to specify the path of the file with the " + text + " environment variables"    
            sys.exit(1)
            
    return True
    
if __name__ == "__main__":
    main()
#END


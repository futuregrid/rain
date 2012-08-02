#/usr/bin/env python
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
Service proxy in the client side.

Before the SOA is implemented, this contains the concrete functional access
that supposed to reside in the service side. When the web service is used,
this will serve as a proxy that talks to the service in the server side.
"""

__author__ = 'Javier Diaz, Fugang Wang'

import os
import time
import string
import sys
from random import randrange
import socket,ssl
import hashlib
from getpass import getpass
import re

from futuregrid.image.repository.client.IRTypes import ImgMeta
from futuregrid.image.repository.client.IRTypes import ImgEntry
from futuregrid.image.repository.client.IRTypes import IRUser
from futuregrid.image.repository.client.IRClientConf import IRClientConf
from futuregrid.utils import fgLog 

class IRServiceProxy(object):

    #(Now we assume that the server is where the images are stored. We may want to change that)    
    ############################################################
    # __init__
    ############################################################
    def __init__(self, verbose, printLogStdout):
        super(IRServiceProxy, self).__init__()

        #Load Config
        self._conf = IRClientConf()
        #self._backend = self._conf.getBackend()
        #self._fgirimgstore = self._conf.getFgirimgstore()
        self._port = self._conf.getPort()
        self._serveraddr = self._conf.getServeraddr()
        self.verbose = verbose
        
        self._ca_certs = self._conf.getCaCerts()
        self._certfile = self._conf.getCertFile()
        self._keyfile = self._conf.getKeyFile()
        
        self._connIrServer = None
        
        self.passwdtype = "ldappassmd5"
        #Setup log
        self._log = fgLog.fgLog(self._conf.getLogFile(), self._conf.getLogLevel(), "Img Repo Client", printLogStdout)
        

    def connection(self):
        connected = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._connIrServer = ssl.wrap_socket(s,
                                        ca_certs=self._ca_certs,
                                        certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            self._log.debug("Connecting server: " + self._serveraddr + ":" + str(self._port))
            self._connIrServer.connect((self._serveraddr, self._port))   
            connected = True         
        except ssl.SSLError:
            self._log.error("CANNOT establish SSL connection. EXIT")
        except socket.error:
            self._log.error("Error with the socket connection")
        except:
            if self.verbose:
                print "Error CANNOT establish connection with the server"
            self._log.error("ERROR: exception not controlled" + str(sys.exc_info()))
            
        
        return connected
        #irServer.write(options) #to be done in each method
    def disconnect(self):
        try:
            self._connIrServer.shutdown(socket.SHUT_RDWR)
            self._connIrServer.close()
        except:            
            self._log.debug("In disconnect:" + str(sys.exc_info()))
    
    def isUserAdmin(self, userId, passwd, userIdB):
        """
        return True or False
        """
        start = time.time()
        
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|isUserAdmin|" + userIdB
        self._connIrServer.write(msg)
        authstatus=self.check_auth(userId, checkauthstat)
        if authstatus == True:
            #wait for output
            output = eval(self._connIrServer.read(1024))            
        else:
            output=str(checkauthstat[1])
            self._log.error(str(checkauthstat[0]))
                    
        end = time.time()
        self._log.info('TIME query:' + str(end - start))
        
        return output
    
    def getUserStatus(self, userId, passwd, userIdB): #this is used by other services to check the status of the user before checking passwd in ldap
        """
        return "Active", "NoActive" or "NoUser"
        """
        start = time.time()
        
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|getUserStatus|" + userIdB
        self._connIrServer.write(msg)
        authstatus=self.check_auth(userId, checkauthstat)
        if authstatus == True:
            #wait for output
            output = self._connIrServer.read(32768)            
                 
        else:
            output=str(checkauthstat[1])
            self._log.error(str(checkauthstat[0]))
                    
        end = time.time()
        self._log.info('TIME query:' + str(end - start))
        
        return output
        
    
    def check_auth(self, userId, checkauthstat):
        endloop = False
        passed = False
        while not endloop:
            ret = self._connIrServer.read(1024)
            if (ret == "OK"):
                if self.verbose:
                    print "Authentication OK. Your request is being processed"
                self._log.debug("Authentication OK")
                endloop = True
                passed = True
            elif (ret == "TryAuthAgain"):
                msg = "ERROR: Permission denied, please try again. User is " + userId                    
                self._log.error(msg)
                if self.verbose:
                    print msg                            
                m = hashlib.md5()
                m.update(getpass())
                passwd = m.hexdigest()
                self._connIrServer.write(passwd)
            elif (ret == "NoActive"):                
                checkauthstat.append("ERROR: The status of the user "+ userId + " is not active")
                checkauthstat.append("NoActive")
                self._log.error("The status of the user "+ userId + " is not active")
                endloop = True
                passed = False
            elif (ret == "NoUser"):
                checkauthstat.append("ERROR: User "+ userId + " does not exist")
                checkauthstat.append("NoUser")
                self._log.error("User "+ userId + " does not exist")
                endloop = True
                passed = False
            else:                
                self._log.error(str(ret))
                #if self.verbose:
                #    print ret
                checkauthstat.append(str(ret))
                endloop = True
                passed = False
        return passed
        
    ############################################################
    # query
    ############################################################
    def query(self, userId, passwd, userIdB, queryString):   
        """
        userId: user that authenticate against the repository.
        password: password of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        
        start = time.time()
        
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|list|" + userIdB + "|" + queryString
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            data = self._connIrServer.read(32768)
            if data:
                output = str(data)            
            while data:
                data = self._connIrServer.read(32768)
                if data:
                    output += str(data)            
            if output == "None":
                output = None
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        
        end = time.time()
        self._log.info('TIME query:' + str(end - start))
        
        return output
            
    ############################################################
    # get
    ############################################################
    def get(self, userId, passwd, userIdB, option, imgId, dest):
        """
        userId: user that authenticate against the repository.
        password: password of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """  
        start = time.time()
        checkauthstat = []      
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|get|" + userIdB + "|" + option + "|" + imgId
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            output = self._connIrServer.read()
            if not output == 'None':
                output = self._serveraddr + ":" + output
                if (option == "img"):
                    output = self._retrieveImg(userId, imgId, output, dest)
                    if output != None:
                        self._connIrServer.write('OK')
                    else:#this should be used to retry retrieveImg
                        self._connIrServer.write('Fail')
            else:
                output = None
        else:
            output = None
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        
        end = time.time()
        self._log.info('TIME get:' + str(end - start))
               
        return output
    
    ############################################################
    # put
    ############################################################
    def put(self, userId, passwd, userIdB, imgFile, attributeString):
        """
        userId: user that authenticate against the repository.
        password: password of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        
        output:
        0 is general error
        """
        start = time.time()
        status = "0"
        if (self.checkMeta(attributeString) and os.path.isfile(imgFile)):
            
            status = "0"
            output = ""
            checkauthstat = []
            
            size = os.path.getsize(imgFile)
            extension = os.path.splitext(imgFile)[1].strip() 
                        
            if self.verbose:
                print "Checking quota and Generating an ImgId"
            msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|put|" + userIdB + "|" + str(size) + "|" + extension +\
                 "|" + attributeString
            self._connIrServer.write(msg)
            
            authstatus = self.check_auth(userId, checkauthstat)
            self._log.debug("Auth in server status "+str(authstatus))
            if authstatus:
                #wait for "OK,tempdir,imgId" or error status                
                output = self._connIrServer.read(2048)
                self._log.debug("after auth, repo server answer: "+str(output))
                #print output
                if not (re.search('^ERROR', output)):
                    output = output.split(',')                    
                    imgStore = output[0] 
                    imgId = output[1]
                    fileLocation = imgStore + imgId
                    self._log.info("Uploading the image")
                    os.system("chmod +r " + fileLocation)
                    if self.verbose:
                        print 'Uploading image. You may be asked for ssh/passphrase password'
                        cmd = 'scp ' + imgFile + " " + \
                            self._serveraddr + ":" + imgFile
                    else:#this is the case where another application call it. So no password or passphrase is allowed
                        cmd = 'scp -q -oBatchMode=yes ' + imgFile + " " + \
                            self._serveraddr + ":" + fileLocation
                    stat = os.system(cmd)
                    if (str(stat) != "0"):
                        self._log.error(str(stat))
                        self._connIrServer.write("Fail")
                    else:
                        if self.verbose:
                            print "Registering the image"                            
                        msg = fileLocation
                        self._connIrServer.write(msg)
                        #wait for final output
                        status = self._connIrServer.read(2048)
                        if status == "0":    
                            status = "ERROR: uploading image to the repository. File does not exists or metadata string is invalid"
                else:
                    status = output
            else:
                self._log.error("ERROR:auth failed "+str(checkauthstat[0]))
                status = checkauthstat[0]
        else:
            status = "ERROR: uploading image to the repository. File does not exists or metadata string is invalid"
        
        end = time.time()
        self._log.info('TIME put:' + str(end - start))
        return status
        
    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, userId, passwd, userIdB, imgId, attributeString):
        """
        userId: user that authenticate against the repository.
        password: password of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        success = "False"
        if (self.checkMeta(attributeString)):       
            msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|modify|" + userIdB + "|" + imgId + "|" + attributeString
            self._connIrServer.write(msg)
            if self.check_auth(userId, checkauthstat):
                #wait for output
                output = self._connIrServer.read(2048)
            else:
                self._log.error(str(checkauthstat[0]))
                if self.verbose:
                    print checkauthstat[0]
        end = time.time()
        self._log.info('TIME modify:' + str(end - start))  
        return output
    
    ############################################################
    # remove
    ############################################################
    def remove(self, userId, passwd, userIdB, imgIdList):
        """
        userId: user that authenticate against the repository.
        passwd: password of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        
        imgList=" ".join(imgIdList)
        
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|remove|" + userIdB + "|" + imgList
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            output = self._connIrServer.read(2048)
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
                
        end = time.time()
        self._log.info('TIME remove:' + str(end - start))
        
        return output
    
            
    ############################################################
    # setPermission
    ############################################################
    def setPermission(self, userId, passwd, userIdB, imgId, permission):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []        
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|setPermission|" + userIdB + "|" + imgId + "|" + permission
        if(permission in ImgMeta.Permission):
            self._connIrServer.write(msg)
            if self.check_auth(userId, checkauthstat):
                #wait for output
                output = self._connIrServer.read(2048)
            else:
                self._log.error(str(checkauthstat[0]))
                if self.verbose:
                    print checkauthstat[0]
        else:
            output = "Available options: " + str(ImgMeta.Permission)
        end = time.time()
        self._log.info('TIME setpermission:' + str(end - start))
        return output
    
    ############################################################
    # userAdd
    ############################################################
    def userAdd(self, userId, passwd, userIdB, userIdtoAdd):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|useradd|" + userIdB + "|" + userIdtoAdd
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            output = self._connIrServer.read(2048)
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        end = time.time()
        self._log.info('TIME adduser:' + str(end - start)) 
        return output
        
    ############################################################
    # userDel
    ############################################################
    def userDel(self, userId, passwd, userIdB, userIdtoDel):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|userdel|" + userIdB + "|" + userIdtoDel
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            output = self._connIrServer.read(2048)
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        end = time.time()
        self._log.info('TIME deluser:' + str(end - start))
        return output

    ############################################################
    # userList
    ############################################################
    def userList(self, userId, passwd, userIdB):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|userlist|" + userIdB 
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            data = self._connIrServer.read(32768)
            if data:
                output = str(data)            
            while data:
                data = self._connIrServer.read(32768)
                if data:
                    output += str(data)
                
            if output == "None":
                output = None
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        end = time.time()
        self._log.info('TIME userlist:' + str(end - start))
        return output

    ############################################################
    # setUserQuota    
    ############################################################
    def setUserQuota(self, userId, passwd, userIdB, userIdtoModify, quota):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        try:
            quotanum = str(eval(quota))
            msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|setUserQuota|" + userIdB + "|" + userIdtoModify + "|" + quotanum
            self._connIrServer.write(msg)
            if self.check_auth(userId, checkauthstat):
                #wait for output
                output = self._connIrServer.read(2048)
            else:
                self._log.error(str(checkauthstat[0]))
                if self.verbose:
                    print checkauthstat[0]
        except:
            if self.verbose:
                print "ERROR: evaluating the quota. It must be a number or a mathematical operation enclosed in \"\" characters"        
        end = time.time()
        self._log.info('TIME userquota:' + str(end - start))
        return output


    ############################################################
    # setUserRole
    ############################################################
    def setUserRole(self, userId, passwd, userIdB, userIdtoModify, role):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []        
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|setUserRole|" + userIdB + "|" + userIdtoModify + "|" + role
        if(role in IRUser.Role):
            self._connIrServer.write(msg)
            if self.check_auth(userId, checkauthstat):
                #wait for output
                output = self._connIrServer.read(2048)
            else:
                self._log.error(str(checkauthstat[0]))
                if self.verbose:
                    print checkauthstat[0]
        else:
            output = "Available options: " + str(IRUser.Role)
             
        end = time.time()
        self._log.info('TIME userrole:' + str(end - start))   
        return output
        
        
    ############################################################
    # setUserStatus
    ############################################################
    def setUserStatus(self, userId, passwd, userIdB, userIdtoModify, status):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []        
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|setUserStatus|" + userIdB + "|" + userIdtoModify + "|" + status
        if(status in IRUser.Status):
            self._connIrServer.write(msg)
            if self.check_auth(userId, checkauthstat):
                #wait for output
                output = self._connIrServer.read(2048)
            else:
                self._log.error(str(checkauthstat[0]))
                if self.verbose:
                    print checkauthstat[0]
        else:
            output = "Available options: " + str(IRUser.Status)
        end = time.time()
        self._log.info('TIME userstatus:' + str(end - start))       
        return output
        

    ############################################################
    # histImg
    ############################################################
    def histImg(self, userId, passwd, userIdB, imgId):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|histimg|" + userIdB + "|" + imgId
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            data = self._connIrServer.read(32768)
            if data:
                output = str(data)            
            while data:
                data = self._connIrServer.read(32768)
                if data:
                    output += str(data)
            if output == "None":
                output = None
        else:
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        end = time.time()
        self._log.info('TIME histimg:' + str(end - start))    
        return output

    ############################################################
    # histUser
    ############################################################
    def histUser(self, userId, passwd, userIdB, userIdtoSearch):
        """
        userId: user that authenticate against the repository.
        passwd: passwd of the previous user
        userIdB: user that execute the command in the repository.         
        
        Typically, userId and userIdB are the same user. However, they are different when the repo 
        is used by a service like IMGenerateServer or IMRegisterServer, because these services interact 
        with the repo in behalf of other users.
        """
        start = time.time()
        checkauthstat = []
        output = None
        msg = userId + "|" + str(passwd) + "|" + self.passwdtype + "|histuser|" + userIdB + "|" + userIdtoSearch
        self._connIrServer.write(msg)
        if self.check_auth(userId, checkauthstat):
            #wait for output
            data = self._connIrServer.read(32768)
            if data:
                output = str(data)            
            while data:
                data = self._connIrServer.read(32768)
                if data:
                    output += str(data)
            if output == "None":
                output = None
        else:
            #TODO: GVL: should this be a function, it seems to be reused often 
            self._log.error(str(checkauthstat[0]))
            if self.verbose:
                print checkauthstat[0]
        end = time.time()
        self._log.info('TIME histuser:' + str(end - start)) 
        return output
    
    ############################################################
    # checkMeta
    ############################################################
    def checkMeta(self, attributeString):
        attributes = attributeString.split("&")
        correct = True
        for item in attributes:
            attribute = item.strip()
            #print attribute
            tmp = attribute.split("=")
            if (len(tmp) == 2):
                key = string.lower(tmp[0])
                value = tmp[1]
                if key in ImgMeta.metaArgsIdx.keys():
                    if (key == "vmtype"):
                        value = string.lower(value)
                        if not (value in ImgMeta.VmType):
                            self._log.error("Wrong value for VmType, please use: " + str(ImgMeta.VmType))
                            if self.verbose:
                                print "Wrong value for VmType, please use: " + str(ImgMeta.VmType)
                            correct = False
                            break
                    elif (key == "imgtype"):
                        value = string.lower(value)
                        if not (value in ImgMeta.ImgType):
                            self._log.error("Wrong value for ImgType, please use: " + str(ImgMeta.ImgType))
                            if self.verbose:
                                print "Wrong value for ImgType, please use: " + str(ImgMeta.ImgType)
                            correct = False
                            break
                    elif(key == "permission"):
                        value = string.lower(value)
                        if not (value in ImgMeta.Permission):
                            self._log.error("Wrong value for Permission, please use: " + str(ImgMeta.Permission))
                            if self.verbose:
                                print "Wrong value for Permission, please use: " + str(ImgMeta.Permission)
                            correct = False
                            break
                    elif (key == "imgstatus"):
                        value = string.lower(value)
                        if not (value in ImgMeta.ImgStatus):
                            self._log.error("Wrong value for ImgStatus, please use: " + str(ImgMeta.ImgStatus))
                            if self.verbose:
                                print "Wrong value for ImgStatus, please use: " + str(ImgMeta.ImgStatus)
                            correct = False
                            break
                else:
                    self._log.warning("Wrong attribute: "+key)
                    if self.verbose:
                        print "WARNING: Attribute "+key+" is invalid. It will be ignored."
        return correct
    """
    ############################################################
    # _rExec
    ############################################################
    def _rExec(self, userId, cmdexec):

        #TODO: do we want to use the .format statement from python to make code more readable?

        #cmdssh = "ssh " + userId + "@" + self._serveraddr
        cmdssh = "ssh " + self._serveraddr
        tmpFile = "/tmp/" + str(time()) #+ str(self.randomId())
        #print tmpFile
        cmdexec = cmdexec + " > " + tmpFile
        cmd = cmdssh + cmdexec
        #print cmd
        stat = os.system(cmd)
        if (str(stat) != "0"):
            self._log.error(str(stat))
            if self.verbose:
                print stat
        f = open(tmpFile, "r")
        outputs = f.readlines()
        #print outputs
        f.close()
        os.system("rm -rf " + tmpFile)
        #output = ""
        #for line in outputs:
        #    output += line.strip()
        #print outputs
        return outputs
    """
    ############################################################
    # _retrieveImg
    ############################################################
    def _retrieveImg(self, userId, imgId, imgURI, dest):
        
        extension = os.path.splitext(imgURI)[1]
        extension = string.split(extension, "_")[0]
        
        fulldestpath = dest + "/" + imgId + "" + extension
                
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
                
    
        if self.verbose:
            #cmdscp = "scp " + userId + "@" + imgURI + " " + fulldestpath
            cmdscp = "scp " + imgURI + " " + fulldestpath
        else:
            #cmdscp = "scp -q " + userId + "@" + imgURI + " " + fulldestpath
            cmdscp = "scp -q -oBatchMode=yes " + imgURI + " " + fulldestpath
        #print cmdscp
        self._log.debug(cmdscp)
        output = ""
        try:
            self._log.debug('Retrieving image. You may be asked for ssh/passphrase password')
            
            if self.verbose:
                print 'Retrieving image. You may be asked for ssh/passphrase password'
            stat = os.system(cmdscp)
            if (stat == 0):
                output = fulldestpath                
            else:
                self._log.error("Error retrieving the image. Exit status " + str(stat))
                if self.verbose:
                    print "Error retrieving the image. Exit status " + str(stat)
                #remove the temporal file
        except os.error:
            #GVL: TODO: should this be a function:
            self._log("Error, The image cannot be retieved" + str(sys.exc_info()))
            if self.verbose:
                print "Error, The image cannot be retieved" + str(sys.exc_info())
            output = None

        return output
     
    #def randomId(self):
    #    Id = str(randrange(999999999999999999999999))
    #    return Id

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
Image repository server

"""
__author__ = 'Javier Diaz, Fugang Wang'

import os, sys
import string
from multiprocessing import Process
import socket, ssl
import logging
import time

from futuregrid.image.repository.server.IRService import IRService



class IRServer(object):

    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(IRServer, self).__init__()

        self.numparams = 4

        self._service = IRService()
        self._log = self._service.getLog()
        self._repoconf = self._service.getRepoConf()

        self.port = self._repoconf.getPort()
        self.proc_max = self._repoconf.getProcMax()
        self.refresh_status = self._repoconf.getRefreshStatus()
        self._authorizedUsers = self._repoconf.getAuthorizedUsers()    
        self._nopasswdusers = self._repoconf.getNoPasswdUsers()
        
        self._ca_certs = self._repoconf.getCaCerts()
        self._certfile = self._repoconf.getCertFile()
        self._keyfile = self._repoconf.getKeyFile()
        
    def start(self):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(1) #Maximum of system unaccepted connections. Maximum value depend of the system (usually 5) 
        self._log.info('Starting Server on port ' + str(self.port))        
        proc_list = []
        total_count = 0
        while True:            
            if len(proc_list) == self.proc_max:
                full = True
                while full:
                    for i in range(len(proc_list) - 1, -1, -1):
                        #self._log.debug(str(proc_list[i]))
                        if not proc_list[i].is_alive():
                            #print "dead"                        
                            proc_list.pop(i)
                            #put here terminate?? just in case the process is not done but neither alive?? I have noticed that when IOError the process keep running
                            full = False
                    if full:
                        time.sleep(self.refresh_status)
            
            total_count += 1            
            #channel, details = sock.accept()
            newsocket, fromaddr = sock.accept()            
            connstream = None
            try:
                connstream = ssl.wrap_socket(newsocket,
                              server_side=True,
                              ca_certs=self._ca_certs,
                              cert_reqs=ssl.CERT_REQUIRED,
                              certfile=self._certfile,
                              keyfile=self._keyfile,
                              ssl_version=ssl.PROTOCOL_TLSv1)
                #print connstream                                
                proc_list.append(Process(target=self.repo, args=(connstream, fromaddr[0],)))            
                proc_list[len(proc_list) - 1].start()
            except ssl.SSLError:
                self._log.error("Unsuccessful connection attempt from: " + repr(fromaddr) + " " + str(sys.exc_info()))
            except socket.error:
                self._log.error("Error with the socket connection")
            except:
                self._log.error("Uncontrolled Error: " + str(sys.exc_info()))
                if type(connstream) is ssl.SSLSocket: 
                    connstream.shutdown(socket.SHUT_RDWR)
                    connstream.close()
                     
    #def auth(self, userCred):
    #    return FGAuth.auth(self.user, userCred)        
      
    def checknopasswd(self, fromaddr):
        status = False
        if self.user in self._nopasswdusers:
            if fromaddr in self._nopasswdusers[self.user]:
                status = True
        return status
     
    def repo(self, channel, fromaddr):
        
        self._log = self._log.getLogger("Img Repo Server." + str(os.getpid()))
        
        self._service.setLog(self._log)
        
        self._log.info('Processing request')
        
        #receive the message
        data = channel.read(2048)
        
        self._log.debug("received data: " + data)
        
        params = data.split('|')

        #params[0] is user that authenticates  
        #params[1] is the user password
        #params[2] is the type of password
        #params[3] is the command
        #params[4] is the user that interact with the repo. Usually is the same that params[0]
        #params[5...] are the options 

        if (len(params) <= self.numparams):
            msg = "ERROR: Invalid Number of Parameters"    
            self.errormsg(channel, msg)
            sys.exit(1)
        
        self.user = params[0].strip() #ONLY for authentication. To specify the user that call methods you need to use params[4]
        passwd = params[1].strip()
        passwdtype = params[2].strip()
        command = params[3].strip()
                
        for i in range(len(params)):
            params[i] = params[i].strip()

        
        if not self.user in self._authorizedUsers:
            if not (self.user == params[4]):
                msg = "ERROR: You are not authorized to act in behalf of other user"    
                self.errormsg(channel, msg)
                sys.exit(1)
        
        
        retry = 0
        maxretry = 3
        endloop = False
        while (not endloop):
            #userCred = FGCredential(passwd, passwdtype)
            if not self.checknopasswd(fromaddr):
                status = self._service.auth(self.user, passwd, passwdtype)
                if status == True:
                    channel.write("OK")
                    endloop = True
                elif status == False:
                    #_authorizedUsers is not used currently. If we want to activate it, we need to make sure that the authizedUsers are in the Repository database
                    if self.user in self._authorizedUsers: #because these users are services that cannot retry.
                        msg = "ERROR: authentication failed"                    
                        self.errormsg(channel, msg)
                        sys.exit(1)
                    else:
                        msg = "ERROR: authentication failed. Try again"
                        self._log.error(msg)
                        retry += 1
                        if retry < maxretry:
                            channel.write("TryAuthAgain")
                            passwd = channel.read(2048)
                        else:
                            msg = "ERROR: authentication failed"                        
                            self.errormsg(channel, msg)
                            sys.exit(1)                
                else:
                    msg = status #this is NoActive or NoUser                
                    self.errormsg(channel, msg)
                    sys.exit(1)
            else:
                channel.write("OK")
                endloop = True
                
        needtoclose = False      
        if (command == "list"):
            if (len(params) == self.numparams + 2):
                #user, query string
                #print params[5]
                output = self._service.query(params[4], params[5])                
                channel.write(str(output))
                needtoclose = True
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)        
        elif (command == "get"):
            #user, img/uri, imgid
            if (len(params) == self.numparams + 3):
                output = self._service.get(params[4], params[5], params[6])
                channel.write(str(output))
                if output != None:
                    status = channel.read(1024) ##just to wait for client answer.
                    if status != 'OK':
                        self._log.error("ERROR: Client did not receive the image")
                        needtoclose = False
                    else:
                        needtoclose = True                 
                    if (self._service.getBackend() != "mysql"):
                        cmdrm = " rm -f " + output             
                        self._log.debug("Deleting Temporal file: " + cmdrm)           
                        os.system(cmdrm)                
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "put"):
            #user, img_size, extension, attributeString   
            if (len(params) == self.numparams + 4):
                self._log.debug("Before uploadValidator ")
                output = self._service.uploadValidator(params[4], long(params[5]))
                self._log.debug("After uploadValidator "+str(output))                
                if str(output) == 'True':
                    self._log.debug("Before genImgId ")                               
                    imgId = self._service.genImgId()
                    self._log.debug("After genImgId "+str(imgId))
                    if imgId != None:
                        self._log.debug("sending to the client: "+str(self._service.getImgStore())+ " , "+str(imgId))
                        channel.write(self._service.getImgStore() + "," + str(imgId))
                        self._log.debug("sent and waiting in the read")
                        #waiting for client to upload image
                        output = channel.read(2048)                    
                        if output != 'Fail':
                            #user, imgId, imgFile(uri), attributeString, size, extension
                            output = self._service.put(params[4], imgId, output, params[7], long(params[5]), params[6])
                            channel.write(str(output))
                            needtoclose = True
                        else:
                            os.system("rm -f "+self._service.getImgStore() + "/" + str(imgId))
                            self._log.debug("rm -f "+self._service.getImgStore() + "/" + str(imgId))                    
                    else:
                        channel.write()
                        msg = "ERROR: The imgId generation failed"
                        self.errormsg(channel, msg)
                else:
                    output = str(output)
                    if output == "NoUser":                    
                        status = "ERROR: The User does not exist"
                    elif (output == "NoActive"):                    
                        status = "ERROR: The User is not active"
                    elif (output == 'False'):
                        status = "ERROR: The file exceed the quota"
                    else:
                        status = "ERROR: " + output
                    msg = status
                    self.errormsg(channel, msg)
            else:
                msg = "ERROR: Invalid Number of Parameters"
                self.errormsg(channel, msg)    
            #send storage directory, temporal or not
            #receive the OK, meaning that the image is already there
        elif (command == "modify"):
            #userid, imgid, attributestring
            if (len(params) == self.numparams + 3):
                output = self._service.updateItem(params[4], params[5], params[6])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "remove"):
            #user, imgids list separated by spaces
            if (len(params) == self.numparams + 2):
                output = self._service.remove(params[4], params[5])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "setPermission"):
            #user, imgid, query
            if (len(params) == self.numparams + 3):                
                output = self._service.updateItem(params[4], params[5], "permission=" + params[6])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "histimg"):
            #userId, imgId
            if (len(params) == self.numparams + 2):
                output = self._service.histImg(params[4], params[5])
                channel.write(str(output))                
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "histuser"):
            #userId, userId
            if (len(params) == self.numparams + 2):
                output = self._service.histUser(params[4], params[5])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        #elif (command == "uploadValidator"):
        #    #user, size of the img to upload
        #    if (len(optionlist) != 2):
        #        output = self._service.uploadValidator(optionlist[0], long(optionlist[1]))
        #        channel.write(str(output))
        #    else:
        #        msg = "Invalid Number of Parameters"
        #        self.errormsg(channel, msg)
        #elif (command == "genImgId"):
        #    if (len(optionlist) != 1):
        #        output = self._service.genImgId()
        #        channel.write(str(output))
        #    else:
        #        msg = "Invalid Number of Parameters"
        #        self.errormsg(channel, msg)
        elif (command == "getBackend"):
            if (len(params) == self.numparams + 1):
                output = self._service.getBackend()
                output1 = self._service.getImgStore()
                channel.write(str(output) + str(output1))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "useradd"):
            #userid, useridtoadd
            if (len(params) == self.numparams + 2):
                output = self._service.userAdd(params[4], params[5])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "userdel"):
            #userid, useridtodel
            if (len(params) == self.numparams + 2):
                output = self._service.userDel(params[4], params[5])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "userlist"):
            #userid
            if (len(params) == self.numparams + 1):
                output = self._service.userList(params[4])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "setUserQuota"):
            #userid, useridtomodify, quota in bytes
            if (len(params) == self.numparams + 3):
                output = self._service.setUserQuota(params[4], params[5], long(params[6]))
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "setUserRole"):
            #userid, useridtomodify, role
            if (len(params) == self.numparams + 3):
                output = self._service.setUserRole(params[4], params[5], params[6])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "setUserStatus"):
            if (len(params) == self.numparams + 3):
                output = self._service.setUserStatus(params[4], params[5], params[6])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        elif (command == "getUserStatus"):
            #userId
            if (len(params) == self.numparams + 1):
                output = self._service.getUserStatus(params[4])
                channel.write(str(output))
            else:
                msg = "Invalid Number of Parameters"
                self.errormsg(channel, msg)
        else:
            msg = "Invalid Command: " + command
            self.errormsg(channel, msg)
            needtoclose = False
        
        if needtoclose:
            channel.shutdown(socket.SHUT_RDWR)
            channel.close()
            self._log.info("Image Repository Request DONE")
        else:
            self._log.info("Image Repository Request DONE")
        
    def errormsg(self, channel, msg):
        self._log.error(msg)
        try:        
            channel.write(msg)                    
            channel.shutdown(socket.SHUT_RDWR)
            channel.close()
        except:
            self._log.debug("In errormsg: " + str(sys.exc_info()))
        self._log.info("Image Repository Request DONE")
        
def main():
    
    server = IRServer()
    server.start()
    
if __name__ == "__main__":
    main()

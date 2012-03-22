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
Service interface in the server side.

"""
__author__ = 'Fugang Wang, Javier Diaz'

import cherrypy
from cherrypy.lib import cptools
import os, sys
import os.path
import re
import string
from datetime import datetime

from futuregrid.image.repository.server.IRTypes import ImgMeta
from futuregrid.image.repository.server.IRTypes import ImgEntry
from futuregrid.image.repository.server.IRTypes import IRUser
from futuregrid.image.repository.server.IRServerConf import IRServerConf
import futuregrid.image.repository.server.IRUtil
from futuregrid.utils.FGTypes import FGCredential
from futuregrid.utils import FGAuth, fgLog

class IRService(object):

    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(IRService, self).__init__()

        #load config
        self._repoConf = IRServerConf()
        self._repoConf.loadRepoServerConfig()
        
        #self._authorizedUsers=self._repoConf.getAuthorizedUsers()  #to be removed    
        self._backend = self._repoConf.getBackend()
        
        self._address = self._repoConf.getAddress()
        self._userAdmin = self._repoConf.getUserAdmin()
        self._configFile = self._repoConf.getConfigFile()        
        self._imgStore = self._repoConf.getImgStore()
        self._addressS = self._repoConf.getAddressS()
        self._userAdminS = self._repoConf.getUserAdminS()
        self._configFileS = self._repoConf.getConfigFileS()
        #self._idp = self._repoConf.getIdp()
        
        print "\nReading Configuration file from " + self._repoConf.getServerConfig() + "\n"
        
        #Setup log. 
        #When integrate ALL FG software, we may need to create this somewhere else and send the log object to all classes like this        
        self._log = fgLog.fgLog(self._repoConf.getLogRepo(), self._repoConf.getLogLevelRepo(), "Img Repo Server", False)
        
        if (self._backend == "mongodb"):
            from IRDataAccessMongo import ImgStoreMongo
            from IRDataAccessMongo import ImgMetaStoreMongo
            from IRDataAccessMongo import IRUserStoreMongo
            self.metaStore = ImgMetaStoreMongo(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreMongo(self._address, self._userAdmin, self._configFile, self._imgStore, self._log)
            self.userStore = IRUserStoreMongo(self._address, self._userAdmin, self._configFile, self._log)
        elif(self._backend == "mysql"):
            from IRDataAccessMysql import ImgStoreMysql
            from IRDataAccessMysql import ImgMetaStoreMysql
            from IRDataAccessMysql import IRUserStoreMysql
            self.metaStore = ImgMetaStoreMysql(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreMysql(self._address, self._userAdmin, self._configFile, self._imgStore, self._log)
            self.userStore = IRUserStoreMysql(self._address, self._userAdmin, self._configFile, self._log)
        elif(self._backend == "swiftmysql"):
            from IRDataAccessSwiftMysql import ImgStoreSwiftMysql
            from IRDataAccessSwiftMysql import ImgMetaStoreSwiftMysql
            from IRDataAccessSwiftMysql import IRUserStoreSwiftMysql
            self.metaStore = ImgMetaStoreSwiftMysql(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreSwiftMysql(self._address, self._userAdmin, self._configFile, self._addressS, self._userAdminS, self._configFileS, self._imgStore, self._log)
            self.userStore = IRUserStoreSwiftMysql(self._address, self._userAdmin, self._configFile, self._log)
        elif(self._backend == "swiftmongo"):
            from IRDataAccessSwiftMongo import ImgStoreSwiftMongo
            from IRDataAccessSwiftMongo import ImgMetaStoreSwiftMongo
            from IRDataAccessSwiftMongo import IRUserStoreSwiftMongo
            self.metaStore = ImgMetaStoreSwiftMongo(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreSwiftMongo(self._address, self._userAdmin, self._configFile, self._addressS, self._userAdminS, self._configFileS, self._imgStore, self._log)
            self.userStore = IRUserStoreSwiftMongo(self._address, self._userAdmin, self._configFile, self._log)
        elif(self._backend == "cumulusmysql"):
            from IRDataAccessCumulusMysql import ImgStoreCumulusMysql
            from IRDataAccessCumulusMysql import ImgMetaStoreCumulusMysql
            from IRDataAccessCumulusMysql import IRUserStoreCumulusMysql
            self.metaStore = ImgMetaStoreCumulusMysql(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreCumulusMysql(self._address, self._userAdmin, self._configFile, self._addressS, self._userAdminS, self._configFileS, self._imgStore, self._log)
            self.userStore = IRUserStoreCumulusMysql(self._address, self._userAdmin, self._configFile, self._log)
        elif(self._backend == "cumulusmongo"):
            from IRDataAccessCumulusMongo import ImgStoreCumulusMongo
            from IRDataAccessCumulusMongo import ImgMetaStoreCumulusMongo
            from IRDataAccessCumulusMongo import IRUserStoreCumulusMongo
            self.metaStore = ImgMetaStoreCumulusMongo(self._address, self._userAdmin, self._configFile, self._log)
            self.imgStore = ImgStoreCumulusMongo(self._address, self._userAdmin, self._configFile, self._addressS, self._userAdminS, self._configFileS, self._imgStore, self._log)
            self.userStore = IRUserStoreCumulusMongo(self._address, self._userAdmin, self._configFile, self._log)
        else:
            self.metaStore = ImgMetaStoreFS()
            self.imgStore = ImgStoreFS()
            self.userStore = IRUserStoreFS()

    def getRepoConf(self):
        return self._repoConf

    def genImgId(self):
        """
        return None if it could not get an imgId
        """
        return self.metaStore.genImgId()

    def getLog(self):
        return self._log
    def setLog(self, log):
        self._log = log
    def getAuthorizedUsers(self):
        return self._authorizedUsers
    def getBackend(self):
        return self._backend
    def getImgStore(self):
        return self._imgStore

    
    def auth(self, userId, userCred, provider):
        """
        return True, False, "NoActive", "NoUser"
        """
        cred = FGCredential(provider, userCred)
        status = FGAuth.auth(userId, cred)
        if status:
            userstatus=self.userStore.getUserStatus(userId)
            if userstatus=="Active":
                self.userStore.updateLastLogin(userId)
            else:
                status=userstatus        
                    
        return status

    ############################################################
    # getUserStatus
    ############################################################
    def getUserStatus(self,userId):
        """
        This is to verify the status of a user. 
        This method should be called by the auth method.
        return "Active", "NoActive" or "NoUser"
        """
        self._log.info("user:" + userId + " command:getUserStatus args={userId:" + userId + "}")
        return self.userStore.getUserStatus(userId)
    
    ############################################################
    # uploadValidator
    ############################################################
    def uploadValidator(self, userId, size):
        self._log.info("user:" + userId + " command:uploadValidator args={size:" + str(size) + "}")
        return self.userStore.uploadValidator(userId, size)

    ############################################################
    # userAdd
    ############################################################
    def userAdd(self, userId, username):
        self._log.info("user:" + userId + " command:userAdd args={userIdtoAdd:" + username + "}")
        user = IRUser(username)
        return self.userStore.userAdd(userId, user)

    ############################################################
    # userDel
    ############################################################
    def userDel(self, userId, userIdtoDel):
        self._log.info("user:" + userId + " command:userDel args={userIdtoDel:" + userIdtoDel + "}")
        return self.userStore.userDel(userId, userIdtoDel)

    ############################################################
    # userList
    ############################################################
    def userList(self, userId):
        self._log.info("user:" + userId + " command:userlist")
        return self.userStore.queryStore(userId, None)

    ############################################################
    # setUserRole
    ############################################################
    def setUserRole(self, userId, userIdtoModify, role):
        self._log.info("user:" + userId + " command:setUserRole args={userIdtoModify:" + userIdtoModify + ", role:" + role + "}")
        if (role in IRUser.Role):
            return self.userStore.setRole(userId, userIdtoModify, role)
        else:
            self._log.error("Role " + role + " is not valid")
            print "Role not valid. Valid roles are " + str(IRUser.Role)
            return False

    ############################################################
    # setUserQuota
    ############################################################
    def setUserQuota(self, userId, userIdtoModify, quota):
        self._log.info("user:" + userId + " command:setUserQuota args={userIdtoModify:" + userIdtoModify + ", quota:" + str(quota) + "}")
        return self.userStore.setQuota(userId, userIdtoModify, quota)

    ############################################################
    # setUserStatus
    ############################################################
    def setUserStatus(self, userId, userIdtoModify, status):
        self._log.info("user:" + userId + " command:setUserStatus args={userIdtoModify:" + userIdtoModify + ", status:" + status + "}")
        if (status in IRUser.Status):
            return self.userStore.setUserStatus(userId, userIdtoModify, status)
        else:
            self._log.error("Status " + status + " is not valid")
            print "Status not valid. Status available: " + str(IRUser.Status)
            return False



    def query(self, userId, queryString):
        self._log.info("user:" + userId + " command:list args={queryString:" + queryString + "}")
        return self.metaStore.getItems(queryString)

    ############################################################
    # get
    ############################################################
    def get(self, userId, option, imgId):
        self._log.info("user:" + userId + " command:get args={option:" + option + ", imgId:" + imgId + "}")

        if (option == "img"):
            return self.imgStore.getItem(imgId, userId, self.userStore.isAdmin(userId))
        elif (option == "uri"):
            return self.imgStore.getItemUri(imgId, userId, self.userStore.isAdmin(userId))

    ############################################################
    # put
    ############################################################
    def put(self, userId, imgId, imgFile, attributeString, size, extension):
        """
        Register the file in the database
        
        return imgId or 0 if something fails
        """

        status = False
        statusImg = False
        fileLocation = ""
        aMeta = None
        aImg = None

        if (size > 0):
            if type(imgFile) == cherrypy._cpreqbody.Part:
                self._log.info("user:" + userId + " command:put args={imgId:" + imgId + ", imgFile:" + imgId + ", metadata:" + attributeString + \
                               ", size:" + str(size) + ", extension:" + extension + "}")
                aMeta = self._createImgMeta(userId, imgId, attributeString, False)
                aImg = ImgEntry(imgId, aMeta, self._imgStore + "/" + imgId, size, extension)
                #it sends the imgEntry and the requestInstance
                statusImg = self.imgStore.addItem(aImg, imgFile)

            else:
                self._log.info("user:" + userId + " command:put args={imgId:" + imgId + ", imgFile:" + imgFile + ", metadata:" + attributeString + \
                               ", size:" + str(size) + ", extension:" + extension + "}")
                fileLocation = self._imgStore + imgId
                if(os.path.isfile(fileLocation)):
                        #parse attribute string and construct image metadata
                        aMeta = self._createImgMeta(userId, imgId, attributeString, False)
                        #put image item in the image store        
                        aImg = ImgEntry(imgId, aMeta, fileLocation, size, extension.strip())
                        #it sends the imgEntry and None                
                        statusImg = self.imgStore.addItem(aImg, None)

            if(statusImg):
                #put metadata into the image meta store

                #with MongoDB I put the metadata with the ImgEntry, so it skips meta add                    
                if(re.search("mongo", self._backend) == None):
                    statusMeta = self.metaStore.addItem(aMeta)
                else:
                    statusMeta = True

                if(statusMeta):
                    #Add size and #imgs to user
                    statusAcc = self.userStore.updateAccounting(userId, size, 1)

                    if (statusAcc):
                        status = True

        else:
            self._log.error("File size must be higher than 0")

        if(status):
            return aImg._imgId
        else:
            return 0

    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, userId, imgId, attributeString):
        """
        Update Image Repository
      
        keywords:
        option: 
        img - update only the Image file
        meta - update only the Metadata
        all - update Image file and Metadata
        """
        self._log.info("user:" + userId + " command:updateItem args={imgId:" + imgId + ",metadata:" + attributeString + "}")
        success = False
        self._log.debug(str(attributeString))
        aMeta = self._createImgMeta(userId, imgId, attributeString, True)
        self._log.debug(str(aMeta))
        success = self.metaStore.updateItem(userId, imgId, aMeta)

        return success

    ############################################################
    # remove
    ############################################################
    def remove(self, userId, imgIdList):
        self._log.info("user:" + userId + " command:remove args={imgId:" + imgIdList + "}")
        notdeletedIds=[]
        for imgId in imgIdList.split():
            status=False
            owner = self.imgStore.getOwner(imgId)
            if owner != None:
                size = [0] #Size is output parameter in the first call. 
                status = self.imgStore.removeItem(userId, imgId, size, self.userStore.isAdmin(userId))
            if(status):
                status = self.userStore.updateAccounting(owner, -(size[0]), -1)
                self._log.info("Image " + imgId + " removed")
            else:
                notdeletedIds.append(imgId)
                self._log.info("Image " + imgId + " NOT removed")
        
        if len(notdeletedIds) == 0:
            return True
        else:
            return " ".join(notdeletedIds)

    ############################################################
    # histImg
    ############################################################
    def histImg(self, userId, imgId):
        self._log.info("user:" + userId + " command:histImg args={imgId:" + imgId + "}")
        output = self.imgStore.histImg(imgId)
        if output != None:
            output = re.sub(r"imgURI=,|size=0,|extension=","",str(output))
        return output

    """
    ############################################################
    # printHistImg
    ############################################################
    def printHistImg(self, imgs):
        output = {}
        output ['head'] = "    Image_Id \t\t     Created_Date \t Last_Access \t    #Access \n"
        output ['head'] = string.expandtabs(output ['head'], 8)
        stradd = ""
        for i in range(len(output['head'])):
            stradd += "-"
        output ['head'] += stradd

        if(imgs != None):
            for key in imgs.keys():
                spaces = ""
                num = 24 - len(imgs[key]._imgId)
                if (num > 0):
                    for i in range(num):
                        spaces += " "

                output[key] = imgs[key]._imgId + spaces + "  " + str(imgs[key]._createdDate) + "  " + \
                        str(imgs[key]._lastAccess) + "    " + str(imgs[key]._accessCount) + "\n"

        return output
    """

    ############################################################
    # histUser
    ############################################################
    def histUser(self, userId, userIdtoSearch):
        self._log.info("user:" + userId + " command:histImg args={userIdtoSearch:" + userIdtoSearch + "}")
        output = {}
        """
        output ['head'] = "User_Id  Used_Disk \t\t  Last_Login  \t\t #Owned_Images \n"
        output ['head'] = string.expandtabs(output ['head'], 8)
        stradd = ""
        for i in range(len(output['head'])):
            stradd += "-"
        output ['head'] += stradd
        """
        if (userIdtoSearch == "None"):
            userIdtoSearch = None

        users = self.userStore.queryStore(userId, userIdtoSearch)
        #.*? everything until
        if users != None:
            users = re.sub("cred=.*?, ","",str(users))
        """
        if(users != None):
            for key in users.keys():
                spaces = ""
                num = 8 - len(users[key]._userId)
                if (num > 0):
                    for i in range(num):
                        spaces += " "


                output[key] = users[key]._userId + spaces + "   " + str(users[key]._fsUsed).split(".")[0] + " \t\t " + \
                        str(users[key]._lastLogin) + "   \t " + str(users[key]._ownedImgs).split(".")[0] + "\n"
        """
        return users



    ############################################################
    # _createImgMeta
    ############################################################
    def _createImgMeta(self, userId, imgId, attributeString, update):  ##We assume that values are check in client side
        """
        Create a ImgMeta object from a list of attributes
        
        keywords
        update: if True no default values are added
        """
        args = [''] * 10
        attributes = attributeString.split("&")
        for item in attributes:
            attribute = item.strip()
            #print attribute
            tmp = attribute.split("=")
            for i in range(len(tmp)):
                tmp[i]=tmp[i].strip()            
            if (len(tmp) == 2):
                key = string.lower(tmp[0])
                value = tmp[1]
                if key in ImgMeta.metaArgsIdx.keys():
                    if (key == "vmtype"):
                        value = string.lower(value)
                        if not (value in ImgMeta.VmType):
                            print "Wrong value for VmType, please use: " + str(ImgMeta.VmType)
                            break
                    elif (key == "imgtype"):
                        value = string.lower(value)
                        if not (value in ImgMeta.ImgType):
                            print "Wrong value for ImgType, please use: " + str(ImgMeta.ImgType)
                            break
                    elif(key == "permission"):
                        value = string.lower(value)
                        if not (value in ImgMeta.Permission):
                            print "Wrong value for Permission, please use: " + str(ImgMeta.Permission)
                            break
                    elif (key == "imgstatus"):
                        value = string.lower(value)
                        if not (value in ImgMeta.ImgStatus):
                            print "Wrong value for ImgStatus, please use: " + str(ImgMeta.ImgStatus)
                            break
                    args[ImgMeta.metaArgsIdx[key]] = value
        if not update:
            for x in range(len(args)):
                if args[x] == '':
                    args[x] = ImgMeta.argsDefault[x]
            #if x==4 or x==5 or x==8:
             #   args[x] = "'" + args[x] + "'"
            #print IRService.argsDefault[x], args[x]

        aMeta = ImgMeta(imgId, args[1], args[2], userId, args[4],
                        args[5], args[6], args[7], args[8], args[9])
        #print aMeta
        return aMeta
"""
    ############################################################
    # usage
    ############################################################
def usage():
    print "options:"
    print '''
        -h/--help: get help information
        -l/--auth: login/authentication
        -q/--list queryString: get list of images that meet the criteria
        -a/--setPermission imgId permissionString: set access permission
        -g/--get img/uri imgId: get a image or only the URI by id
        -p/--put imgFile attributeString: upload/register an image
        -m/--modify imgId attributeString: update information
        -r/--remove imgId: remove an image from the repository
        -i/--histimg imgId: get usage info of an image
        -u/--histuser userId: get usage info of a user
        --getBackend: provide the back-end configuration in the server side
        --useradd <userId> : add user 
        --userdel <userId> : remove user
        --userlist : list of users
        --setquota <userId> <quota> :modify user quota
        --setrole  <userId> <role> : modify user role
        --setUserStatus <userId> <status> :modify user status
          '''
"""
"""
    ############################################################
    # main
    ############################################################
def main():


    try:
        opts, args = gnu_getopt(sys.argv[1:],
                                "hlqagprium",
                                ["help",
                                 "auth",
                                 "list",
                                 "setPermission",
                                 "get",
                                 "put",
                                 "remove",
                                 "histimg",
                                 "histuser",
                                 "uploadValidator",
                                 "genImgId",
                                 "getBackend",
                                 "modify",
                                 "useradd",
                                 "userdel",
                                 "userlist",
                                 "setUserQuota",
                                 "setUserRole",
                                 "setUserStatus"
                                 ])

    except GetoptError, err:
        print "%s" % err
        sys.exit(2)

    

    service = IRService()

    if(len(opts) == 0):
        usage()
        sys.exit(0)

    #Security mechanism. We create a list of users that can use this interface. For example, image generation user must be able to run this.
    AuthorizedUsers = service.getAuthorizedUsers()
    if not os.popen('whoami', 'r').read().strip() in AuthorizedUsers:
        if not (os.popen('whoami', 'r').read().strip() == args[0]):    
            print "Error. your are not authorized to use another user name"
            sys.exit(1)

    for o, v in opts:
        #print o, v
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--auth"):
            #username = os.system("whoami")
            #service.auth(username)
            print service.auth("fuwang", "REMOVED")
        elif o in ("-q", "--list"):
            imgs = service.query(args[0], args[1])
            #for key in imgs.keys():
            #    print imgs[key]
            print imgs
            #service.query("tstuser2", "imgId=fakeid4950877")
        elif o in ("-a", "--setPermission"): ##THIS is not used from client side. We call directly updateItem
            print service.updateItem(args[0], args[1], args[2])
        elif o in ("-g", "--get"):
            print service.get(args[0], args[1], args[2])
            #print service.get(args[], "img", "4d4c2e6e577d70102a000000")
        elif o in ("-p", "--put"):
            print service.put(args[0], args[1], args[2], args[3], int(args[4]), args[5])
        elif o in ("-r", "--remove"):
            print service.remove(args[0], args[1])
            #print service.remove(args[], "4d4b0b8a577d700d2b000000")
        elif o in ("-i", "--histimg"):
            imgs = service.histImg(args[0], args[1])

            print service.printHistImg(imgs)

        elif o in ("-u", "--histuser"):
            print service.histUser(args[0], args[1])

        elif o in ("--uploadValidator"):
            print service.uploadValidator(args[0], int(args[1]))
            #print service.uploadValidator("javi", 0)
        elif o in ("--genImgId"):
            print service.genImgId()
        elif o in ("--getBackend"):
            print service.getBackend()
            print service.getImgStore()
        elif o in ("-m", "--modify"):
            print service.updateItem(args[0], args[1], args[2])
            #print service.updateItem(args[], "4d681d65577d703439000000", "vmtype=vmware|os=windows")

#This commands only can be used by users with Admin Role.
        elif o in ("--useradd"):  #args[0] is the username. It MUST be the same that the system user
            print service.userAdd(args[0], args[1])

        elif o in ("--userdel"):
            print service.userDel(args[0], args[1])

        elif o in ("--userlist"):
            print service.userList(args[0])

        elif o in ("--setUserQuota"):
            print service.setUserQuota(args[0], args[1], int(args[2]))

        elif o in ("--setUserRole"):
            print service.setUserRole(args[0], args[1], args[2])

        elif o in ("--setUserStatus"):
            print service.setUserStatus(args[0], args[1], args[2])

        else:
            assert False, "unhandled option"

if __name__ == "__main__":
    main()
"""

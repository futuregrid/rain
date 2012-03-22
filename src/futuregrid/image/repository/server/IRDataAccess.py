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
Data access and persistent

These classes deal with data persistent and access in the file system,
which could be implemented using file or database.
"""

__author__ = 'Fugang Wang'

from futuregrid.image.repository.server.IRTypes import ImgEntry
from futuregrid.image.repository.server.IRTypes import ImgMeta
from futuregrid.image.repository.server.IRTypes import IRUser
import re

class AbstractImgStore(object):
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        if type(self) is AbstractImgStore:
            raise Exception('This is an abstract class')
        else:
            self._items = {}

    ############################################################
    # getItemUri
    ############################################################
    def getItemUri(self, imgId):
        pass

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId, userId):
        pass

    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgEntry):
        pass

    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, imgId, imgEntry):
        pass

    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds, userId):
        pass

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items):
        pass

    ############################################################
    # removeItem
    ############################################################
    def removeItem(self, userId, imgId):
        pass

class AbstractImgMetaStore(object):
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        if type(self) is AbstractImgMetaStore:
            raise Exception('This is an abstract class')
        else:
            self._items = {}

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId):
        pass

    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgMeta):
        pass

    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, imgId, imgEntry):
        pass

    ############################################################
    # getItems
    ############################################################
    def getItems(self, criteria):
        pass

    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds):
        pass

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items):
        pass

    ############################################################
    # removeItem
    ############################################################
    def removeItem(self, userId, imgId):
        pass

class AbstractIRUserStore(object):
    '''
    User store existing as a file or db
    '''
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        if type(self) is AbstractImgMetaStore:
            raise Exception('This is an abstract class')
        else:
            self._items = {}

    ############################################################
    # getUser
    ############################################################
    def getUser(self, userId):
        pass

    ############################################################
    # addUser
    ############################################################
    def addUser(self, user):
        pass

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, users):
        pass

    ############################################################
    # uploadValidator
    ############################################################
    def uploadValidator(self, userId, imgSize):
        pass

##
# Image store existing as a file or db 
#
class ImgStoreFS(AbstractImgStore):
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(ImgStoreFS, self).__init__()
        #self._items = {}
        self._fsloc = "IRImgStore"   #file location containing images

    ############################################################
    # getItemUri
    ############################################################
    def getItemUri(self, imgId):
        return getItem(imgId)

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId):
        if not imgId in self._items.keys():
            # not found, so searching the file
            ret = self.queryStore(imgId)
        else:
            ret = self._items[imgId];
        if ret:
            ret = ret._imgURI
        else:
            ret = None
        return ret


    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgEntry):
        self.persistToStore([imgEntry])
        self._items[imgEntry._imgId] = imgEntry


    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, imgId, imgEntry):
        ret = True;
        if not imgId in self._items.keys():
            ret = false
        else:
            self._items[imgEntry._imgId] = imgEntry
        return ret

    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds):
        ret = False
        self._getItems()
        if not isinstance(imgIds, list):
            # print "querying single id for id=" + imgIds
            if imgIds in self._items.keys():
                ret = True
                ret = self._items[imgIds]
        else:
            pass
        return ret



    ############################################################
    # _getItems
    ############################################################
    def _getItems(self):
        f = open(self._fsloc, "r")
        self._items.clear()
        items = f.readlines()
        for item in items:
            item = eval(item)
            segs = item.split(",")
            args = [x.strip() for x in segs]
            self._items[args[0]] = ImgEntry(args[0], None, args[1])
        f.close()


    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items):
        f = open(self._fsloc, "a")
        for item in items:
            f.write(str(item) + '\n')
        f.close()

#
# Image metadata store
#       
class ImgMetaStoreFS(AbstractImgMetaStore):
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(ImgMetaStoreFS, self).__init__()
        #self._items = {}
        self._fsloc = "IRMetaStore"   #file location containing the metadata

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId):
        if not imgId in self._items.keys():
            if self.queryStore("id=" + imgId):
                ret = self._items[imgId]
            else:
                ret = None
        else:
            ret = self._items[imgId];
        return ret

    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgMeta):
        self.persistToStore([imgMeta])
        self._items[imgMeta._imgId] = imgMeta


    ############################################################
    # updateItem
    ############################################################
    def updateItem(self, imgId, imgMeta):
        ret = True;
        if not imgId in _items.keys():
            ret = false
        else:
            self._items[imgMeta._imgId] = imgMeta
        return ret

    ############################################################
    # getItems
    ############################################################
    def getItems(self, criteria):
        if self.queryStore(criteria):
            return self._items
        else:
            return None


    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, criteria):
        ret = False
        self._items.clear()
        f = open(self._fsloc, "r")
        items = f.readlines()
        #parse query string
        if criteria == "*":
            for item in items:
                #print item
                item = eval(item)
                segs = item.split(",")
                args = [x.strip() for x in segs]
                tmpMeta = ImgMeta(args[0], args[1], args[2], args[3],
                    args[4], args[5], args[6], args[7], args[8], args[9])
                self._items[tmpMeta._imgId] = tmpMeta
            ret = True
        elif re.findall("id=.+", criteria):
            #print "searching for " + criteria
            matched = re.search("id=.+", criteria).group[0]
            #print matched
            idsearched = matched.split("=")[1]
            for item in items:
                item = eval(item)
                segs = item.split(",")
                args = [x.strip() for x in segs]
                #print args[0], idsearched
                if args[0] == idsearched:
                    tmpMeta = ImgMeta(args[0], args[1], args[2], args[3],
                    args[4], args[5], args[6], args[7], args[8], args[9])
                    self._items[tmpMeta._imgId] = tmpMeta
                    ret = True
                    break
        else:
            print "query string not supported. Try '*'"
        f.close()
        return ret

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items):
        f = open(self._fsloc, "a")
        for item in items:
            f.write(str(item) + '\n')
        f.close()

class IRUserStoreFS(AbstractIRUserStore):
    '''
    User store existing as a file or db
    '''
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(IRUserStoreFS, self).__init__()
        #self._items = []
        self._fsloc = "IRUserStore"   #file location for users

    ############################################################
    # getUser
    ############################################################
    def getUser(self, userId):
        '''Get user from the store by Id'''
        return IRUser(userId)


    ############################################################
    # addUser
    ############################################################
    def addUser(self, user):
        pass

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, users):
        pass

    ############################################################
    # uploadValidator
    ############################################################
    def uploadValidator(self, userId, imgSize):
        user = self.getUser(userId)
        ret = True
        if imgSize + user._fsUsed > user._fsCap:
            ret = False
        return ret

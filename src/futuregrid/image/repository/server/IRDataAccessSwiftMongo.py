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
This class is to use MongoDB as Image Repository back-end

Create a config file with
    list of mongos: ip/address and port
    list of db names: I would say one per imgType    

MongoDB Databases Info:

    A database with all the info. The problem of the Option 1 is that we need to perform 
                                   a minimum of two queries to get an image
                                  The problem of Option 2 could be that if the db is too big,
                                   we could have performance problems... or not, lets see ;)
        images.fs.chunks (GridFS files)
        images.fs.files  (GridFS metadata)
        images.data      (Image details)
        images.meta        (Image metadata)

REMEBER: imgId will be _id (String) in the data collection, which is also _id (ObjectId) in fs.files. 
               In the first case it is an String and in the second one is an ObjectId
               
"""

__author__ = 'Javier Diaz'

import pymongo
from pymongo import Connection
from pymongo.objectid import ObjectId
import gridfs
import bson
import os
import re
import sys
import cloudfiles
from datetime import datetime

from futuregrid.image.repository.server.IRDataAccessMongo import ImgStoreMongo
from futuregrid.image.repository.server.IRDataAccessMongo import ImgMetaStoreMongo
from futuregrid.image.repository.server.IRDataAccessMongo import IRUserStoreMongo
from futuregrid.image.repository.server.IRTypes import ImgEntry
from futuregrid.image.repository.server.IRTypes import ImgMeta
from futuregrid.image.repository.server.IRTypes import IRUser

class ImgStoreSwiftMongo(ImgStoreMongo):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, addressS, userAdminS, configFileS, imgStore, log):
        """
        Initialize object
        
        Keyword parameters:             
        _mongoaddress = mongos addresses and ports separated by commas (optional if config file exits)
        _items = list of imgEntry
        _dbName = name of the database
        
        """
        super(ImgStoreMongo, self).__init__()

        self._dbName = "imagesS"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None
        self._log = log
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._imgStore=imgStore

        self._swiftAddress = addressS
        self._userAdminS = userAdminS
        self._configFileS = configFileS
        self._swiftConnection = None
        self._containerName = "imagesMongo"

    ############################################################
    # getItemUri
    ############################################################
    def getItemUri(self, imgId, userId):
        return "For now we do not provide this feature with the Swift system as backend."

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId, userId, admin):
        """
        Get Image file identified by the imgId
        
        keywords:
        imgId: identifies the image
        
        return the image uri
        """

        imgLinks = []
        extension = []
        result = self.queryStore([imgId], imgLinks, userId, admin, extension)
        """
        if (result):
            filename = self._imgStore + "/" + imgId + "" + extension[0].strip()
            if not os.path.isfile(filename):
                f = open(filename, 'w')
            else:
                for i in range(1000):
                    filename = self._imgStore + "/" + imgId + "" + extension[0].strip() + "_" + i.__str__()
                    if not os.path.isfile(filename):
                        f = open(filename, 'w')
                        break
            
            #I think that this need the connection with Swift
            for chunk in imgLinks[0].stream():  
                f.write(chunk)   
            f.close()
                              
            return filename
        else:
            return None
        """
        self._log.debug(imgLinks[0])
        ##to skip the python api
        if (result):
            return imgLinks[0]
        else:
            return None
        ##to skip the python api

    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds, imgLinks, userId, admin, extension):
        """        
        Query the DB and provide a generator object of the Images to create them with strean method.    
        
        keywords:
        imgIds: this is the list of images that I need
        imgEntries: This is an output parameter. Return the list of GridOut objects
                      To read the file it is needed to use the read() method    
        """
        del imgLinks[:]
        itemsFound = 0

        if (self.mongoConnection()):# and self.swiftConnection()):
            try:

                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]

                #contain= self._swiftConnection.get_container(self._containerName)

                for imgId in imgIds:

                    access = False
                    if(self.existAndOwner(imgId, userId) or admin):
                        access = True
                        #self._log.debug("ifowner "+str(access))
                    elif(self.isPublic(imgId)):
                        access = True
                        #self._log.debug("ifpublic "+str(access))
                    if (access):
                        #extension.append(collection.find_one({'_id':imgId})['extension'])                        
                        #imgLinks.append(contain.get_object(imgId))

                        ##to skip the python api
                        ext = collection.find_one({'_id':imgId})['extension']
                        imagepath = self._imgStore + '/' + imgId + "" + ext.strip()

                        if os.path.isfile(imagepath):
                            for i in range(1000):
                                imagepath = self._imgStore + "/" + imgId + "" + ext.strip() + "_" + i.__str__()
                                if not os.path.isfile(imagepath):
                                    break

                        cmd = "$HOME/swift/trunk/bin/st download -q " + self._containerName + " " + imgId + " -o " + imagepath + " -A https://192.168.11.40:8080/auth/v1.0 -U test:tester -K testing"

                        os.system(cmd)
                        self._log.debug(imagepath)
                        imgLinks.append(imagepath)
                        ##to skip the python api


                        collection.update({"_id": imgId},
                                      {"$inc": {"accessCount": 1}, }, safe=True)
                        collection.update({"_id": imgId},
                                      {"$set": {"lastAccess": datetime.utcnow()}, }, safe=True)
                        #print "here"                                         
                        itemsFound += 1
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgStoreSwiftMongo - queryStore.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed.")
            except TypeError as detail:
                self._log.error("TypeError in ImgStoreSwiftMongo - queryStore")
            except bson.errors.InvalidId:
                self._log.error("There is no Image with such Id. (ImgStoreSwiftMongo - queryStore)")
            except gridfs.errors.NoFile:
                self._log.error("File not found")
            except cloudfiles.errors.NoSuchObject:

                self._log.error("File not found")
            except:
                self._log.error("Error in ImgStoreSwiftMongo - queryToStore. " + str(sys.exc_info()))
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The file has not been stored")

        if (itemsFound >= 1):
            return True
        else:
            return False


    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items, requestInstance):
        """Copy imgEntry and imgMeta to the DB. It first store the imgEntry to get the file Id
        
        Keyword arguments:
        items= list of ImgEntrys
                
        return: True if all items are stored successfully, False in any other case
        """
        self._dbConnection = self.mongoConnection()
        imgStored = 0

        if (self.mongoConnection()):#and self.swiftConnection()):
            """
            try:
                contain= self._swiftConnection.get_container(self._containerName)
            except cloudfiles.errors.NoSuchContainer:
                self._swiftConnection.create_container(self._containerName)
                contain= self._swiftConnection.get_container(self._containerName)
                self._log.warning("Creating the container")
            except:
                self._log.error("Error in ImgStoreSwiftMongo - persistToStore. "+str(sys.exc_info()))      
            """
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]
                collectionMeta = dbLink[self._metacollection]

                for item in items:
                    """                   
                    loaded=False
                    retries=0
                    while (not loaded and retries<10):
                        try:
                            img=contain.create_object(item._imgId)
                            img.load_from_filename(item._imgURI)
                            loaded=True
                        except:
                            retries+=1
                            self._log.error("Error in ImgStoreSwiftMysql - trytoload "+str(sys.exc_info()))  
                    """

                    s = os.chdir(self._imgStore)#self._fgirdir)
                    cmd = "$HOME/swift/trunk/bin/st upload -q " + self._containerName + " " + item._imgId + " -A https://192.168.11.40:8080/auth/v1.0 -U test:tester -K testing"
                    status = os.system(cmd)
                    self._log.debug(" swift upload image status: " + str(status))
                    if(status == 0):
                        loaded = True

                    if loaded:
                        tags = item._imgMeta._tag.split(",")
                        tags_list = [x.strip() for x in tags]
                        meta = {"_id": item._imgId,
                                "os" : item._imgMeta._os,
                                "arch" : item._imgMeta._arch,
                                "owner" : item._imgMeta._owner,
                                "description" : item._imgMeta._description,
                                "tag" : tags_list,
                                "vmType" : item._imgMeta._vmType,
                                "imgType" : item._imgMeta._imgType,
                                "permission" : item._imgMeta._permission,
                                "imgStatus" : item._imgMeta._imgStatus,
                                }
                        data = {"_id": item._imgId,
                                "createdDate" : datetime.utcnow(),
                                "lastAccess" : datetime.utcnow(),
                                "accessCount" : 0,
                                "size" : item._size,
                                "extension" : item._extension,
                                }

                        collectionMeta.insert(meta, safe=True)
                        collection.insert(data, safe=True)

                        imgStored += 1


            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure. The file has not been stored. Image details: " + item.__str__() + "\n")
            except IOError:
                self._log.error("Error in ImgStoreSwiftMongo - persistToStore. " + str(sys.exc_info()))
                self._log.error("No such file or directory. Image details: " + item.__str__())
            except TypeError:
                self._log.error("TypeError in ImgStoreSwiftMongo - persistToStore " + str(sys.exc_info()))
            except pymongo.errors.OperationFailure:
                self._log.error("Operation Failure in ImgStoreSwiftMongo - persistenToStore")
            except:
                self._log.error("Error in ImgStoreSwiftMongo - persistToStore. " + str(sys.exc_info()))
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The file has not been stored")

        for item in items:
            if (re.search('^/tmp/', item._imgURI)):
                cmd = "rm -f " + item._imgURI
                os.system(cmd)

        if (imgStored == len(items)):
            return True
        else:
            return False

    ############################################################
    # removeItem 
    ############################################################
    def removeItem (self, userId, imgId, size, admin):
        #what are we going to do with concurrency?
        """
        Remove the Image file and Metainfo if imgId exists and your are the owner.
        
        IMPORTANT: if you want to update both imgEntry and imgMeta, 
                   you have to update first imgMeta and then imgEntry,
                   because imgEntry's update method change the _id of the imgMeta document
                
        keywords:
        imgId : identifies the image (I think that we can remove this)
        imgEntry : new info to update. It HAS TO include the owner in _imgMeta
        size: Size of the img deleted.
        
        Return boolean
        """
        removed = False
        if (self.mongoConnection()):# and self.swiftConnection()):
            if(self.existAndOwner(imgId, userId) or admin):
                try:
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._datacollection]
                    collectionMeta = dbLink[self._metacollection]

                    #contain= self._swiftConnection.get_container(self._containerName)
                    cmd = "$HOME/swift/trunk/bin/st delete -q " + self._containerName + " " + imgId + " -A https://192.168.11.40:8080/auth/v1.0 -U test:tester -K testing"
                    status = os.system(cmd)
                    self._log.debug(" swift remove image status: " + str(status))
                    if (status == 0):
                        aux = collection.find_one({"_id": imgId})
                        size[0] = aux['size']

                    #contain.delete_object(imgId)

                        collection.remove({"_id": imgId}, safe=True) #Wait for replication? w=3 option
                        collectionMeta.remove({"_id": imgId}, safe=True)
                        removed = True
                except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                    self._log.warning("Autoreconnected.")
                except pymongo.errors.ConnectionFailure:
                    self._log.error("Connection failure. The file has not been updated")
                except IOError:
                    self._log.error("Error in ImgStoreSwiftMongo - removeItem. " + str(sys.exc_info()))
                    self._log.error("No such file or directory. Image details: " + item.__str__())
                except TypeError:
                    self._log.error("TypeError in ImgStoreSwiftMongo - removeItem " + str(sys.exc_info()))
                except pymongo.errors.OperationFailure:
                    self._log.error("Operation Failure in ImgStoreSwiftMongo - RemoveItem")
                except:
                    self._log.error("Error in ImgStoreSwiftMongo - removeItem. " + str(sys.exc_info()))
                finally:
                    self._dbConnection.disconnect()
            else:
                self._log.error("The Image does not exist or the user is not the owner")
        else:
            self._log.error("Could not get access to the database. The file has not been removed")

        return removed

    ############################################################
    # existAndOwner
    ############################################################
    def existAndOwner(self, imgId, ownerId):
        """
        To verify if the file exists and I am the owner
        
        keywords:
        imgId: The id of the image
        ownerId: The owner Id
        
        Return: boolean
        """

        exists = False
        isOwner = False

        try:
            dbLink = self._dbConnection[self._dbName]
            collection = dbLink[self._metacollection]
            #contain= self._swiftConnection.get_container(self._containerName)

            #if imgId in contain.list_objects():
            cmd = "$HOME/swift/trunk/bin/st list " + self._containerName + " -A https://192.168.11.40:8080/auth/v1.0 -U test:tester -K testing"
            output = os.popen(cmd).read()
            if imgId in output:
                exists = True
            #exists=True
            #print imgId         
            #print ownerId
            aux = collection.find_one({"_id": imgId, "owner": ownerId})
            if (aux == None):
                isOwner = False
            else:
                isOwner = True
            #print isOwner                 
        except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
            self._log.warning("Autoreconnected.")
        except pymongo.errors.ConnectionFailure:
            self._log.error("Connection failure")
        except TypeError as detail:
            self._log.error("TypeError in ImgStoreMongo - existAndOwner")
        except bson.errors.InvalidId:
            self._log.error("Error, not a valid ObjectId in ImgStoreMongo - existAndOwner")
        except gridfs.errors.NoFile:
            self._log.error("File not found")

        if (exists and isOwner):
            return True
        else:
            return False

    ############################################################
    # swiftConnection
    ############################################################
    def swiftConnection(self):
        """
        Connect with OpenStack swift
        
        """
        connected = False

        id = self._userAdminS #'test:tester'
        pw = self.getPassword(self._configFileS) #'testing'
        try:
            self._swiftConnection = cloudfiles.get_connection(id, pw, authurl='https://' + self._swiftAddress + ':8080/auth/v1.0')
            connected = True
        except:
            self._log.error("Error in swift connection. " + str(sys.exc_info()))

        return connected

class ImgMetaStoreSwiftMongo(ImgMetaStoreMongo):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, log):
        """
        Initialize object
        
        Keyword parameters:             
        _mongoaddress = mongos addresses and ports separated by commas (optional if config file exits)
        _items = list of imgEntry
        _dbName = name of the database
        
        """
        super(ImgMetaStoreMongo, self).__init__()

        self._dbName = "imagesS"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None
        self._log = log        
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile

class IRUserStoreSwiftMongo(IRUserStoreMongo):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, log):
        """
        Initialize object
        
        Keyword parameters:             
        _mongoaddress = mongos addresses and ports separated by commas (optional if config file exits)
        _items = list of imgEntry
        _dbName = name of the database
        
        """
        super(IRUserStoreMongo, self).__init__()

        self._dbName = "imagesS"   #file location for users
        self._usercollection = "users"
        self._dbConnection = None
        self._log = log
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        


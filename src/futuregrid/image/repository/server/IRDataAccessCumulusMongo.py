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
import gridfs
import bson
from bson.objectid import ObjectId
from datetime import datetime
import os
import re
import sys
import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.connection import S3Connection

from futuregrid.image.repository.server.IRDataAccessMongo import ImgStoreMongo
from futuregrid.image.repository.server.IRDataAccessMongo import ImgMetaStoreMongo
from futuregrid.image.repository.server.IRDataAccessMongo import IRUserStoreMongo
from futuregrid.image.repository.server.IRTypes import ImgEntry
from futuregrid.image.repository.server.IRTypes import ImgMeta
from futuregrid.image.repository.server.IRTypes import IRUser


class ImgStoreCumulusMongo(ImgStoreMongo):

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

        self._dbName = "imagesC"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None        
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile

        self._cumulusAddress = addressS
        self._userAdminS = userAdminS
        self._configFileS = configFileS        
        self._cumulusConnection = None
        self._containerName = "imagesmongo"  ##bucket
        self._log = log
        self._imgStore=imgStore
    ############################################################
    # getItemUri
    ############################################################
    def getItemUri(self, imgId, userId):
        return "For now we do not provide this feature with the cumulus system as backend."


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
        result = self.queryStore([imgId], imgLinks, userId, admin)

        if (result):
            return imgLinks[0]
        else:
            return None

    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds, imgLinks, userId, admin):
        """        
        Query the DB and provide a generator object of the Images to create them with strean method.    
        
        keywords:
        imgIds: this is the list of images that I need
        imgEntries: This is an output parameter. Return the list of GridOut objects
                      To read the file it is needed to use the read() method    
        """
        del imgLinks[:]
        itemsFound = 0

        if (self.mongoConnection() and self.cumulusConnection()):
            try:

                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]

                contain = self._cumulusConnection.get_bucket(self._containerName)
                k = Key(contain)

                for imgId in imgIds:

                    access = False
                    if(self.existAndOwner(imgId, userId) or admin):
                        access = True
                        #self._log.debug("ifowner "+str(access))
                    elif(self.isPublic(imgId)):
                        access = True
                        #self._log.debug("ifpublic "+str(access))
                    if (access):
                        extension=collection.find_one({'_id':imgId})['extension']
                        
                        k.key = imgId

                        #Boto does not stream, so we have to create the file here instead of in getItem
                        imagepath = self._imgStore + '/' + imgId + "" + extension.strip()

                        if os.path.isfile(imagepath):
                            for i in range(1000):
                                imagepath = self._imgStore + "/" + imgId + "" + extension.strip() + "_" + i.__str__()
                                if not os.path.isfile(imagepath):
                                    break

                        k.get_contents_to_filename(imagepath)

                        imgLinks.append(imagepath)

                        collection.update({"_id": imgId},
                                      {"$inc": {"accessCount": 1}, }, safe=True)
                        collection.update({"_id": imgId},
                                      {"$set": {"lastAccess": datetime.utcnow()}, }, safe=True)
                        #print "here"                                         
                        itemsFound += 1
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgStorecumulusMongo - queryStore.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed.")
            except TypeError as detail:
                self._log.error("TypeError in ImgStorecumulusMongo - queryStore")
            except bson.errors.InvalidId:
                self._log.error("There is no Image with such Id. (ImgStoreMongo - queryStore)")
            except boto.exception.S3ResponseError as detail:
                self._log.error("Code and reason " + detail.code + " " + detail.reason)
                self._log.error("Error in ImgStorecumulusMongo - queryToStore. full error " + str(sys.exc_info()))
            except:
                self._log.error("Error in ImgStorecumulusMongo - queryToStore. " + str(sys.exc_info()))
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

        if (self.mongoConnection() and self.cumulusConnection()):

            try:
                contain = self._cumulusConnection.get_bucket(self._containerName)
            except boto.exception.S3ResponseError as detail:
                if(detail.reason.strip() == "Not Found"):
                    self._log.warning("Creating bucket")
                    self._cumulusConnection.create_bucket(self._containerName)
                    contain = self._cumulusConnection.get_bucket(self._containerName)
                else:
                    self._log.error("Code and reason " + detail.code + " " + detail.reason)
                    self._log.error("Error in ImgStorecumulusMongo - queryToStore. full error " + str(sys.exc_info()))
            except:
                self._log.error("Error in ImgStorecumulusMongo - persistToStore. " + str(sys.exc_info()))

            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]
                collectionMeta = dbLink[self._metacollection]

                k = Key(contain)

                for item in items:

                    k.key = item._imgId
                    if requestInstance == None:
                        k.set_contents_from_filename(item._imgURI)
                    else:
                        requestInstance.file.seek(0)
                        k.set_contents_from_file(requestInstance.file)

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
                self._log.error("Error in ImgStorecumulusMongo - persistenToStore. " + str(sys.exc_info()))
                self._log.error("No such file or directory. Image details: " + item.__str__())
            except TypeError:
                self._log.error("TypeError in ImgStorecumulusMongo - persistenToStore " + str(sys.exc_info()))
            except pymongo.errors.OperationFailure:
                self._log.error("Operation Failure in ImgStorecumulusMongo - persistenToStore. " + str(sys.exc_info()))
            except:
                self._log.error("Error in ImgStoreCumulusMongo - persistToStore. " + str(sys.exc_info()))
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The file has not been stored")

        for item in items:            
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
        if (self.mongoConnection() and self.cumulusConnection()):
            if(self.existAndOwner(imgId, userId) or admin):
                try:
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._datacollection]
                    collectionMeta = dbLink[self._metacollection]

                    contain = self._cumulusConnection.get_bucket(self._containerName)
                    contain.delete_key(imgId)

                    aux = collection.find_one({"_id": imgId})
                    size[0] = aux['size']

                    collection.remove({"_id": imgId}, safe=True) #Wait for replication? w=3 option
                    collectionMeta.remove({"_id": imgId}, safe=True)
                    removed = True
                except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                    self._log.warning("Autoreconnected.")
                except pymongo.errors.ConnectionFailure:
                    self._log.error("Connection failure. The file has not been updated")
                except IOError:
                    self._log.error("Error in ImgStorecumulusMongo - RemoveItem. " + str(sys.exc_info()))
                    self._log.error("No such file or directory. Image id: " + imgId)
                except TypeError:
                    self._log.error("TypeError in ImgStorecumulusMongo - RemoveItem " + str(sys.exc_info()))

                except pymongo.errors.OperationFailure:
                    self._log.error("Operation Failure in ImgStorecumulusMongo - RemoveItem")
                except:
                    self._log.error("Error in ImgStorecumulusMongo - removeItem. " + str(sys.exc_info()))
                finally:
                    self._dbConnection.disconnect()
            else:
                self._log.error("The Image does not exist or the user is not the owner")
        else:
            self._log.error("Could not get access to the database. The file has not been removed")

        return removed

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

            contain = self._cumulusConnection.get_bucket(self._containerName)

            if contain.get_key(imgId) != None:
                exists = True
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
        except TypeError:
            self._log.error("TypeError in ImgStoreMongo - existAndOwner")
        except bson.errors.InvalidId:
            self._log.error("Error, not a valid ObjectId in ImgStoreMongo - existAndOwner")
        except:
            self._log.error("Error in ImgStorecumulusMongo - existAndOwner. " + str(sys.exc_info()))

        if (exists and isOwner):
            return True
        else:
            return False

    ############################################################
    # cumulusConnection
    ############################################################
    def cumulusConnection(self):
        """
        Connect with Nimbus Cumulus
        
        """
        connected = False

        idu = self._userAdminS #'PgkhmT23FUv7aRZND7BOW'
        pw = self.getPassword(self._configFileS) #'Bf9ppgw9mzxe2EoKjbVl0wjaNJoHlIPxJ6QAgA0pOj'
        cf = OrdinaryCallingFormat()
        try:
            self._cumulusConnection = S3Connection(idu, pw, host=self._cumulusAddress, port=8888, is_secure=False, calling_format=cf)
            connected = True
        except:
            self._log.error("Error in cumulus connection. " + str(sys.exc_info()))

        return connected

        

class ImgMetaStoreCumulusMongo(ImgMetaStoreMongo):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, log):
        """
        Initialize object
        
        Keyword parameters:             
        _mongoaddress = mongos addresses and ports separated by commas
        _items = list of imgEntry
        _dbName = name of the database        
        """
        
        super(ImgMetaStoreMongo, self).__init__()

        self._dbName = "imagesC"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None
        
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._log = log

class IRUserStoreCumulusMongo(IRUserStoreMongo):

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

        self._dbName = "imagesC"   #file location for users
        self._usercollection = "users"
        self._dbConnection = None
        
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._log = log


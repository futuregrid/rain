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
        images.users     (users)

REMEBER: imgId will be _id (String) in the data collection, which is also _id (ObjectId) in fs.files. 
               In the first case it is an String and in the second one is an ObjectId
               
"""


#We get an AutoReconnect exception. This means that the driver was not able to connect to the old 
#primary (which makes sense, as we killed the server), but that it will attempt to automatically 
#reconnect on subsequent operations. When this exception is raised our application code needs to 
#decide whether to retry the operation or to simply continue, accepting the fact that the operation 
#might have failed.
#With authentication, it has to reauthenticate if this exception is raised

__author__ = 'Javier Diaz'

import pymongo
from pymongo import Connection
from pymongo.objectid import ObjectId
import gridfs
import bson
from datetime import datetime
import os
import re
import sys
from random import randrange
import ConfigParser
import string

from futuregrid.image.repository.server.IRDataAccess import AbstractImgStore
from futuregrid.image.repository.server.IRDataAccess import AbstractImgMetaStore
from futuregrid.image.repository.server.IRDataAccess import AbstractIRUserStore
from futuregrid.image.repository.server.IRTypes import ImgEntry
from futuregrid.image.repository.server.IRTypes import ImgMeta
from futuregrid.image.repository.server.IRTypes import IRUser


class ImgStoreMongo(AbstractImgStore):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, imgStore, log):
        """
        Initialize object
        
        Keyword parameters:             
        _mongoaddress = mongos addresses and ports separated by commas (optional if config file exits)
        _items = list of imgEntry
        _dbName = name of the database
        
        """
        super(ImgStoreMongo, self).__init__()
        
        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._log = log
        self._imgStore=imgStore
        
        self._dbName = "images"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None
        
        
        
    ############################################################
    # getItemUri
    ############################################################
    def getItemUri(self, imgId, userId):
        return "MongoDB cannot provide an image URI, try to retrieve the image."

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
        extension= []
        result = self.queryStore([imgId], imgLinks, userId, admin, extension)
        
        if (result):
            self._log.debug("extension: "+extension[0])
            filename = self._imgStore + "/" + imgId + "" + extension[0].strip()
            self._log.debug(filename)
            if not os.path.isfile(filename):
                f = open(filename, 'w')
            else:
                for i in range(1000):
                    filename = self._imgStore + "/" + imgId + "" + extension[0].strip() + "_" + i.__str__()
                    if not os.path.isfile(filename):
                        f = open(filename, 'w')
                        break

            f.write(imgLinks[0].read())   #read return an str
            f.close()

            return filename
        else:
            return None

    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgEntry1, requestInstance):
        """
        Add imgEntry to store or Update it if exists and the user is the owner
        
        keywords:
        imgEntry : Image information. 
        """
        #self._items.append(imgEntry)
        
        status = self.persistToStore([imgEntry1], requestInstance)

        return status
    """
    def updateItem(self, userId, imgId, imgEntry1):
        #what are we going to do with concurrency? because I need to remove the old file
        #Here we can implement the same syntax than in the Meta query method and it can 
              #be useful for both, since we update what the query ask to
        
        Update the item if imgId exists and your are the owner.
        
        IMPORTANT: if you want to update both imgEntry and imgMeta, 
                   you have to update first imgMeta and then imgEntry,
                   because imgEntry's update method change the _id of the imgMeta document
                
        keywords:
        imgId : identifies the image (I think that we can remove this)
        imgEntry : new info to update. 
        
        Return boolean
         
        imgUpdated=False
        if (self.mongoConnection()):            
            oldDeleted=False
            newimgId=""
                
            if (self.existAndOwner(imgId, userId)):
                try:
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink["data"]
                    collectionMeta = dbLink["meta"]
                    gridfsLink=gridfs.GridFS(dbLink)
                    
                    collection.update({"_id": imgId}, 
                                          {"$set": {"createdDate" : datetime.utcnow(), 
                                                    "lastAccess" : datetime.utcnow(),
                                                    "accessCount" : 0}
                                                    }, safe=True)
                    
                    #aux=item._imgURI.split("/")
                    #filename=aux[len(aux)-1].strip()      
                     
                    with open(imgEntry1._imgURI) as image:
                        imgIdOb = gridfsLink.put(image, chunksize=4096*1024) 
                                                           
                    newimgId=imgIdOb.__str__().decode('utf-8') # we store an String instead of an ObjectId.
                                                                                         
                    
                    #store the document in a variable
                    oldMeta = collectionMeta.find_one({"_id": imgEntry1._imgId})
                    oldData = collection.find_one({"_id": imgEntry1._imgId})
                    #set a new _id on the document
                    oldMeta['_id'] = newimgId
                    oldData['_id'] = newimgId
                    
                    #print "UpdateItem in ImgStoreMongo"
                    #print oldMeta
                    #print oldData
                    #insert the document, using the new _id
                    collectionMeta.insert(oldMeta, safe=True)
                    collection.insert(oldData, safe=True)
                    # remove the old document with the old _id
                    collection.remove({"_id": imgEntry1._imgId}, safe=True) #Wait for replication? w=3 option
                    collectionMeta.remove({"_id": imgEntry1._imgId}, safe=True)
                    oldDeleted=gridfsLink.delete(ObjectId(imgEntry1._imgId))
                    imgEntry1._imgId=newimgId        
                    imgUpdated=True
                    
                except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                    print "Autoreconnected."                 
                except pymongo.errors.ConnectionFailure:
                    print "Connection failure. The file has not been updated"                                           
                except IOError as (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                    print "No such file or directory. Image details: "+imgEntry1.__str__()+"\n"                 
                except TypeError as detail:
                    print "TypeError in ImgStoreMongo - UpdateImage"                
                except pymongo.errors.OperationFailure:
                    print "Operation Failure in ImgStoreMongo - UpdateImage"
                finally:
                    self._dbConnection.disconnect()
            else:
                print "The Image file has not been updated. The imgId is wrong or the User is not the owner"          
        else:            
            print "Could not get access to the database. The Image file has not been updated"
            
        if (re.search('^/tmp/', imgEntry1._imgURI)):
            cmd="rm -rf "+ imgEntry1._imgURI         
            os.system(cmd)
            
        return imgUpdated  
    """

    ############################################################
    # histImg 
    ############################################################
    def histImg (self, imgId):
        """
        Query DB to provide history information about the image Usage
        
        keyworks
        imgId: if you want to get info of only one image
        
        return list of imgEntry or None
        
        """
        self._items={}
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]


                if (imgId.strip() == "None"):
                    results = collection.find({}, ['_id', 'createdDate', 'lastAccess', 'accessCount'])
                else:
                    results = collection.find({'_id':imgId}, ['_id', 'createdDate', 'lastAccess', 'accessCount'])

                for dic in results:
                    tmpEntry = ImgEntry(dic['_id'], "", "", 0, "", str(dic['createdDate']).split(".")[0], str(dic['lastAccess']).split(".")[0], dic['accessCount'])                    
                    self._items[tmpEntry._imgId] = tmpEntry
                
                    
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgStoreMongo - histImg.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed.")
            except TypeError as detail:
                self._log.error("TypeError in ImgStoreMongo - histImg")
            except bson.errors.InvalidId:
                self._log.error("There is no Image with such Id. (ImgStoreMongo - histImg)")
            #except:
            #    self._log.error(str(sys.exc_info()))
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database.")

        if len(self._items) > 0:            
            return self._items
        else:
            return None


    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, imgIds, imgLinks, userId, admin, extension):
        """        
        Query the DB and provide the GridOut of the Images to create them with read method.    
        
        keywords:
        imgIds: this is the list of images that I need
        imgEntries: This is an output parameter. Return the list of GridOut objects
                      To read the file it is needed to use the read() method    
        """
        del imgLinks[:]
        itemsFound = 0

        if (self.mongoConnection()):
            try:

                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]
                gridfsLink = gridfs.GridFS(dbLink)
                for imgId in imgIds:

                    access = False
                    if(self.existAndOwner(imgId, userId) or admin):
                        access = True
                        #self._log.debug("ifowner "+str(access))
                    elif(self.isPublic(imgId)):
                        access = True
                        #self._log.debug("ifpublic "+str(access))
                    if (access):
                        imgLinks.append(gridfsLink.get(ObjectId(imgId)))

                        extension.append(collection.find_one({'_id':imgId})['extension'])
                        
                        collection.update({"_id": imgId},
                                      {"$inc": {"accessCount": 1}, }, safe=True)
                        collection.update({"_id": imgId},
                                      {"$set": {"lastAccess": datetime.utcnow()}, }, safe=True)
                        #print "here"                                         
                        itemsFound += 1
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgStoreMongo - queryStore.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed.")
            except TypeError as detail:
                self._log.error("TypeError in ImgStoreMongo - queryStore")
            except bson.errors.InvalidId:
                self._log.error("There is no Image with such Id. (ImgStoreMongo - queryStore)")
            except gridfs.errors.NoFile:
                self._log.error("File not found")
            #except:
            #    self._log.error(str(sys.exc_info()))
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

        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._datacollection]
                collectionMeta = dbLink[self._metacollection]
                gridfsLink = gridfs.GridFS(dbLink)
                for item in items:
                    #each imgType is stored in a different DB
                    #dbLink = self._dbConnection[self._dbNames.get(item._imgMeta._imgType)]                
                    """Store the file. 
                    The filename and the fileID are different in MongoDB.
                    We should include the filename in ImgEntry"""
                    """The default chunksize is 256kb. We should made tests with different sizes
                    4MB is the biggest and should be the most efficient for big binary files"""

                    if requestInstance == None:
                        with open(item._imgURI) as image:
                            imgId = gridfsLink.put(image, chunksize=4096 * 1024)
                    else:
                        requestInstance.file.seek(0)
                        imgId = gridfsLink.put(requestInstance.file, chunksize=4096 * 1024)

                    item._imgId = imgId.__str__().decode('utf-8') # we store an String instead of an ObjectId.
                    #item._imgMeta._imgId=imgId #not needed                                                                       

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
                self._log.error("Error in ImgStoreMongo - persistToStore. " + str(sys.exc_info()))
                self._log.error("No such file or directory. Image details: " + item.__str__())
            except TypeError:
                self._log.error("TypeError in ImgStoreMongo - persistToStore " + str(sys.exc_info()))
            except pymongo.errors.OperationFailure:
                self._log.error("Operation Failure in ImgStoreMongo - persistenToStore")
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
        if (self.mongoConnection()):
            if(self.existAndOwner(imgId, userId) or admin):
                try:
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._datacollection]
                    collectionMeta = dbLink[self._metacollection]
                    gridfsLink = gridfs.GridFS(dbLink)

                    aux = collection.find_one({"_id": imgId})
                    size[0] = aux['size']

                    gridfsLink.delete(ObjectId(imgId))
                    collection.remove({"_id": imgId}, safe=True) #Wait for replication? w=3 option
                    collectionMeta.remove({"_id": imgId}, safe=True)
                    removed = True
                except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                    self._log.warning("Autoreconnected.")
                except pymongo.errors.ConnectionFailure:
                    self._log.error("Connection failure. The file has not been updated")
                except IOError:
                    self._log.error("Error in ImgStoreMongo - removeitem. " + str(sys.exc_info()))
                    self._log.error("No such file or directory. Image details: " + imgId)
                except TypeError:
                    self._log.error("TypeError in ImgStoreMongo - removeitem " + str(sys.exc_info()))
                except pymongo.errors.OperationFailure:
                    self._log.error("Operation Failure in ImgStoreMongo - RemoveItem")
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
    def getOwner(self, imgId):
        """
        Get image Owner
        
        keywords:
        imgId: The id of the image
       
        
        Return: string
        """

        results = None
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._metacollection]


                aux = collection.find_one({"_id": imgId})

                if (aux != None):
                    results = aux['owner']
                #print isOwner                 
            except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                self._log.warning("Autoreconnected.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure")
            except TypeError as detail:
                self._log.error("TypeError in ImgStoreMongo - getOwner: " + str(detail))
            except bson.errors.InvalidId:
                self._log.error("Error, not a valid ObjectId in ImgStoreMongo - getOwner")
        else:
            self._log.error("Could not get access to the database. Cannot check img owner")
        return results

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
            gridfsLink = gridfs.GridFS(dbLink)

            exists = gridfsLink.exists(ObjectId(imgId))
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
    # isPublic
    ############################################################
    def isPublic(self, imgId):
        """
        To verify if the file is public
        
        keywords:
        imgId: The id of the image        
        
        Return: boolean
        """

        public = False

        try:
            dbLink = self._dbConnection[self._dbName]
            collection = dbLink[self._metacollection]

            aux = collection.find_one({"_id": imgId})

            if(aux['permission'] == "public"):
                public = True

        except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
            self._log.warning("Autoreconnected.")
        except pymongo.errors.ConnectionFailure:
            self._log.error("Connection failure")
        except TypeError as detail:
            self._log.error("TypeError in ImgStoreMongo - isPublic")
        except bson.errors.InvalidId:
            self._log.error("Error, not a valid ObjectId in ImgStoreMongo - isPublic")
        except gridfs.errors.NoFile:
            self._log.error("File not found")

        return public

    ############################################################
    # mongoConnection
    ############################################################
    def mongoConnection(self):
        """connect with the mongos available
        
        return: Connection object if succeed or False in other case
        
        """
        #TODO: change to a global connection??                
        connected = False
        try:
            self._dbConnection = Connection(self._mongoAddress)
            connected = True

        except pymongo.errors.ConnectionFailure as detail:
            self._log.error("Connection failed for " + self._mongoAddress)
        except TypeError:
            self._log.error("TypeError in ImgStoreMongo - mongoConnection")

        return connected
    #not used in mongodb yet, but it is used by swift and cumulus
    def getPassword(self, config):
        password=""
        self._config = ConfigParser.ConfigParser()
        if(os.path.isfile(config)):
            self._config.read(config)
        else:
            self._log.error("Configuration file "+config+" not found")
            sys.exit(1)
        
        section="client"
        try:
            password = self._config.get(section, 'password', 0)
        except ConfigParser.NoOptionError:
            self._log.error("No password option found in section " + section)
            sys.exit(1)  
        except ConfigParser.NoSectionError:
            self._log.error("no section "+section+" found in the "+config+" config file")
            sys.exit(1)
            
        return password
"""end of class"""

class ImgMetaStoreMongo(AbstractImgMetaStore):

    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, log):
        """
        Initialize object
        
        Keyword arguments:        
        _mongoaddress = mongos addresses and ports separated by commas (optional if config file exits)
        
        """
        super(ImgMetaStoreMongo, self).__init__()

        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._log = log
        
        self._dbName = "images"
        self._datacollection = "data"
        self._metacollection = "meta"
        self._dbConnection = None
       

    ############################################################
    # getItem
    ############################################################
    def getItem(self, imgId):
        criteria = "* where id=" + imgId
        return self.queryStore(criteria)

    ############################################################
    # addItem
    ############################################################
    def addItem(self, imgMeta):
        self._log.error("Please, use the ImgStoreMongo to add new items")

        return False


    ############################################################
    # existAndOwner
    ############################################################
    def existAndOwner(self, imgId, ownerId):
        """
        To verify that I am the owner
        
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
                        
            aux = collection.find_one({"_id": imgId, "owner": ownerId})
            if (aux == None):
                isOwner = False
            else:
                isOwner = True
                exists=True
            #print imgId
            #print ownerId               
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
    # updateItem
    ############################################################
    def updateItem(self, userId, imgId, imgMeta1):
        #what are we going to do with concurrency? because I need to remove the old file
        """
        IMPORTANT: if you want to update both imgEntry and imgMeta, 
                   you have to update first imgMeta and then imgEntry,
                   because imgEntry's update method change the _id of the imgMeta document
                   
        keywords:
        imgId : identifies the image (I think that we can remove this)
        imgMeta : new info to update. 
        
        Return boolean
        """
        imgUpdated = False

        if (self.mongoConnection()):
            
            if(self.existAndOwner(imgId, userId)):
                try:
                    dbLink = self._dbConnection[self._dbName]
                    #collection = dbLink[self._datacollection]
                    collectionMeta = dbLink[self._metacollection]

                    tags = imgMeta1._tag.split(",")
                    tags_list = [x.strip() for x in tags]

                    dic = {}
                    temp = imgMeta1.__repr__()

                    temp = temp.replace('\"', '')
                    #print temp
                    attributes = temp.split(',')

                    #Control tag
                    tagstr = ""
                    newattr = []
                    i = 0


                    while (i < len(attributes)):
                        if attributes[i].strip().startswith('tag='):
                            tagstr += attributes[i]
                            more = True
                            while(more):
                                if(attributes[i + 1].strip().startswith('vmType=')):
                                    more = False
                                else:
                                    tagstr += "," + attributes[i + 1]
                                    i += 1
                            newattr.append(tagstr)
                        else:
                            newattr.append(attributes[i])
                        i += 1

                    for item in newattr:
                        attribute = item.strip()
                        #print attribute
                        tmp = attribute.split("=")
                        key = tmp[0].strip()
                        value = tmp[1].strip()
                        if not (value == '' or key == "imgId" or key == "owner"):
                            #print key +"  "+value
                            if (key == "tag"):
                                tags = value.split(",")
                                tags_list = [x.strip() for x in tags]
                                dic[key] = tags_list
                            else:
                                dic[key] = value

                    self._log.debug(dic)
                    if len(dic) > 0:

                        collectionMeta.update({"_id": imgId},
                                          {"$set": dic }, safe=True)

                        imgUpdated = True


                except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                    self._log.warning("Autoreconnected.")
                except pymongo.errors.ConnectionFailure:
                    self._log.error("Connection failure. The file has not been updated")
                except IOError:
                    self._log.error("Error in ImgMetaStoreMongo - updateimage. " + str(sys.exc_info()))
                    self._log.error("No such file or directory. Image details: " + item.__str__())
                except TypeError:
                    self._log.error("TypeError in ImgMetaStoreMongo - updateimage " + str(sys.exc_info()))
                except pymongo.errors.OperationFailure:
                    self._log.error("Operation Failure in ImgMetaStoreMongo - UpdateImage")
                finally:
                    self._dbConnection.disconnect()
            else:
                self._log.error("The Information has not been updated. The imgId is wrong or the User is not the owner")
        else:
            self._log.error("Could not get access to the database. The Information has not been updated")

        return imgUpdated

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
        """
        Query the db and store the documents in self._items
        
        keyword:
           criteria:
                *      
                * where field=XX, field2=YY
                field1, field2    
                field1,field2 where field3=XX, field4=YY               
                
        TODO:  after the where, the two parts of the equal must be together with no white spaces.                
                                
        return list of dictionaries with the Metadata
        """
        self._items={}
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._metacollection]

                fieldsWhere = {}
                fields = []                
                criteria = criteria.strip()  #remove spaces before                
                beforewhere=""
                afterwhere=""
                if re.search("where",criteria):
                    beforewhere, afterwhere = criteria.split("where")  #splits in parts                    
                elif re.search("WHERE", criteria):
                    beforewhere, afterwhere = criteria.split("WHERE")  #splits in parts
                else:
                    beforewhere=criteria
                
                beforewhere=beforewhere.strip()
                afterwhere=afterwhere.strip()
                
                beforewhere = beforewhere.split(" ")                        
                args = [x.strip() for x in beforewhere]              
                for i in range(len(args)):
                    if (args[i] != " "):
                        if (args[i] == "*"):
                            del fields[:]
                            fields = "*"
                            break
                        else:
                            exit=False
                            aux = args[i].split(",")
                            aux1 = [z.strip() for z in aux]
                            for j in aux1:
                                if (j != ""):
                                    if (j == "*"):
                                        del fields[:]
                                        fields = "*"
                                        exit=True
                                        break                                    
                                    else:
                                        fields.append(j)
                            if exit:
                                break            
                if afterwhere != "":                    
                    afterwhere = string.replace(afterwhere,' ', '')                                        
                    aux = afterwhere.split(",")
                    aux1 = [z.strip() for z in aux]
                    for j in aux1:
                        if (j != ""):                                    
                            aux2 = j.split("=")
                                                                
                            if (aux2[0].strip() == "imgId" or aux2[0].strip() == "imgid"):
                                fieldsWhere["_id"] = aux2[1].strip()
                            #elif (aux2[0].strip() == "imgType" or aux2[0].strip() == "vmType" or aux2[0].strip() == "imgStatus"):
                            #   fieldsWhere[aux2[0].strip()]=int(aux2[1].strip())
                            else:
                                fieldsWhere[aux2[0].strip()] = aux2[1].strip()

                self._log.debug("fields " + fields.__str__())
                self._log.debug("fieldsWhere " + fieldsWhere.__str__())

                if (fields == "*"):
                    results = collection.find(fieldsWhere)
                    for resultList in results:
                        #print resultList
                        tmpMeta = self.convertDicToObject(resultList, True)
                        self._items[tmpMeta._imgId] = tmpMeta
                else:
                    results = collection.find(fieldsWhere, fields)
                    for resultList in results:
                        tmpMeta = self.convertDicToObject(resultList, False)
                        self._items[tmpMeta._imgId] = tmpMeta

                

            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgMetaStoreMongo - queryStore")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed")
            except TypeError as detail:
                self._log.error("TypeError in ImgMetaStoreMongo - queryStore "+ str(sys.exc_info()))
            except:
                self._log.error("TypeError in ImgMetaStoreMongo - queryStore. " + str(sys.exc_info()))
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. Query failed")

        if len(self._items) > 0:
            return True
        else:
            return False 

    def convertDicToObject(self, dic, fullMode):
        """
        This method convert a dictionary in a ImgMetaStoreMongo object
        
        keywords:
        dic: dictionary to convert
        fullMode: boolean. This indicates the way to convert the dic
        
        return: ImgMetaStoreMongo
        """
        if (fullMode):
            tags = ','.join(str(bit) for bit in dic['tag'])
            tmpMeta = ImgMeta(dic['_id'], dic['os'], dic['arch'], dic['owner'],
                                          dic["description"], tags, dic["vmType"],
                                          dic["imgType"], dic["permission"], dic["imgStatus"])
        else:
            tmpMeta = ImgMeta("", "", "", "", "", "", "", 0, "", "")
            for i in dic.keys():
                if (i == "_id"):
                    tmpMeta._imgId = dic[i]
                elif (i == "os"):
                    tmpMeta._os = dic[i]
                elif (i == "arch"):
                    tmpMeta._arch = dic[i]
                elif (i == "owner"):
                    tmpMeta._owner = dic[i]
                elif (i == "description"):
                    tmpMeta._description = dic[i]
                elif (i == "tag"):
                    tmpMeta._tag = ",".join(str(bit) for bit in dic[i])
                elif (i == "vmType"):
                    tmpMeta._vmType = dic[i]
                elif (i == "imgType"):
                    tmpMeta._imgType = dic[i]
                elif (i == "permission"):
                    tmpMeta._permission = dic[i]
                elif (i == "imgStatus"):
                    tmpMeta._imgStatus = dic[i]

        #print tmpMeta._tag

        return tmpMeta

    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, items):
        #this method is used only in ImgStoreMongo
        self._log.error("Data has not been stored. Please, use the ImgStoreMongo to add new items")

    ############################################################
    # removeItem 
    ############################################################
    def removeItem (self, imdId):
        #this method is used only in ImgStoreMongo
        self._log.error("Data has not been deleted. Please, use the ImgStoreMongo to delete items ")

    def genImgId(self):
        found = False
        imgId = None
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._metacollection]
                while not found:
                    imgId = str(randrange(999999999999999999999999))

                    aux = collection.find_one({"_id": imgId})

                    if (aux == None):
                        found = True

            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in ImgMetaStoreMongo - queryStore")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed")
            except TypeError as detail:
                self._log.error("TypeError in ImgMetaStoreMongo - genImgId")
            finally:
                self._dbConnection.disconnect()
        return imgId

    ############################################################
    # mongoConnection
    ############################################################
    def mongoConnection(self):
        """connect with the mongos available
        
        return: Connection object if succeed or False in other case
        
        """
        #TODO: change to a global connection??

        connected = False
        try:
            self._dbConnection = Connection(self._mongoAddress)
            connected = True

        except pymongo.errors.ConnectionFailure as detail:
            self._log.error("Connection failed for " + self._mongoAddress)
        except TypeError:
            self._log.error("TypeError in ImgStoreMongo - mongoConnection")

        return connected
    """
    #not used in mongodb yet
    def getPassword(self, config):
        password=""
        self._config = ConfigParser.ConfigParser()
        if(os.path.isfile(config)):
            self._config.read(config)
        else:
            self._log.error("Configuration file "+config+" not found")
            sys.exit(1)
        
        section="client"
        try:
            password = self._config.get(section, 'password', 0)
        except ConfigParser.NoOptionError:
            self._log.error("No password option found in section " + section)
            sys.exit(1)  
        except ConfigParser.NoSectionError:
            self._log.error("no section "+section+" found in the "+config+" config file")
            sys.exit(1)
            
        return password
    """

class IRUserStoreMongo(AbstractIRUserStore):
    '''
    User store existing as a file or db
    
    If we got a huge number of user ^^ try to create an index to accelerate searchs
         collection.ensure_index("userId")
    '''
    ############################################################
    # __init__
    ############################################################
    def __init__(self, address, userAdmin, configFile, log):
        super(IRUserStoreMongo, self).__init__()

        self._mongoAddress = address
        self._userAdmin = userAdmin
        self._configFile = configFile
        self._log = log
        
        self._dbName = "images"
        self._usercollection = "users"        
        self._dbConnection = None
        
    ############################################################
    # queryStore
    ############################################################
    def queryStore(self, userId, userIdtoSearch):
        """Get user from the store by Id'''
                
        Keyword arguments:
        userId = the username (it is the same that in the system)
                
        return: IRUser object
        """

        found = False
        tmpUser = {}

        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]

                if self.isAdmin(userId):
                    if userIdtoSearch == None:
                        dicList = collection.find()

                        for dic in dicList:
    
                            tmpUser[dic['userId']] = IRUser(dic['userId'], dic['cred'], dic['fsCap'], dic['fsUsed'], dic['lastLogin'],
                                                  dic["status"], dic["role"], dic["ownedImgs"])
                            found = True
                    else:
                        dic = collection.find_one({"userId": userIdtoSearch})

                        if not dic == None:
    
                            tmpUser[dic['userId']] = IRUser(dic['userId'], dic['cred'], dic['fsCap'], dic['fsUsed'], dic['lastLogin'],
                                                  dic["status"], dic["role"], dic["ownedImgs"])
                            found = True
                else:
                    dic = collection.find_one({"userId": userId})

                    if not dic == None:

                        tmpUser[dic['userId']] = IRUser(dic['userId'], dic['cred'], dic['fsCap'], dic['fsUsed'], dic['lastLogin'],
                                              dic["status"], dic["role"], dic["ownedImgs"])
                        found = True
                
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - queryStore")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure in IRUserStoreMongo - queryStore")
            except IOError:
                self._log.error("Error in ImgUserMongo - queryStore. " + str(sys.exc_info()))                
            except TypeError:
                self._log.error("TypeError in ImgUserMongo - queryStore " + str(sys.exc_info()))

            except pymongo.errors.OperationFailure:
                self._log.error("Operation Failure in IRUserStoreMongo - queryStore")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database.")


        if (found):
            return tmpUser
        else:
            return None

    def _getUser(self, userId):
        """Get user from the store by Id'''
                
        Keyword arguments:
        userId = the username (it is the same that in the system)
                
        return: IRUser object
        """

        user = self.queryStore(userId, userId)
        if(user != None):
            return user[userId]
        else:
            return None

    def updateAccounting (self, userId, size, num):
        """
        Update the disk usage of a user when it add a new Image
        
        keywords:
        userId
        size: size of the new image stored by the user.
        
        return: boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]

                user = collection.find_one({"userId": userId})

                totalSize = int(user['fsUsed']) + int(size)
                total = int(user['ownedImgs']) + int(num)

                if(totalSize < 0):
                    totalSize = 0
                if(total < 0):
                    total = 0

                collection.update({"userId": userId},
                                  {"$set": {"fsUsed" : totalSize, "ownedImgs":total}
                                            }, safe=True)
                success = True
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - updateAccounting")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - updateAccounting")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The disk usage has not been updated")

        return success

    ############################################################
    # last login
    ############################################################
    def updateLastLogin(self, userIdtoModify):
        """
        Modify the lastlogin date of a user.
        
        return boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]

                collection.update({"userId": userIdtoModify},
                                  {"$set": {"lastLogin" : datetime.utcnow()}
                                            }, safe=True)
                success = True
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - updateLastLogin")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - updateLastLogin")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The lastlogin date has not been changed")

        return success


    def setRole(self, userId, userIdtoModify, role):
        """
        Modify the role of a user. Only admins can do it
        
        return boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                if(self.isAdmin(userId)  and self._getUser(userIdtoModify) != None):
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._usercollection]

                    collection.update({"userId": userIdtoModify},
                                      {"$set": {"role" : role}
                                                }, safe=True)
                    success = True
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - setRole")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - setRole")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database.  The role has not been changed")

        return success

    ############################################################
    # setQuota
    ############################################################
    def setQuota(self, userId, userIdtoModify, quota):
        """
        Modify the quota of a user. Only admins can do it
        
        return boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                if(self.isAdmin(userId)  and self._getUser(userIdtoModify) != None):
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._usercollection]

                    collection.update({"userId": userIdtoModify},
                                      {"$set": {"fsCap" : quota}
                                                }, safe=True)
                    success = True
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - setRole")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - setRole")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The quota has not been changed")

        return success

    ############################################################
    # setUserStatus
    ############################################################
    def setUserStatus(self, userId, userIdtoModify, status):
        """
        Modify the status of a user. Only admins can do it
        
        return boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                if(self.isAdmin(userId) and self._getUser(userIdtoModify) != None ):
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._usercollection]

                    collection.update({"userId": userIdtoModify},
                                      {"$set": {"status" : status}
                                                }, safe=True)
                    success = True
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - setUserStatus")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - setUserStatus")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database.  The status has not been changed")

        return success


    ############################################################
    # userDel
    ############################################################
    def userDel(self, userId, userIdtoDel):
        """
        Modify the quota of a user. Only admins can do it
        
        return boolean
        """
        success = False

        if (self.mongoConnection()):
            try:
                if(self.isAdmin(userId) and self._getUser(userIdtoDel) != None):
                    dbLink = self._dbConnection[self._dbName]
                    collection = dbLink[self._usercollection]

                    collection.remove({"userId": userIdtoDel}, safe=True)

                    success = True

            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected in IRUserStoreMongo - userDel")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure: the query cannot be performed ")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - userDel")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The user has not been deleted")

        return success

    ############################################################
    # userAdd
    ############################################################
    def userAdd(self, userId, user):
        """
        Add user to the database. Only admins can do it
        
        keywords:
        user: IRUser object to be created
        userId: Id of the user that is executing this
        
        return boolean
        """
        return self.persistToStore(userId, [user])



    ############################################################
    # persistToStore
    ############################################################
    def persistToStore(self, userId, users):
        """
        Add user to the database. Only admins can do it
        
        keywords:
        users: list of IRUser object
        
        return boolean. True only if all users where added correctly to the db
        """
        userStored = 0
        authorized = False
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]
                output = collection.find_one()

                if (output == None):
                    self._log.warning("First User inserted is " + users[0]._userId + ". He is admin")
                    users[0]._status = "active"
                    users[0]._role = "admin"
                    authorized = True
                else:
                    if(self.isAdmin(userId)):
                        authorized = True

                if (authorized):
                    for user in users:

                        user._lastLogin = datetime.fromordinal(1) #creates time 0001-01-01 00:00:00

                        meta = {"userId": user._userId,
                                "cred" : user._cred,
                                "fsUsed" : user._fsUsed,
                                "fsCap"  : user._fsCap,
                                "lastLogin" : user._lastLogin,
                                "status" : user._status,
                                "role" : user._role,
                                "ownedImgs" : user._ownedImgs
                                }

                        if (collection.find_one({"userId": user._userId}) == None):
                            collection.insert(meta, safe=True)
                            userStored += 1
                        else:
                            self._log.error("The userId " + user._userId + " exits in the database")


            except pymongo.errors.AutoReconnect:  #TODO: Study what happens with that. store or not store the file
                self._log.warning("Autoreconnected.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure. The user has not been stored.")
            except IOError:
                self._log.error("Error in IRUserStoreMongo - addUser. " + str(sys.exc_info()))                
            except TypeError:
                self._log.error("TypeError in IRUserStoreMongo - addUser " + str(sys.exc_info()))
            except pymongo.errors.OperationFailure:
                self._log.error("Operation Failure in IRUserStoreMongo - addUser")
            finally:
                self._dbConnection.disconnect()
        else:
            self._log.error("Could not get access to the database. The user has not been stored")

        if (userStored >= 1):
            return True
        else:
            return False


    ############################################################
    # isAdmin
    ############################################################
    def isAdmin(self, userId):
        """
        Verify if a user is admin
        """
        admin = False
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]

                aux = collection.find_one({"userId": userId})
                if (aux != None):
                    if (aux['role'] == "admin"):
                        admin = True
                #print admin   
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - isAdmin" + str(sys.exc_info()))
            except bson.errors.InvalidId:
                self._log.error("Error, not a valid ObjectId in IRUserStoreMongo - isAdmin")
        else:
            self._log.error("Could not get access to the database. IsAdmin command failed")

        return admin

    def isEmpty(self):
        empty=True
        if (self.mongoConnection()):
            try:
                dbLink = self._dbConnection[self._dbName]
                collection = dbLink[self._usercollection]
                output = collection.find_one()

                if (output != None):
                    empty=False
                    
            except pymongo.errors.AutoReconnect:
                self._log.warning("Autoreconnected.")
            except pymongo.errors.ConnectionFailure:
                self._log.error("Connection failure")
            except TypeError as detail:
                self._log.error("TypeError in IRUserStoreMongo - isEmpty" + str(sys.exc_info()))
            except bson.errors.InvalidId:
                self._log.error("Error, not a valid ObjectId in IRUserStoreMongo - isEmpty")
        else:
            self._log.error("Could not get access to the database. IsAdmin command failed")

        return empty
   
    def getUserStatus(self, userId):
        """
        Get the status of a user
        """
        ret = ""
        if self.isEmpty(): #No users in the database
            ret ="Active"
        else:
            user = self._getUser(userId)
            
            if (user != None):
                if (user._status == "active"):                
                    ret = "Active"
                else:
                    ret = "NoActive"
            else:
                ret = "NoUser"

        return ret


    ############################################################
    # uploadValidator
    ############################################################
    def uploadValidator(self, userId, imgSize):
        user = self._getUser(userId)
        ret = False
        if (user != None):
            if (user._status == "active"):
                #self._log.debug(user._fsCap)                   
                if imgSize + user._fsUsed <= user._fsCap:
                    ret = True
            else:
                ret = "NoActive"
        else:
            ret = "NoUser"

        return ret

    ############################################################
    # mongoConnection
    ############################################################
    def mongoConnection(self):
        """connect with the mongos available
        
        return: Connection object if succeed or False in other case
        
        """
        #TODO: change to a global connection??

        connected = False
        try:
            self._dbConnection = Connection(self._mongoAddress)
            connected = True

        except pymongo.errors.ConnectionFailure as detail:
            self._log.error("Connection failed for " + self._mongoAddress)
        except TypeError:
            self._log.error("TypeError in IRUserStoreMongo - mongoConnection")

        return connected
    """
    #not used in mongodb yet
    def getPassword(self, config):
        password=""
        self._config = ConfigParser.ConfigParser()
        if(os.path.isfile(config)):
            self._config.read(config)
        else:
            self._log.error("Configuration file "+config+" not found")
            sys.exit(1)
        
        section="client"
        try:
            password = self._config.get(section, 'password', 0)
        except ConfigParser.NoOptionError:
            self._log.error("No password option found in section " + section)
            sys.exit(1)  
        except ConfigParser.NoSectionError:
            self._log.error("no section "+section+" found in the "+config+" config file")
            sys.exit(1)
            
        return password
    """

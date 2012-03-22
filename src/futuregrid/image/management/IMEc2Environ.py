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
Class to store the EC2 and S3 Information 
"""

__author__ = 'Javier Diaz'


class IMEc2Environ(object):
    
    ############################################################
    # __init__
    ############################################################
    def __init__(self):
        super(IMEc2Environ, self).__init__()

        self.ec2_url = self.s3_url = self.path = self.region = self.bucket = self.base_key = self.s3id = self.s3key = self.cannonicalid = ""
        self.ec2_port = self.s3_port = 0
        
    def setEc2_url(self, ec2_url):
        self.ec2_url=ec2_url
    def setEc2_port(self, ec2_port):
        self.ec2_port=ec2_port
    def setS3_url(self, s3_url):
        self.s3_url=s3_url
    def setS3_port(self, s3_port):
        self.s3_port=s3_port        
    def setPath(self, path):
        self.path=path
    def setRegion(self, region):
        self.region=region
    def setBucket(self, bucket):
        self.bucket=bucket
    def setBase_key(self, base_key):
        self.base_key=base_key
    def setS3id(self, s3id):#although it is called S3, it is the same for Ec2
        self.s3id=s3id
    def setS3key(self, s3key):#although it is called S3, it is the same for Ec2
        self.s3key=s3key
    def setCannonicalId(self, cannonicalid):
        self.cannonicalid=cannonicalid
    
    def getEc2_url(self):
        return self.ec2_url
    def getEc2_port(self):
        return self.ec2_port
    def getS3_url(self):
        return self.s3_url
    def getS3_port(self):
        return self.s3_port        
    def getPath(self):
        return self.path
    def getRegion(self):
        return self.region
    def getBucket(self):
        return self.bucket
    def getBase_key(self):
        return self.base_key
    def getS3id(self): #although it is called S3, it is the same for Ec2
        return self.s3id
    def getS3key(self): #although it is called S3, it is the same for Ec2
        return self.s3key
    def getCannonicalId(self):
        return self.cannonicalid

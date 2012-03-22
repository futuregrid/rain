The information about the usage and deployment of the image repository is maintened in https://portal.futuregrid.org/manual/dev/soft-deploy/fg-repo

This information can be outdated
--------------------------------

VER: 0.1a
------------
This is the alpha version of the FG Image Repository which layouts the
basic code framework and implements some basic functionality using
python.

The code tree structure:
|-- client
|   |-- IRClient.py
|   |-- IRServiceProxy.py
|   |-- IRTest.py
|   |-- IRUtil.py
|   |-- IRClientConf.py
|   `-- IRTypes.py
|-- README.txt
`-- server
    |-- IRDataAccessMongo.py
    |-- IRDataAccessMysql.py
    |-- IRDataAccess.py
    |-- IRService.py
    |-- IRTypes.py
    `-- IRUtil.py

It follows the architecture design document that has been developed in
the FG wiki. Please refer to the wiki SW-010 document for the detailed
info.
    
The code has two portions: server and client.

SERVER configuration:

All the configuration in the server side is done in the file
IRUtil.py. We can configure the backend or the image directory
used. In MongoDB we use __fgirimgstoremongo__ as a temporal dir, the
images are not stored there. Meawhile in MySQL the dir
__fgirimgstoremysql__ is where the images are stored.  We need to
create an empty file to put the logs and allow everyone to modify this
file. This file is identified by __logfile__ in IRUtil.py

-FileSystem (no DBs) #There is no new develpments

    Files with name 'IRMetaStore' and 'IRImgStore' should be created
    to store the image data.

-MongoDB

    Config example: __backend__="mongodb" __address__="localhost:23000"

    __backend__ indicates the MongoDB connection, it could be the
    address of the mongod process in a simple installation or the
    address of the mongos process in a distributed deployment (we
    recommend have mongos in the same machine that the IR server)
    Quotas and user managment Enabled. Commands only implemented in
    server side. First user added will be admin automatically for free
    ;). Users MUST be equals to the system user. Users MUST be
    activated with setUserStatus

-MySQL 

   Config example: __backend__="mysql" __address__="localhost"

   A directory with name specified in __fgirimgstoremysql__ must be
   created to store the real image files.  Create user IRUser and
   store the password in the file specified in __mysqlcfg__. The
   format is: [client] password=yourpass

   Quotas and user managment Enabled. Commands only implemented in
   server side. First user added will be admin automatically for free
   ;). Users MUST be equals to the system user. Users MUST be
   activated with setUserStatus

   #Creating DB and user
   mysql -u root -p
   CREATE USER 'IRUser'@'localhost' IDENTIFIED BY 'yourpass';
   create database images;
   use images;

   create table meta ( imgId varchar(100) primary key, os varchar(100), arch varchar(100), owner varchar(100), description varchar(200), tag varchar(200), vmType  varchar(100), imgType varchar(100), permission varchar(100), imgStatus varchar(100) );

   create table data ( imgId varchar(100) primary key, imgMetaData varchar(100), imgUri varchar(200), createdDate datetime, lastAccess datetime, accessCount long, FOREIGN KEY (imgMetaData) REFERENCES meta(imgId) ON UPDATE CASCADE ON DELETE CASCADE );

   create table users (userId varchar(100) primary key, cred varchar(200), fsCap long, fsUsed long,
lastLogin datetime, status varchar(100), role carchar(100));

   GRANT ALL PRIVILEGES ON images.* TO 'IRUser' IDENTIFIED BY 'yourpass';  

CLIENT configuration:

The client side is to be distributed to user environment from where
user can access the Image Repository. First you need to define where
is the software installed using the FG_PATH variable. By default will
be FG_PATH=/opt/futuregrid/futuregrid

Please note some configurations in etc/config need to be changed to
reflect your deployment. In later phase we'll provide intallation
script to do this automatically. The first one is the machine where
the server is deployed and the second one is the local directory where
the server is.

    serveraddr = "xray.futuregrid.org"
    serverdir = "/opt/futuregrid/futuregrid/image/repository/server/"
    
Users need to have access to the irstore where the images to be put,
and also the serverdir so the remote command could be executed.

To run the client, make sure that python is installed. Then

IRClient.py -h 

to get the help info on available commands.

PLEASE NOTE:

1. Some of the functionality is not yet implemented. Basic operations
like query, put, get, modify are supported.

2. SSH/SCP is used for authentication/authorization. This is not an
ideal way in long run since it lacks of fine-grained authorization.

3. We have a plan that improve this version with a> replace the file
based data access by a distributed DB based solution(MangoDB is now on
the list); b> convert the ssh and remote execution paradigm with
service based solution as the names already implied. However this need
to be in alignment with the security solution to be used, e.g., an
extra secret access token may be needed for each user..

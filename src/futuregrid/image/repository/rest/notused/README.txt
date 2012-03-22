REST

The REST interface implements the IRService API for a admin and a non
admin users from unique URLs.  The admin application name within the
URL would be specified as adminRest, while the non admin application
name within the URL would be specified as userRest.  For example going
to the URL https://<address>:<port>/adminRest/list would allow an
admin user to list all the users.



INVENTORY :

The Rest repository contains the following
Config files:  
httpConfig.conf     (specificiations for  the http server)  
httpsConfig.conf    (specifications for the https server)
adminConfig.conf    (admin user name specification)
userConfig.con      (general user name specification)

Test Files:  (twill required)
userTest.py
adminTest.py

Executables:
install
getDistribution.py

startMongo

startRestUser.py
startRestAdmin.py


FIRST TIME STARTUP

For first time execution you should run the scripts in the following
order: install ( to insture cherrypy, openssl, and mongodb are
installed)

startMongo <port #>
python startRest<"User.py"|"Admin.py">   (startRestUser.py for the user script,  startRestAdmin.py for admin script)


INSTALLATION

REST comes with dependencies: cherrypy, openssl, and mongodb and twill
for testing with using a browser. To ensure these dependencies are
loaded on your system type: install.  Check out the readme-install for
more specifics.


 
STARTING UP MONGODB

MONGODB is the database server. In order to start up the server, type
startMongo < port #> i.e startMongo 23000.  The mongod server will
start up on port 23000. The shell prompts you to hit enter again only
if you want to cleanly exit the mongod server.

STARTING UP REST SERVICE - Admin Users
Type -  python startRestAdmin.py , this script will start

STARTING UP REST SERVER - Non Admin Users
Type - python startRestUser.py 


Test scripts

The Rest service comes with two test scripts userTest.py and
adminTest.py.  These scripts use twill to automatically generate the
rest server without using a browser. For executing the user script
type: python userTest.py and for admin type : python adminTest.py.
There currently is not an installation procedure for checking if twill
is installed and wether or not to download twill if not the case.





Open SSL:

The install command will check if open ssl is installed and 
will generate the public, private keys and certificate if 
not already detected in the repository. T



The OpenSSL commands to generate the keys are the following:

To generate the server server.key with passphrase:
openssl genrsa -des3 -out server.key 2048

Remove pssphrase from the key :
openssl rsa -in server.key -out server.key

Generate the certificate:
openssl req -new -key server.key -out server.csr

To sign by private key:

openssl x509 -req -days 60 -in server.csr -signkey server.key -out server.crt


INSTALLATION
============

This REST installation requires cherrypy, openssl, and the mongo
distribution. To insure these dependencies are installed just type
./install.  The install script will call the getDistribution.py
script. This script is responsible for retrieving (via wget) the
correct distribution for your computer if the destribution has not
already been installed on your computer. The getDistributions.py
script will also check to insure that the pymongo, and cherrypy are
instaled as python imports.


The install script will continue to generate the library and install
it in the appropriate /usr/local paths. /usr/local/ssl for opensl and
/usr/local/mongodb for the mongo database library.  If the account
that executes install does not have the authority to install ssl and
mongodb in those directories the generated libraries be put in the
current directory path of the REST repository: ./ssl and ./mongodb

BUGS:

TODO: GVL: We have a patch file do we also need this for newer versions of cherry py?
TODO: distributions should be done with virtualenv and pip/easy install if possible




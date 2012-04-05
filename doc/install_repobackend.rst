.. _chap_install_repobackend:

Installing Image Repository Backends
====================================

Deployment of MongoDB
---------------------

In this section we are going to explain how to install a single MongoDB service. More information can be found in `MongoDB <http://www.mongodb.org/>`_

.. note::
      In MongoDB the databases and tables are created automatically
      
.. note::
      MongoDB is case sensitive
      

Install MongoDB on RHEL
***********************

* For all 64-bit RPM-based distributions with yum, create the file ``/etc/yum.repos.d/10gen.repo`` and add the following lines:

   ::

      [10gen]
      name=10gen Repository
      baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64
      gpgcheck=0
      
* Install MongoDB

   ::
   
      sudo yum install mongo-*

* Create DB directory

   ::
   
      sudo mkdir -p /data/db/
      sudo chown `id -u` /data/db     #The owner must be the user that is going to execute mongodb server
      
* Run MongoDB

   ::
   
      mongod --port 23000 --dbpath /data/db/ --fork --logpath=/data/db/mongo.log

**Rebuild spider monkey**

This is only needed if after running MongoDB you get warning message like this:

   ::

      warning: some regex utf8 things will not work.  pcre build doesn't have --enable-unicode-properties
      
Rebuilding spider monkey from RHEL (`Building Spider Monkey <http://www.mongodb.org/display/DOCS/Building+Spider+Monkey>`_). 

   ::

      sudo yum erase xulrunner
      sudo yum install curl
      curl -O ftp://ftp.mozilla.org/pub/mozilla.org/js/js-1.7.0.tar.gz
      tar zxvf js-1.7.0.tar.gz
      cd js/src
      export CFLAGS="-DJS_C_STRINGS_ARE_UTF8"
      make -f Makefile.ref
      JS_DIST=/usr make -f Makefile.ref export
 

Install MongoDB on Ubuntu 10.10
*******************************

* Add MongoDB repository to the aptitude soucers file ``/etc/apt/sources.list``.

   ::

      deb http://downloads.mongodb.org/distros/ubuntu 10.10 10gen

* Install MongoDB

   ::

      sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
      sudo apt-get update
      sudo apt-get install mongodb-stable


* Create DB directory

   ::

      sudo mkdir -p /data/db/ 
      sudo chown `id -u` /data/db
      Run MongoDB
      mongod --port 23000 --dbpath /data/db/ --fork --logpath=/data/db/mongo.log

Install MongoDB on MacOSX
*************************

Via homebrew (`MongoDB OSX <http://www.mongodb.org/display/DOCS/Quickstart+OS+X>`_)

* Install homebrew if you have not yet done

   ::
   
      ruby -e "$(curl -fsSLk https://gist.github.com/raw/323731/install_homebrew.rb)"
      
* Install mongodb via homebrew

   ::

      brew update
      brew install mongodb

* Create DB directory

   ::

      sudo mkdir -p /data/db/
      sudo chown `id -u` /data/db

* Run MongoDB

   ::
   
      /usr/local/Cellar/mongodb/1.6.5-x86_64/bin/mongod --port 23000 --dbpath /data/db/ --fork --logpath=/data/db/mongo.log
       
* Work with client by executing mongo localhost:23000 in a different terminal

   ::

      db.foo.save ( {a:1} )
      db.foo.find ()

* In case you use macports, replace two first steps with

   ::
   
      sudo port install mongodb  

Deployment of Cumulus
---------------------

In this section we are going to explain how to install and configure Cumulus. More information can be found in `Nimbus Project <http://www.nimbusproject.org/>`_

* Check the dependencies from the `Cumulus Requirements <http://www.nimbusproject.org/docs/2.8/admin/z2c/service-dependencies.html>`_.

* Download and Install the software

   ::
   
      wget http://www.nimbusproject.org/downloads/nimbus-iaas-2.9-src.tar.gz

      tar vxfz nimbus-iaas-2.9-src.tar.gz
      cd nimbus-iaas-2.9-src/cumulus
      sudo mkdir /opt/cumulus
      sudo chown -R user:user /opt/cumulus
      ./cumulus-install.sh /opt/cumulus/
      mkdir ~/.nimbus
      cp /opt/cumulus/etc/cumulus.ini ~/.nimbus


* Test the software

   ::

      cd /opt/cumulus/tests
      ./run-all.sh

* Run service

   ::

      /opt/cumulus/bin/cumulus &

* Create user

   ::

      /opt/cumulus/bin/cumulus-add-user javi
      
  * Output:
  
      ::
      
          ID : eqe0YoRAs2GT1sDvPZKAU
          password : S9Ii7QqcCQxDecrezMn6o5frSFvXhThYWmCE4S7nAf
          quota : None
          canonical_id : 048db304-6b4c-11df-897b-001de0a80259
          
.. note::

   Remember the ``ID`` and ``password`` to fill out the fg-server.conf file (the ``ID`` will be the ``userAdminS`` and the ``password`` will be in 
   the file specified in ``configfileS``). More details can be found in :ref:`Configure Image Repository <imagerepo_config>`.

* More Information

  * `Cumulus F.A.Q. <http://www.nimbusproject.org/docs/2.9/faq.html#cumulusnonimbus>`_
  * `Cumulus Video <http://www.mcs.anl.gov/~bresnaha/cumulus/cumulusinst.html>`_
  * `Cumulus Administrator Reference <http://www.nimbusproject.org/docs/2.9/admin/reference.html#cumulus>`_
  * `Cumulus Quickstarth <ttps://github.com/nimbusproject/nimbus/blob/master/cumulus/docs/QUICKSTART.txt>`_
  * `Cumulus Readme <https://github.com/nimbusproject/nimbus/blob/master/cumulus/docs/README.txt>`_

Deployment of MySQL
-------------------

In this section we are going to explain how to install and configure MySQL.

* Installing MySQL

   ::
      
      apt-get install mysql-client mysql-common mysql-server
      
      or
      
      yum install mysql mysql-server mysql-devel
      
* Login into Mysql

   ::
   
      mysql -u root -p
      
* Create User that will manage the image repository databases

   ::

      CREATE USER 'IRUser'@'localhost' IDENTIFIED BY 'complicatedpass';
      
* Create databases. The name of the database is different depending on the configuration selected in the Image Repository (see :ref:`Configure Image Repository <imagerepo_config>`).

         +----------------+---------------+--------------------------------+
         | Backend option | Database Name | Command to create the Database |
         +================+===============+================================+
         | mysql          | images        | create database images;        |
         +----------------+---------------+--------------------------------+
         | swiftmysql     | imagesS       | create database imagesS;       |
         +----------------+---------------+--------------------------------+
         | cumulusmysql   | imagesC       | create database imagesC;       |
         +----------------+---------------+--------------------------------+


* Create the tables for the selected database. This example is with the ``images`` databases. You will need to do the same with the others if you plan to use 
  these storage configurations.

  * Select the database to be used
  
      :: 
      
         use images;
         
  * Create tables

      ::

         create table meta ( imgId varchar(100) primary key, os varchar(100), arch varchar(100), owner varchar(100), description varchar(200), 
             tag varchar(200), vmType  varchar(100), imgType varchar(100), permission varchar(100), imgStatus varchar(100) );
         
         create table data ( imgId varchar(100) primary key, imgMetaData varchar(100), imgUri varchar(200), createdDate datetime, lastAccess datetime, 
              accessCount long, size long, extension varchar (50), FOREIGN KEY (imgMetaData) REFERENCES meta(imgId) ON UPDATE CASCADE ON DELETE CASCADE );
         
         create table users (userId varchar(100) primary key, cred varchar(200), fsCap long, fsUsed long, lastLogin datetime, status varchar(100), 
              role varchar(100), ownedimgs long);
              
  * Give all permission to the user created
  
      ::
      
         GRANT ALL PRIVILEGES ON images.* TO 'IRUser' IDENTIFIED BY 'userpassword';

.. note::

   Remember the ``userId`` (``IRUser``) and ``password`` (``userpassword``) to fill out the fg-server.conf file (the ``userId`` will be the ``userAdmin`` and 
   the ``password`` will be in the file specified in ``configfile``). More details can be found in :ref:`Configure Image Repository <imagerepo_config>`.

Deployment of Swift
-------------------

OpenStack provides some manuals to explain how to deploy Swift.

* Manual to deploy a `Test Infrastructure <http://swift.openstack.org/development_saio.html>`_.

* Manual to deploy a `Multi-Node Infrastructure <http://swift.openstack.org/howto_installmultinode.html>`_. In this case, we recommend 
  installing the proxy server in the same machine where the Image Repository is installed.


**Notes for RHEL 5**

* Install Python 2.6

   ::

      sudo rpm -Uvh http://yum.chrislea.com/centos/5/i386/chl-release-5-3.noarch.rpm
      sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CHL
      sudo yum install python26
      sudo yum install python26-devel
      
      or
      
      sudo wget ftp://ftp.univie.ac.at/systems/linux/fedora/epel/5/i386/epel-release-5-4.noarch.rpm
      sudo rpm -Uvh epel-release-5-4.noarch.rpm
      sudo yum install python26
      sudo yum install python26-devel

* Setuptools

   ::

      yum install python26-distribute

* Install python modules

   ::
   
      easy_install-2.6 netifaces eventlet setuptools virtualenv paste PasteDeploy webob pysqlite uuid xattr repoze.what configobj coverage formencode 
      netifaces nose paramiko paste pastedeploy pastescript scgi
      
* Install sqlite3

   ::
   
      wget http://dl.atrpms.net/el5-x86_64/atrpms/testing/sqlite-3.6.20-1.el5.x86_64.rpm
      wget http://dl.atrpms.net/el5-x86_64/atrpms/testing/sqlite-devel-3.6.20-1.el5.x86_64.rpm
      rpm -Uvh sqlite-3.6.20-1.el5.x86_64.rpm sqlite-devel-3.6.20-1.el5.x86_64.rpm

* Differences with the Swift manuals for the "Storage nodes"

  * Step 4. /etc/xinetd.d/rsync to enable it
  * Step 5. service xinetd restart
  * Iptable config (/etc/sysconfig/iptalbes). Add this:
  
    ::

      -A RH-Firewall-1-INPUT -p udp -m udp --dport 6000 -j ACCEPT
      -A RH-Firewall-1-INPUT -p tcp -m tcp --dport 6000 -j ACCEPT
      -A RH-Firewall-1-INPUT -p udp -m udp --dport 6001 -j ACCEPT
      -A RH-Firewall-1-INPUT -p tcp -m tcp --dport 6001 -j ACCEPT
      -A RH-Firewall-1-INPUT -p udp -m udp --dport 6002 -j ACCEPT
      -A RH-Firewall-1-INPUT -p tcp -m tcp --dport 6002 -j ACCEPT
      
  * If you don't have another partition, you can create a file. In this case we don't have xfs support, so we use ext3

    ::
     
      dd if=/dev/zero of=/srv/swift-disk bs=1024 count=0 seek=20000000
      mkfs.ext3 /srv/swift-disk

  * Edit /etc/fstab and add
  
    ::

      /srv/swift-disk /srv/node/sdb1 ext3  loop,noatime,user_xattr 0 0
          
  * Mount it
  
    ::
    
      mount /srv/swift-disk

.. note::

   Remember the ``userId:usergroup`` and ``password`` to fill out the fg-server.conf file (the ``userId:usergroup`` will be the ``userAdminS`` and the ``password`` will be in 
   the file specified in ``configfileS``). More details can be found in :ref:`Configure Image Repository <imagerepo_config>`. Swift users are defined in 
   the file ``/etc/swift/proxy-server.conf``.
   
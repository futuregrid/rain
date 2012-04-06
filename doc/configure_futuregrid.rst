.. _chap_configure_futuregrid:

Setting up the FutureGrid Software
==================================

Configuration Files
-------------------

There are two places where we can locate the configuration files. Our software will look into these places in the following order:   

#. In the directory ``~/.fg/``
#. In the directory ``/etc/futuregrid/`` 

If you have installed FutureGrid Rain using the tarball file (:ref:`Using a source tarball <source_tarball>`) you will find the configuration 
sample files in /etc/futuregrid/. Otherwise, you can download them as a :docs-tar:`tarball <configsamples>` or a :docs-zip:`ZIP file <configsamples>`.

**Server Side**: The configuration file has to be renamed as ``fg-server.conf``.

**Client Side**: The configuration file has to be renamed as ``fg-client.conf``. 

.. note::
   If you configure several clients or servers in the same machine, the ``fg-client.conf`` or ``fg-server.conf`` must be the same file.

.. note::
   In the **Client Side**, the path of the log files must be relative to each users. Using the ``$HOME`` directory is a good idea.

Setting up LDAP
---------------

The authentication of our software is based on LDAP. So, we need to configure some options in the configuration files to make it possible. 

Server Side
***********

We need to configure the ``[LDAP]`` section. This is going to be use by all servers. More information about this section 
of the server configuration file can be found in :ref:`LDAP section <fg-server_ldap>`.

   .. highlight:: bash

   ::
   
      [LDAP]
      LDAPHOST= ldap.futuregrid.org
      LDAPUSER= uid=rainadmin,ou=People,dc=futuregrid,dc=org
      LDAPPASS= passwordrainadmin
      log= ~/fg-auth.log


Client Side
***********

We need to configure the ``[LDAP]`` section. This is going to be use by the FutureGrid Shell. This allows the shell to store 
your encrypted password once it has been validated. In this way, you won't have to type to password again during that session. More information 
about this section of the client configuration file can be found in :ref:`LDAP section <fg-client_ldap>`.

   .. highlight:: bash

   ::
   
      [LDAP]
      LDAPHOST=ldap.futuregrid.org
      log=~/fg-auth.log


Setting up an http Server
-------------------------

This server will contain configuration files and kernel files that are needed by the different components of the FutureGrid software.

#. Setting up an Apache server.

   ::
     
      sudo yum install httpd
     
      or
     
      sudo apt-get install apache2

      sudo /etc/init.d/httpd start

#. Copy all configuration files into ``/var/www/html/`` or the directory specified in ``httpd.conf`` if you are not using the default options. 
   The configuration files are in the FutureGrid private svn.

Setting up the Image Repository
-------------------------------

In this section we explain how to configure the Image Repository.

.. _imagerepo_config:

Server Side
***********

In the Server side we need to configure several sections. The main one is the ``[RepoServer]`` and we have to create another section with the 
of the backend system that we want to use (see :ref:`RepoServer section <fg-server_reposerver>`). Our image repository support different 
backends that are described in the next table:

                  +----------------+-------------------------+----------------------+
                  | Backend option | Storage for Image Files | Storage for Metadata |
                  +================+=========================+======================+
                  | mysql          | Posix Filesystem        | MySQL                |
                  +----------------+-------------------------+----------------------+
                  | mongodb        | MongoDB                 | MongoDB              |
                  +----------------+-------------------------+----------------------+
                  | swiftmysql     | Swift                   | MySQL                |
                  +----------------+-------------------------+----------------------+
                  | swiftmmongo    | Swift                   | MongoDB              |
                  +----------------+-------------------------+----------------------+
                  | cumulusmysql   | Cumulus                 | MySQL                |
                  +----------------+-------------------------+----------------------+
                  | cumulusmmongo  | Cumulus                 | MongoDB              |
                  +----------------+-------------------------+----------------------+


.. note::

   Installation instructions for the software to be used as storage backend can be found in 
   :ref:`Installing Image Repository Backends <chap_install_repobackend>` 

Our predefined option is ``cumulusmongo``. Thus, the ``[RepoServer]`` section looks like:

   .. highlight:: bash

   ::

      [RepoServer]
      port = 56792
      proc_max = 10
      refresh = 20
      nopasswdusers = testuser:127.0.0.1,127.0.0.2; testuser2:127.0.0.1
      backend = cumulusmongo
      log = ~/reposerver.log
      log_level = debug
      ca_cert= /etc/futuregrid/certs/imdserver/cacert.pem
      certfile= /etc/futuregrid/certs/imdserver/imdscert.pem
      keyfile= /etc/futuregrid/certs/imdserver/privkey.pem
      restConfFile = /etc/futuregrid/fg-restrepo.conf

.. note::

   You may need to configure the iptables to open the port specified in the ``port`` option to allow the communication with the client.
   
Since we have specified ``backend = cumulusmongo``, we also have to add a section named ``[cumulusmongo]`` 
(see :ref:`Backend Example Section <repo_backend_example>`)

   .. highlight:: bash

   ::
   
      [cumulusmongo]
      address = localhost:23000
      userAdmin =
      configfile =
      addressS = 192.168.1.2
      userAdminS = PgkhmT23FUv7aRZND7BOW
      configfileS = /etc/futuregrid/cumulus.conf
      imgStore =/temp/

The ``imgStore`` directory is where the images are uploaded to the server via ssh. This is a temporal directory for all the different backends
but the mysql one. The permission of this directory must be 777 to allow everyone to upload images. Moreover, when this is used as temporal 
directory, **the bit t must be disabled** because the user that executes the server (i.e. ``imageman``) must be able to remove the images from 
the temporal directory after it has been uploaded to the final destination. By default any directory that you creates has this bit disabled. 
However, the /tmp directory existing in your system has this bit enabled.

The files specified in the ``configfile`` and ``configfileS`` options contain the password of the services. These files look like:

   .. highlight:: bash

   ::

      [client]
      password=complicatedpass


In case we want to use a different configuration, we may need to install the python modules to support that. 

   * MySQL (MySQL has to be installed before you install the python module)
   
     ::
      
      sudo easy_install MySQL-python
   
   * Swift
   
     ::
      
      sudo easy_install python-cloudfiles



Additionally, if we want to configure the Rest Interface Server, we need to specify the option ``restConfFile`` in ``[RepoServer]`` Section to identify its
configuration file. In this configuration file we need to specify the information about the Rest Interface. A simple configuration file is:

   .. highlight:: bash

   ::
   
      [global]
      log.error_file = 'cherrypy.error.log'
      log.accessfile = 'cherrypy.access.log'
      server.socket_host = "0.0.0.0"
      server.socket_port = 8443
      server.thread_pool = 10
      server.ssl_module="builtin"

To enable https, we need to install ``pyopenssl``,

   ::
   
    sudo easy_install python-cloudfiles
    
    or
    
    sudo apt-get/yum install python-openssl

have x509 certificates and modify the configuration file:

   .. highlight:: bash

   ::
   
      [global]
      log.error_file = 'cherrypy.error.log'
      log.accessfile = 'cherrypy.access.log'
      server.socket_host = "0.0.0.0"
      server.socket_port = 8443
      server.thread_pool = 10
      server.ssl_module="pyopenssl"
      server.ssl_certificate="server.crt"
      server.ssl_private_key="server.key"
      

Once you have the configuration files ready and the backend software installed, you can start the image repository and the rest interface 
servers by executing ``IRServer.py`` and ``IRRestServer.py`` respectively. 

.. note::
   We recommend to have a system user that run all the servers. In this way it will be easier to manage the sudoers file when necessary. 

.. _imagerepository_client_conf:

Client Side
***********

In the client side, we need to configure the ``[Repo]`` section. More information 
about this section of the client configuration file can be found in :ref:`Repo section <fg-client_repo>`.

   .. highlight:: bash

   ::
     
      [Repo]
      port = 56792
      serveraddr=localhost
      log=~/clientrepo.log
      log_level=debug
      ca_cert=/opt/futuregrid/futuregrid/etc/imdclient/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdclient/imdccert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdclient/privkey.pem
     
Once you have everything set up, you need to create the users in the image repository. Although users are managed in the LDAP server, the image
repository also maintain a database with users to control user's access, quotas, store statistics, etc. This database is also used by the rest 
of the framework The first user that you create will have the ``admin`` role by default. In this way, you can create more users. The command 
to add an user is:

   ::
      
       fg-repo --useradd <userid>

The executable file of this client is ``fg-repo``. More information about how to use the image repository can be found in the :ref:`Image Repository Manual <man-repo>`.

.. note::
   The userid created in the image repository must be the same that in LDAP.

Image Repository Check List
***************************

+-----------------+----------------------------------------------------------+--------------------------------------------------------------------------+
|                 | Server Side (``fg-server.conf``)                         | Client Side (``fg-client.conf``)                                         |
+=================+==========================================================+==========================================================================+
| **Access to**   | - Storage Backend                                        | - Users must be able to SSH the server machine to retrieve/upload images |
+-----------------+----------------------------------------------------------+--------------------------------------------------------------------------+
| **Configure**   | - ``[RepoServer]`` section                               | - ``[Repo]`` section                                                     |
|                 | - ``[LDAP]`` section                                     |                                                                          |
|                 | - Rest config file specified in ``[RepoServer]`` section |                                                                          |
+-----------------+----------------------------------------------------------+--------------------------------------------------------------------------+
| **Executables** | - ``IRServer.py`` (Server for CLI)                       | - ``fg-repo``                                                            |
|                 | - ``IRRestServer.py`` (Server for Rest Interface)        |                                                                          |
+-----------------+----------------------------------------------------------+--------------------------------------------------------------------------+



Setting up the Image Generator
------------------------------

In this section we explain how to configure the Image Generator

Server Side
***********

In the Server side we need to configure the ``[GenerateServer]`` Section (see :ref:`GenerateServer section <fg-server_generateserver>`). 

   .. highlight:: bash

   ::
   
      [GenerateServer]
      port = 56791
      proc_max = 5
      refresh = 20
      wait_max = 3600
      nopasswdusers = testuser:127.0.0.1,127.0.0.2;testuser2:127.0.0.1
      vmfile_centos = 5:/srv/cloud/one/share/examples/centos5_context.one,6:/srv/cloud/one/share/examples/centos6_context.one
      vmfile_rhel =
      vmfile_ubuntu = /srv/cloud/one/share/examples/ubuntu_context.one
      vmfile_debian =
      xmlrpcserver = http://localhost:2633/RPC2
      bridge = br1
      addrnfs = 192.168.1.6
      tempdirserver = /srv/scratch/
      tempdir = /media/
      http_server = http://fg-gravel.futuregrid.edu/
      oneuser = oneadmin
      onepass = f8377c90fcfd699f0ddbdcb30c2c9183d2d933ea
      log = ~/fg-image-generate-server.log
      log_level=debug
      ca_cert=/opt/futuregrid/futuregrid/etc/imdserver/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdserver/imdscert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdserver/privkey.pem

.. note::

   You may need to configure the iptables to open the port specified in the ``port`` option to allow the communication with the client.

As we described in the :ref:`Image Generation Section <sec_whatisimagegeneration>`, the Image Generator is supported by a IaaS cloud. 
Currently, we use `OpenNebula <http://www.opennebula.org/>`_ for this purpose. Therefore, it is a requirement to have an OpenNebula 
cloud installed and configured with at least one compute node. Additionally, you need to have the VMs that will be used to generate 
the images and the templates. The VM templates are specified in the 

   .. highlight:: bash

   ::
   
      #---------------------------------------
      # VM definition 
      #---------------------------------------      
      NAME = "centos5"      
      CPU    = 1
      MEMORY = 1024      
      OS = [
        arch="x86_64"
        ]
      DISK = [
        source   = "/srv/cloud/images/centos-5.6c1.img",
        target   = "hda",
        readonly = "no"
        ]      
      NIC = [ NETWORK_ID=0]
      NIC = [ NETWORK_ID=1]      
      FEATURES=[ acpi="no" ]      
      CONTEXT = [
         files = "/srv/cloud/images/centos/init.sh /srv/cloud/images/imageman_key.pub",
         target = "hdc",
         root_pubkey = "imageman_key.pub"
         ]      
      GRAPHICS = [
        type    = "vnc",
        listen  = "127.0.0.1"
        ]

Configure the scratch directory specified in the ``tempdirserver`` option. For that, we need to export via NFS the directory to allow the VMs
to mount as scratch disk. Assuming that the ``tempdirserver`` option is ``/srv/scratch`` and the subnet is ``192.168.1.0/24``, the configuration 
steps are:

#. Install NFS support

   ::

      sudo apt-get install nfs-common
      
      or
      
      sudo yum install nfs-utils
      
#. Create directories

   ::
   
      sudo mkdir -p /srv/scratch
      sudo chmod 777 /srv/scratch

#. Export directories. Edit ``/etc/exports`` file to insert the following line:

   ::   
      
      /srv/scratch 192.168.1.*(rw,async,no_subtree_check,no_root_squash) 192.168.1.*(rw,async,no_subtree_check,no_root_squash)
      
#. Refresh NFS server

   ::
      
      sudo exportfs -r
 

Configure user that is going to execute the server. Let's assume that the name of this user is ``imageman``:

#. Configure ssh to don't check the host id. This is needed for login into the VMs because the same IP will be associated to different 
   VMs over time. So, we need to edit the ``$HOME/.ssh/config`` file to insert the next lines. The permissons of this file is 644.

   ::
  
     Host *
           StrictHostKeyChecking no
     
#. Edit ``sudoers`` file by executing ``visudo`` as ``root`` user and add the following lines:

   ::

      imageman ALL=(ALL) NOPASSWD: /usr/bin/python *
      imageman ALL=(ALL) NOPASSWD: /usr/sbin/chroot *
      imageman ALL=(ALL) NOPASSWD: /bin/mount *
      imageman ALL=(ALL) NOPASSWD: /bin/umount *

Configure the Image Repository client because the Image Generation must be able to retrieve and upload images to the repository. See 
:ref:`Setting up Image Repository Client <imagerepository_client_conf>`. The ``imageman`` user must be able to ssh the Image Repository
Server machine without introducing password or passphrase. Therefore, we need to put the ``imageman`` public key in the ``authorized_keys``
of the machine where the Image Repository Server is running.

Once everything is set up you can start the server by execution ``IMGenerateServer.py`` as ``imageman`` user.


Client Side
***********

In the client side, we need to configure the ``[Generation]`` section. More information 
about this section of the client configuration file can be found in :ref:`Repo section <fg-client_repo>`.

   .. highlight:: bash

   ::
     
      [Generation]
      serveraddr = fg-gravel.futuregrid.edu
      port = 56791
      log=~/clientgen.log
      log_level=debug
      ca_cert=/opt/futuregrid/futuregrid/etc/imdclient/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdclient/imdccert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdclient/privkey.pem
      
The executable file of this client is ``fg-generate``.  More information about how to use the image generation can be found in the :ref:`Image Generation Manual <man-generate>`.


Image Generation Check List
***************************

+-----------------+--------------------------------------------------------------------------------------+-------------------------------------------------------------------+
|                 | Server Side (``fg-server.conf``)                                                     | Client Side (``fg-client.conf``)                                  |
+=================+======================================================================================+===================================================================+
| **Access to**   | - OpenNebula Cloud                                                                   | - Users must be able to SSH the server machine to retrieve images |
|                 | - Image Repository (ssh access with no password or passphrase to the server machine) |                                                                   |
+-----------------+--------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| **Configure**   | - ``[GenerateServer]`` section                                                       | - ``[Generation]`` section                                        |
|                 | - ``[LDAP]`` section                                                                 |                                                                   |
|                 | - ``/etc/sudoers`` file                                                              |                                                                   |
|                 | - Export scratch directory for VMs                                                   |                                                                   |
|                 | - Image Repository client                                                            |                                                                   |
+-----------------+--------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| **Executables** | - ``IMGenerateServer.py`` (Server for CLI)                                           | - ``fg-generate``                                                 |
+-----------------+--------------------------------------------------------------------------------------+-------------------------------------------------------------------+


Setting up the Image Registrator
--------------------------------

In this section we explain how to configure the Image Registrator for Cloud and HPC infrastructures.

Server Side for Cloud infrastructures
*************************************

Here we need to configure the ``[RegisterServerIaas]`` Section (see :ref:`RegisterServerIaas section <fg-server_registerserveriaas>`). 

   .. highlight:: bash

   ::

      [RegisterServerIaas]
      port = 56793
      proc_max = 5
      refresh = 20
      nopasswdusers = testuser:127.0.0.1,127.0.0.2;testuser2:127.0.0.1
      tempdir = /temp/
      http_server=http://fg-gravel.futuregrid.edu/
      default_eucalyptus_kernel = 2.6.27.21-0.1-xen
      eucalyptus_auth_kernels = 2.6.27.21-0.1-xen:eki-78EF12D2:eri-5BB61255; 2.6.27.21-0.1-xen-test:eki-test:eri-test
      default_nimbus_kernel = 2.6.27.21-0.1-xen
      nimbus_auth_kernels = 2.6.27.21-0.1-xen:2.6.27.21-0.1-xen:2.6.27.21-0.1-xen; test1:test1:test1
      default_openstack_kernel = 2.6.28-11-generic
      openstack_auth_kernels = 2.6.28-11-generic:aki-00000026:ari-00000027
      default_opennebula_kernel = 2.6.35-22-generic
      opennebula_auth_kernels = 2.6.35-22-generic: /srv/cloud/images/vmlinuz-2.6.35-22-generic:/srv/cloud/images/initrd-2.6.35-22-generic.img
      log = ~/fg-image-register-server-iaas.log
      log_level = debug
      ca_cert=/opt/futuregrid/futuregrid/etc/imdserver/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdserver/imdscert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdserver/privkey.pem

Configure user that is going to execute the server. Let's assume that the name of this user is ``imageman`` and the ``tempdir`` option is ``/temp/``. 
We need to edit the ``sudoers`` file by executing ``visudo`` as ``root`` user and add the following lines:

   ::

      Defaults:imageman    !requiretty
      User_Alias SOFTWAREG = imageman
      Cmnd_Alias IMMANCOMND = 
                           /bin/chmod * /temp/*, \                           
                           /bin/mkdir -p /temp/*, \                           
                           /bin/mount -o loop /temp/* /temp/*, \                           
                           /bin/rm [-]* /temp/*, \                           
                           /bin/sed -i s/enforcing/disabled/g /temp/*, \                           
                           /bin/tar xvfz /temp/* -C /temp/*, \                           
                           /bin/umount /temp/*, \                           
                           /usr/bin/tee -a /temp/*, \
                           /usr/sbin/chroot /temp/*, \
                           /usr/bin/wget * -O /temp/*, \
                           /bin/tar xfz /temp/* --directory /temp/*, \
                           /bin/mv -f /temp/* /temp/*, \
                           /bin/chown root\:root /temp/*
      SOFTWAREG ALL = NOPASSWD: IMMANCOMND

Configure the Image Repository client because the Image Generation must be able to retrieve and upload images to the repository. See 
:ref:`Setting up Image Repository Client <imagerepository_client_conf>`. The ``imageman`` user must be able to ssh the Image Repository
Server machine without introducing password or passphrase. Therefore, we need to put the ``imageman`` public key in the ``authorized_keys``
of the machine where the Image Repository Server is running.

Once everything is set up you can start the server by execution ``IMRegisterServerIaas.py`` as ``imageman`` user.

Server Side for HPC infrastructures
***********************************

As we described in the :ref:`Image Registration Section <sec_whatisimageregistration>`, the Image Registration for HPC is supported 
by a xCAT and Moab. Therefore, it is a requirement to have an such software installed in our HPC infrastructure. To interact with 
xCAT and Moab we have two services called ``IMRegisterServerXcat.py`` and ``IMRegisterServerMoab.py``, respectively.

The ``IMRegisterServerXcat.py`` will copy the image into the xCAT directories and register the image in the xCAT tables. Our service
can run in any machine that has the    
`xCAT client <http://sourceforge.net/apps/mediawiki/xcat/index.php?title=Granting_Users_xCAT_privileges>`_ configured 
and access to the directories ``/install/netboot/``, ``/tftpboot/`` and ``/etc/xcat``. The directories can be mounted via NFS and we
only make changes in the first two directories. The last one is needed for xCAT client.

Here we need to configure the ``[RegisterServerXcat]`` Section (see :ref:`RegisterServerXcat section <fg-server_registerserverxcat>`). 

   .. highlight:: bash

   ::

      [RegisterServerXcat]
      xcat_port=56789
      xcatNetbootImgPath=/install/netboot/
      nopasswdusers = testuser:127.0.0.1,127.0.0.0;testuser:127.0.0.1
      http_server=http://fg-gravel.futuregrid.edu/
      log=fg-image-register-server-xcat.log
      log_level=debug
      test_mode=False
      default_xcat_kernel_centos = 5:2.6.18-164.el5,6:2.6.32-220.4.2.el6
      default_xcat_kernel_ubuntu = karmic:2.6.35-22-generic,lucid:2.6.35-22-generic,maverick:2.6.35-22-generic,natty:2.6.35-22-generic
      auth_kernels_centos = 5:2.6.18-164.el5,2.6.18-164.el5-test12; 6:2.6.32-220.4.2.el6, 2.6.32-220.4.2.el6-test
      auth_kernels_ubuntu = karmic:2.6.35-22-generic,2.6.35-22-generic-test; lucid:2.6.35-22-generic;maverick:2.6.35-22-generic,2.6.35-22-generic-test12;natty:2.6.35-22-generic
      tempdir=/temp/
      ca_cert=/opt/futuregrid/futuregrid/etc/imdserver/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdserver/imdscert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdserver/privkey.pem
      max_diskusage=88


Configure user that is going to execute the server. Let's assume that the name of this user is ``imageman``  and the ``tempdir`` option is ``/temp/``.
We need to edit the ``sudoers`` file by executing ``visudo`` as ``root`` user and add the following lines:

   ::

      Defaults:imageman    !requiretty
      User_Alias SOFTWAREG = imageman
      Cmnd_Alias IMMANCOMND = /bin/chmod 600 /install/netboot/*, \
                           /bin/chmod 644 /install/netboot/*, \
                           /bin/chmod 755 /install/netboot/*, \
                           /bin/chmod 777 /install/netboot/*, \
                           /bin/chmod +x /install/netboot/*, \
                           /bin/chmod * /temp/*, \
                           /bin/chown root\:root /install/netboot/*, \
                           /bin/cp /install/netboot/* *, \
                           /bin/cp [-]* /install/netboot/* , \
                           /bin/mkdir -p /install/netboot/*, \
                           /bin/mkdir -p /install/netboot/*, \
                           /bin/mkdir -p /install/netboot/* /install/netboot/*, \
                           /bin/mkdir -p /tftpboot/xcat/*, \
                           /bin/mkdir -p /temp/*, \
                           /bin/mount -o loop /install/netboot/* /install/netboot/*, \
                           /bin/mount -o loop /temp/* /temp/*, \
                           /bin/mv -f /install/netboot/* /install/netboot/*, \
                           /bin/mv -f /temp/* /install/netboot/*, \
                           /bin/mv /install/netboot/* /install/netboot/*, \
                           /bin/rm [-]* /install/netboot/*, \
                           /bin/rm [-]* /temp/*, \
                           /bin/sed -i s/enforcing/disabled/g /install/netboot/*, \
                           /bin/sed -i * /install/netboot/*, \
                           /bin/sed -i s/enforcing/disabled/g /temp/*, \
                           /bin/tar xfz /install/netboot/* -C /install/netboot/*, \
                           /bin/tar xfz /install/netboot/* --directory /install/netboot/*, \
                           /bin/tar xvfz /temp/* -C /temp/*, \
                           /bin/umount /install/netboot/*, \
                           /bin/umount /temp/*, \
                           /usr/bin/tee -a /install/netboot/*, \
                           /usr/bin/tee -a /temp/*, \
                           /usr/bin/tee -a /opt/moab//tools/msm/images.txt, \
                           /usr/bin/wget * -O /install/netboot/*, \
                           /usr/bin/wget * -O /tftpboot/xcat/*, \
                           /usr/sbin/chroot /install/netboot/*, \
                           /usr/sbin/chroot /temp/*, \
                           /usr/bin/wget * -O /temp/*, \
                           /bin/tar xfz /temp/* --directory /temp/*, \
                           /bin/mv -f /temp/* /temp/*, \
                           /bin/chown root\:root /temp/*
      SOFTWAREG ALL = NOPASSWD: IMMANCOMND

Configure the Image Repository client because the Image Generation must be able to retrieve and upload images to the repository. See 
:ref:`Setting up Image Repository Client <imagerepository_client_conf>`. The ``imageman`` user must be able to ssh the Image Repository
Server machine without introducing password or passphrase. Therefore, we need to put the ``imageman`` public key in the ``authorized_keys``
of the machine where the Image Repository Server is running.

Once everything is set up you can start the server by execution ``IMRegisterServerXcat.py`` as ``imageman`` user.

On the other hand, we have the ``IMRegisterServerMoab.py`` that register the image in Moab. This server must be running in the same machine
where Moab is. In our case, it is running on the Login node. This server is very light as it only modify the ``/opt/moab/tools/msm/images.txt`` 
file and recycle the Moab scheduler.

Here we need to configure the ``[RegisterServerMoab]`` Section (see :ref:`RegisterServerMoab section <fg-server_registerservermoab>`). 

   .. highlight:: bash

   ::

      [RegisterServerMoab]
      moab_port = 56790
      moabInstallPath = /opt/moab/
      log = /var/log/fg/fg-image-register-server-moab.log
      log_level = debug
      ca_cert=/etc/futuregrid/imdserver/cacert.pem
      certfile=/etc/futuregrid/imdserver/imdscert.pem
      keyfile=/etc/futuregrid/imdserver/privkey.pem

Configure user that is going to execute the server. Let's assume that the name of this user is ``imageman``. We need to edit the ``sudoers`` 
file by executing ``visudo`` as ``root`` user and add the following lines:

   ::
   
      Defaults:imageman    !requiretty
      User_Alias SOFTWAREG = imageman
      Cmnd_Alias IMMANCMND = /usr/bin/tee -a /opt/moab/tools/msm/images.txt, \
                             /opt/moab/bin/mschedctl -R
      SOFTWAREG ALL = NOPASSWD: IMMANCOMND
      
Once everything is set up you can start the server by execution ``IMRegisterServerMoab.py`` as ``imageman`` user.
      
Client Side
***********

In the client side, we need to configure the ``[Register]`` section. More information 
about this section of the client configuration file can be found in :ref:`Repo section <fg-client_repo>`.

   .. highlight:: bash

   ::
     
      [Register]
      xcat_port = 56789
      moab_port = 56790
      iaas_serveraddr = localhost
      iaas_port = 56793
      http_server = http://fg-gravel.futuregrid.edu/
      log=~/clientregister.log
      log_level=debug
      ca_cert=/opt/futuregrid/futuregrid/etc/imdclient/cacert.pem
      certfile=/opt/futuregrid/futuregrid/etc/imdclient/imdccert.pem
      keyfile=/opt/futuregrid/futuregrid/etc/imdclient/privkey.pem

We also need to configure a section per machine supported. In our case, we support two machines ``[minicluster]`` and ``[india]``. In this way, 
users can specify the machine where they want to register their images.

   .. highlight:: bash

   ::
     
      [minicluster]      
      loginmachine=localhost
      moabmachine=localhost
      xcatmachine=localhost
      
      [india]
      loginmachine=<machine_address1>
      moabmachine=<machine_address1>
      xcatmachine=<machine_address1>

We use the euca2tools to register images in the Eucalyptus and OpenStack cloud infrastructures. Thus, they are required to be available.  

The executable file of this client is ``fg-register``.  More information about how to use the Image Registration can be found 
in the :ref:`Image Registration Manual <man-register>`.


Image Registration Check List
*****************************

+-----------------+------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
|                 | Server Side Cloud (``fg-server.conf``)                                       | Server Side HPC (``fg-server.conf``)                                                                                 | Server Side Moab (``fg-server.conf``)          | Client Side (``fg-client.conf``)                                                                                   |
+=================+==============================================================================+======================================================================================================================+================================================+====================================================================================================================+
| **Access to**   | - Image Repository (ssh access no password/passphrase to the server machine) | - Image Repository (ssh access no password/passphrase to the server machine)                                         | - Execute in the machine where Moab is running | - Users must be able to SSH the machine where the ``IMRegisterServerIaas.py`` server is running to retrieve images |
|                 |                                                                              | - ``/install/netboot/``, ``/tftpboot/`` and ``/etc/xcat/`` directories of the machine where xCAT server is installed | - ``/etc/moab/tools/msm/images.txt`` file      | - Eucalyptus (Euca2ools), OpenStack (Euca2ools), Nimbus (boto) and OpenNebula                                      |
+-----------------+------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
| **Configure**   | - ``[RegisterServerIaas]`` section                                           | - ``[RegisterServerIaas]`` section                                                                                   | - ``[RegisterServerMoab]`` section             | - ``[Register]`` section                                                                                           |
|                 | - ``[LDAP]`` section                                                         | - ``[LDAP]`` section                                                                                                 | - ``/etc/sudoers`` file                        |                                                                                                                    |
|                 | - ``/etc/sudoers`` file                                                      | - ``/etc/sudoers`` file                                                                                              |                                                |                                                                                                                    |
|                 | - Image Repository client                                                    | - xCAT client                                                                                                        |                                                |                                                                                                                    |
|                 |                                                                              | - Image Repository client                                                                                            |                                                |                                                                                                                    |
+-----------------+------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
| **Executables** | - ``IMRegisterServerIaas.py`` (Server for CLI)                               | - ``IMRegisterServerXcat.py`` (Server for CLI)                                                                       | - ``IMRegisterServerMoab.py``                  | - ``fg-register``                                                                                                  |
+-----------------+------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+


Setting up the Rain
-------------------

In this section we explain how to configure the Rain.

Client Side
***********

Rain is currently under development and therefore its functionality is limited. The current functionality allows users to place images onto resources and run their jobs.
Hence, it makes use of the image management tools and the infrastructures clients. This means that we need to configure the ``[Rain]`` section of the 
``fg-client.conf`` file and the rest of the image management components. More information about this section of the client configuration file can be 
found in :ref:`Rain section <fg-client_rain>`.

   .. highlight:: bash
   
   ::
   
      [Rain]
      moab_max_wait = 480
      moab_images_file = /opt/moab/tools/msm/images.txt
      refresh = 20
      log=~/clientrain.log
      log_level=debug

The executable file of this client is ``fg-rain``.  More information about how to use the Rain can be found in the :ref:`Rain Manual <man-rain>`.


Rain Check List
***************

+-----------------+---------------------------------------------------------------------------------------+
|                 | Client Side (``fg-client.conf``)                                                      |
+=================+=======================================================================================+
| **Access to**   | - Moab/Torque client                                                                  |
|                 | - Eucalyptus, OpenStack, Nimbus and OpenNebula                                        |
|                 | - FutureGrid Image Management services                                                |
+-----------------+---------------------------------------------------------------------------------------+
| **Configure**   | - ``[Rain]`` section                                                                  |
|                 | - Client and Servers of the Image Repository, Generation and Registration componenets |
+-----------------+---------------------------------------------------------------------------------------+
| **Executables** | - ``fg-rain``                                                                         |
+-----------------+---------------------------------------------------------------------------------------+

Setting up the FutureGrid Shell
-------------------------------

In this section we explain how to configure the FutureGrid Shell.

The FutureGrid Shell is a client side interface. Therefore, we need to configure the ``[fg-shell]`` section of the ``fg-client.conf`` file. 
More information about this section of the client configuration file can be found in :ref:`fg-shell section <fg-client_fgshell>`. 

   .. highlight:: bash
   
   ::

      [fg-shell]
      history=~/fgshellhist.txt
      log=~/fg-shell.log
      log_level=debug

Since this shell is a wrapper for our tools, we need to configure each individual tool before we can use all the advantages of the shell. Moreover, we need to configure the 
``[LDAP]`` section in the ``fg-client.conf`` file.

The executable file of this client is ``fg-shell``.  More information about how to use the FutureGrid Shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.


FutureGrid Shell Check List
***************************

+-----------------+---------------------------------------------------------------------------------------+
|                 | Client Side (``fg-client.conf``)                                                      |
+=================+=======================================================================================+
| **Access to**   | - FutureGrid Image Management services                                                |
+-----------------+---------------------------------------------------------------------------------------+
| **Configure**   | - ``[fg-shell]`` section                                                              |
|                 | - ``[LDAP]`` section                                                                  |
|                 | - Client and Servers of the Image Repository, Generation and Registration componenets |
+-----------------+---------------------------------------------------------------------------------------+
| **Executables** | - ``fg-shell``                                                                        |
+-----------------+---------------------------------------------------------------------------------------+




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

Setting up LDAP
---------------

The authentication of our software is based on LDAP. So, we need to configure some options in the configuration files to make it possible. 

**Server Side**

We need to configure the ``[LDAP]`` section. This is going to be use by all servers. More information about this section 
of the server configuration file can be found in :ref:`LDAP section <fg-server_ldap>`

   ::
   
      [LDAP]
      LDAPHOST= ldap.futuregrid.org
      LDAPUSER= uid=rainadmin,ou=People,dc=futuregrid,dc=org
      LDAPPASS= passwordrainadmin
      log= ~/fg-auth.log


**Client Side**

We need to configure the ``[LDAP]`` section. This is going to be use by the FutureGrid Shell. This allows the shell to store 
your encrypted password once it has been validated. In this way, you won't have to type to password again during that session. More information 
about this section of the client configuration file can be found in :ref:`LDAP section <fg-client_ldap>`

   ::
   
      [LDAP]
      LDAPHOST=ldap.futuregrid.org
      log=~/fg-auth.log


Setting up the Image Repository
-------------------------------

In this section we explain how to configure the Image Repository

**Server Side**


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

Since we have specified ``backend = cumulusmongo``, we also have to add a section named ``[cumulusmongo]`` 
(see :ref:`cumulusmongo Section <fg-server_cumulusmongo>`)

   ::
   
      [cumulusmongo]
      address = localhost:23000
      userAdmin =
      configfile =
      addressS = 192.168.1.2
      userAdminS = PgkhmT23FUv7aRZND7BOW
      configfileS = /etc/futuregrid/cumulus.conf
      imgStore =/temp/


The files specified in the ``configfile`` and ``configfileS`` options contain the password of the services. These files look like:

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



Additionally, if we want to configure the Rest Interface Server, we need to specify in ``RepoServer`` the option ``restConfFile`` to identify its
configuration file. In this configuration file we need to specify the information about the Rest Interface. A simple configuration file is:

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
servers by executing ``IRServer.py`` and ``IRRestServer`` respectively. 

.. note::
   We recommend to have a system user that run all the servers. In this way it will be easier to manage the sudoers file when necessary. 

**Client Side**

In the client side, we need to configure the section ``[Repo]``. More information 
about this section of the client configuration file can be found in :ref:`Repo section <fg-client_repo>`

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

More information about how to use the image repository can be found in 

.. warning:: link to the image repository user manual

.. note::
   The userid created in the image repository must be the same that in LDAP.

Setting up the Image Generator
------------------------------

In this section we explain how to configure the Image Generator


**Server Side**

**Client Side**

Setting up the Image Registrator
--------------------------------

In this section we explain how to configure the Image Registrator


**Server Side**

**Client Side**

Setting up the Image Rain
-------------------------

In this section we explain how to configure the Rain


**Server Side**

**Client Side**

Setting up the FutureGrid Shell
-------------------------------

In this section we explain how to configure the FutureGrid Shell


**Server Side**

**Client Side**

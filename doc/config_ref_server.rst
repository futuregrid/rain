.. _sec_fg-server.conf:

``fg-server.conf`` configuration file
-------------------------------------

.. _fg-server_ldap:

Section ``[LDAP]``
******************

This section is used to configure the access to LDAP to verify the user passwords.

*This section is required by all services*

Option ``LDAPHOST``
~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Hostname or IP address of the LDAP server that manages the user's authentication.

Option ``LDAPUSER``
~~~~~~~~~~~~~~~~~~~

**Type:** user-dn

**Required:** Yes

This is the DN of an user that have read access to the encrypted passwords of every user. This looks 
like ``uid=USER,ou=People,dc=futuregrid,dc=org`` 

Option ``LDAPPASS``
~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Password of the user specified in the previous section.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``test``
~~~~~~~~~~~~~~~

**Valid values:** ``True``, ``False``

**Required:** No

This option is for development purposes. For security reasons, the LDAP server cannot be contacted from outside of FutureGrid network.
Therefore, we need this option to go test our services before we deploy them on production.

****************

.. _fg-server_reposerver:

Section ``[RepoServer]``
************************

This section is used to configure the Image Repository Server. To complete the configuration of this service we need to configure also a 
:ref:``Repository Backend <repo_backend_example>`` section.

Option ``port``
~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Repository server will be listening.

Option ``proc_max``
~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Maximum number of request that can be processed at the same time.

Option ``refresh``
~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Interval to check the status of the running requests when ``proc_max`` is reached and determine if new request can be processed.

Option ``authorizedusers``
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String-list (comma separated)

**Required:** No

List of users (separated by commas) that can use the Image Repository in behalf of other users. This could be useful for other FutureGrid
services that need to call the repository in behalf of an user. This also prevents that other users can hack the client to use the 
repository as if they were other users.

Option ``nopasswdusers``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-list (semicolon separated) 

**Required:** No

Users listed here does need to introduce their password when using the Image Repository. Each user will be associated to one or several 
IP address. The format is ``userid:ip,ip1; userid1:ip2,ip3``.

Option ``backend``
~~~~~~~~~~~~~~~~~~

**Valid values:** ``mongodb``, ``mysql``, ``swiftmysql``, ``swiftmongo``, ``cumulusmysql``, ``cumulusmongo``

**Required:** Yes

Specify the desired storage backend (see :ref:`Image Repository Backend Table <imagerepo_config>` for more details). The value specified 
in this option will be the name of a section that has the configuration. See :ref:`Backend example <repo_backend_example>` below.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``, ``error``, ``warning``, ``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``ca_cert``
~~~~~~~~~~~~~~~~~~

**Type:** ca-cert

**Required:** Yes

Location of CA certificate (PEM-encoded) used to generate user and service certificates.

Option ``certfile``
~~~~~~~~~~~~~~~~~~~

**Type:** service-cert

**Required:** Yes

Location of the certificate (PEM-encoded) used by the Image Repository.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

Option ``restConfFile``
~~~~~~~~~~~~~~~~~~~~~~~

**Type:** file-path

**Required:** No

Location of the configuration file for the Image Repository Rest Interface.

****************

.. _repo_backend_example:

Section ``[cumulusmongo]``
**************************

This sections is an example of a backend configurations.

Option ``address``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the server where MongoDB or MySQL are listening. In the case of MongoDB we can use a list of ``address:ports`` separated by commas. 
In MySQL we only specify the ``address`` of the server.

Option ``userAdmin``
~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

User that is going to access MongoDB or MySQL to store/retrieve the data. Although the option is required, it can be with no value.

Option ``configFile``
~~~~~~~~~~~~~~~~~~~~~

**Type:** file-path

**Required:** Yes

Location of the file that contains the password of the user specified in ``userAdmin``. Although the option is required, it can 
be with no value.

Option ``addressS``
~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the server where the complementary service is listening. Currently, this complementary service can be Cumulus or Swift. 
In both cases we only specify the ``address`` of the server.

Option ``userAdminS``
~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

User that is going to access the complementary service (Cumulus or Swift) to store/retrieve the data. In the case of Swift, the user is
typically ``<user-name>``:``<group-name>``.

Option ``configFileS``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** file-path

**Required:** Yes

Location of the file that contains the password of the user specified in ``userAdminS``. 

Option ``imgStore``
~~~~~~~~~~~~~~~~~~~

**Type:** directory-path

**Required:** Yes

Location of the directory where images are uploaded to the server. This is a temporal directory in all cases but MySQL. When this is a temporal
directory the permission must be ``777`` without the **t bit**, because the user that is running the server must be able to remove the images 
once they are stored in the final destination. This bit is disable by default when you create a directory. However the ``/tmp/`` 
directory has this bit enabled.
 
****************

.. _fg-server_generateserver:

Section ``[GenerateServer]``
****************************

This section is used to configure the Image Generation Server.

Option ``port``
~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Generation server will be listening.

Option ``proc_max``
~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Maximum number of request that can be processed at the same time.

Option ``refresh``
~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Interval to check the status of the running requests when ``proc_max`` is reached and determine if new request can be processed.

Option ``wait_max``
~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Maximum time that the service will wait for an image to boot, that is, the time from ``penn`` status to the ``runn`` one. If the time
is exceeded, the VM is killed and the Image Generation request fails.

Option ``nopasswdusers``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-list (semicolon separated) 

**Required:** No

Users listed here does need to introduce their password when using the Image Generation. Each user will be associated to one or several 
IP address. The format is ``userid:ip,ip1; userid1:ip2,ip3``.

Option ``vmfile_<os-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the OpenNebula VM templates that boots the VMs where the image requested by the user will be generated. Currently,
four OSes are considered: ``centos``, ``rhel``, ``ubuntu`` and ``debian``. Therefore, we will have four options named 
``vmfile_centos``, ``vmfile_rhel``, ``vmfile_ubuntu``, ``vmfile_debian``. However, only ``centos`` and ``ubuntu`` are implemented. 
The other options have to be there but we do not need to specify any value until they are implemented. In the case of CentOS, the value is
a list of ``<version>:<template-file-location>`` separated by commas because CentOS 5 is not compatible with CentOS 6.

Option ``xmlrpcserver``
~~~~~~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

Address of the OpenNebula service. It should be something like ``http://localhost:2633/RPC2``

Option ``bridge``
~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Bridge where the VM network interface will be attached. This is used to identify the IP that OpenNebula has assigned to the VM.

Option ``addrnfs``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine that shares the directory ``tempdirserver``. This address must be in the same network that the VM address.

Option ``tempdirserver``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the directory shared with the VMs. This directory will be used as scratch partition for the Vms. In this way, the VM disks can
be small and we don't need to transfer the image back to the server. Users must be able to read the files in this directory to retrieve
their images when needed.

Option ``tempdir``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the ``tempdirserver`` directory inside the VM when it is mounted via NFS.

Option ``http_server``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

Address of the http server that keeps configuration files needed to generate the images. Thus, the VMs has to have access to this http 
server. 

Option ``oneuser``
~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

User that will manage the VMs for the Image Generation server. It could be ``oneadmin`` directly or a user created for this purpose.

Option ``onepass``
~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

Password of the user specified in ``oneuser``. You get that password by executing ``oneuser list`` as ``oneadmin`` user.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``, ``error``, ``warning``, ``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``ca_cert``
~~~~~~~~~~~~~~~~~~

**Type:** ca-cert

**Required:** Yes

Location of CA certificate (PEM-encoded) used to generate user and service certificates.

Option ``certfile``
~~~~~~~~~~~~~~~~~~~

**Type:** service-cert

**Required:** Yes

Location of the certificate (PEM-encoded) used by the Image Generation server.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

****************

.. _fg-server_registerserverxcat:

Section ``[RegisterServerXcat]``
********************************

This section is used to configure the Image Registration xCAT Server for HPC infrastructures.

Option ``xcat_port``
~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration xCAT server will be listening.

Option ``xcatNetbootImgPath``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the directory used by xCAT to store the netboot images. Typically, this is ``/install/netboot``

Option ``nopasswdusers``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-list (semicolon separated) 

**Required:** No

Users listed here does need to introduce their password when using the Image Registration xCAT. Each user will be associated to one or several 
IP address. The format is ``userid:ip,ip1; userid1:ip2,ip3``.

Option ``http_server``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

Address of the http server that keeps configuration files needed to adapt the images and get the kernel files.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``, ``error``, ``warning``, ``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``test_mode``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``True``,``False``

**Required:** No

This option is for testing the service in a machine without xCAT. The default value is False.

Option ``default_xcat_kernel_<os-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-List (comma separated)

**Required:** Yes

Default kernel name for each supported OS. The syntax is a list of ``<os_version>``:``<kernel_version>`` separated by commas. 
Currently, two OSes are considered: ``centos`` and ``ubuntu``. Therefore, we will have two options named 
``default_xcat_kernel_centos`` and ``default_xcat_kernel_ubuntu`` 

Option ``auth_kernels_<os-name>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-list (semicolon separated)

**Required:** Yes

Authorized kernels for each supported OS. The syntax is ``<os_version>:<kernel1>,<kernel2>; <os_version2>:<kernel3>,<kernel4>``.
Currently, two OSes are considered: ``centos`` and ``ubuntu``. Therefore, we will have two options named 
``auth_kernels_centos`` and ``auth_kernels_ubuntu``.

Option ``tempdir``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the scratch directory used to extract the image and read the manifest. Then, the image is moved to the real directory 
using the manifest information.

Option ``ca_cert``
~~~~~~~~~~~~~~~~~~

**Type:** ca-cert

**Required:** Yes

Location of CA certificate (PEM-encoded) used to generate user and service certificates.

Option ``certfile``
~~~~~~~~~~~~~~~~~~~

**Type:** service-cert

**Required:** Yes

Location of the certificate (PEM-encoded) used by the Image Registration server.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

Option ``max_diskusage``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Integer (percentage)

**Required:** Yes

Maximum usage of the partition where the ``xcatNetbootImgPath`` is located. This is specified in percentage. If the usage is higher than
this value, we do not allow to register more images.

****************

.. _fg-server_registerservermoab:

Section ``[RegisterServerMoab]``
********************************

This section is used to configure the Image Registration Moab Server for HPC infrastructures.

Option ``moab_port``
~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration Moab server will be listening.

Option ``moabInstallPath``
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location where Moab is installed. For example ``/opt/moab/``

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``, ``error``, ``warning``, ``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``ca_cert``
~~~~~~~~~~~~~~~~~~

**Type:** ca-cert

**Required:** Yes

Location of CA certificate (PEM-encoded) used to generate user and service certificates.

Option ``certfile``
~~~~~~~~~~~~~~~~~~~

**Type:** service-cert

**Required:** Yes

Location of the certificate (PEM-encoded) used by the Image Registration server.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

.. _fg-server_registerserveriaas:

****************

Section ``[RegisterServerIaas]``
********************************

This section is used to configure the Image Registration Server for Cloud infrastructures.

Option ``port``
~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration IaaS server will be listening.

Option ``proc_max``
~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Maximum number of request that can be processed at the same time.

Option ``refresh``
~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Interval to check the status of the running requests when ``proc_max`` is reached and determine if new request can be processed.


Option ``nopasswdusers``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Dictionary-list (semicolon separated) 

**Required:** No

Users listed here does need to introduce their password when using the Image Registration IaaS. Each user will be associated to one or several 
IP address. The format is ``userid:ip,ip1; userid1:ip2,ip3``.

Option ``tempdir``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the scratch directory where images are copied and modified. The permisson has to be ``777`` with the **t bit** disabled to 
allow the user that executes the server remove the original image. This bit is disable by default when you create a directory. 
However the ``/tmp/`` directory has this bit enabled.

Option ``default_<infrastructure-name>_kernel``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Default kernel that will be used when registering an image in such infrastructure. ``<infrastructure-name>`` can be ``eucalyptus``, 
``openstack``, ``nimbus`` and ``opennebula``. Therefore, we will have two options named 
``default_eucalyptus_kernel``, ``default_openstack_kernel``, ``default_nimbus_kernel`` and ``default_opennebula_kernel``. 

Option ``<infrastructure-name>_auth_kernels``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** List (semicolon separated)

**Required:** Yes

Authorized kernels for registering an image in such infrastructure. ``<infrastructure-name>`` can be ``eucalyptus``, 
``openstack``, ``nimbus`` and ``opennebula``. Therefore, we will have two options named 
``eucalyptus_auth_kernels``, ``openstack_auth_kernels``, ``nimbus_auth_kernels`` and ``opennebula_auth_kernels``.
The syntax is ``eucalyptus_auth_kernels = <kernel1>:eki:eri;<kernel2>:eki:eri``. Nimbus uses the name to identify the kernel, 
but we keep the syntax just in case they change in the future. OpenNebula does not have ids for now and we have to use the location of the
files.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``, ``error``, ``warning``, ``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``ca_cert``
~~~~~~~~~~~~~~~~~~

**Type:** ca-cert

**Required:** Yes

Location of CA certificate (PEM-encoded) used to generate user and service certificates.

Option ``certfile``
~~~~~~~~~~~~~~~~~~~

**Type:** service-cert

**Required:** Yes

Location of the certificate (PEM-encoded) used by the Image Registration server.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.




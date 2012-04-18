.. _sec_fg-client.conf:

``fg-client.conf`` configuration file
-------------------------------------

.. _fg-client_fgshell:

Section ``[fg-shell]``
**********************

This section is used to configure the FutureGrid Shell.

Option ``history``
~~~~~~~~~~~~~~~~~~

**Type:** history-file

**Required:** Yes

Location of the file where the executed commands are stored.

Option ``log``
~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the logs will be stored.

Option ``log_level``
~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``debug``,``error``,``warning``,``info``

**Required:** No

Desired log level. The default option is ``debug``.

Option ``script``
~~~~~~~~~~~~~~~~~

**Type:** file

**Required:** Yes

Location of the default file where the commands executed are recorded after we active the ``script`` command in the shell. More information 
about how to use the FutureGrid Shell can be found in 

.. warning:: link to the shell user manual 

************

.. _fg-client_ldap:

Section ``[LDAP]``
******************

*This section is required only by the FutureGrid Shell*

Option ``LDAPHOST``
~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Hostname or IP address of the LDAP server that manages the user's authentication.

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

*********

.. _fg-client_repo:

Section ``[Repo]``
******************

This section is used to configure the Image Repository client.

Option ``port``
~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Repository server will be listening.

Option ``serveraddr``
~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine where the Image Repository server is running.

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

Location of the certificate (PEM-encoded) used by the Image Repository client.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

************

.. _fg-client_generation:

Section ``[Generation]``
************************

This section is used to configure the Image Generation client.

Option ``port``
~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Repository server will be listening.

Option ``serveraddr``
~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine where the Image Generation server is running.

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

Location of the certificate (PEM-encoded) used by the Image Generation client.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

************

.. _fg-client_register:

Section ``[Register]``
**********************

This section is used to configure the Image Registration client. To complete the configuration of this service we need to configure also the 
:ref:``Machines <fg-client_machines>`` sections.

Option ``xcat_port``
~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration xCAT server will be listening.

Option ``moab_port``
~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration Moab server will be listening.

Option ``iaas_serveraddr``
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine where the Image Registration server for Cloud is running.

Option ``iaas_port``
~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Image Registration xCAT server will be listening.

Option ``tempdir``
~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** No

Location of the scratch directory to extract images when ``--justregister`` option is used. If this option is not provided
the current directory will be used.


Option ``http_server``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** URL

**Required:** Yes

Address of the http server that keeps configuration files.

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

Location of the certificate (PEM-encoded) used by the Image Repository client.

Option ``keyfile``
~~~~~~~~~~~~~~~~~~

**Type:** key-cert

**Required:** Yes

Location of the private key (PEM-encoded) of the certificate specified in ``certfile``.

************

.. _fg-client_machines:

Sections ``[minicluster]`` and ``[india]``
******************************************

Option ``loginmachine``
~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the login machine of the target cluster.

Option ``moabmachine``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine where machine where Moab is installed and therefore the ``IMRegisterServerMoab.py`` is running.

Option ``xcatmachine``
~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the machine where machine where the ``IMRegisterServerXcat.py`` is running.


************

.. _fg-client_rain:

Section ``[Rain]``
******************

Option ``moab_max_wait``
~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Maximum time that we wait for a image registered on Moab to became available.

Option ``moab_images_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Location of the file where Moab stores the list of images. If the image requested is not there, we do not wait.

Option ``loginnode``
~~~~~~~~~~~~~~~~~~~~

**Type:** IP address

**Required:** Yes

IP of the login node. This is used to mound the home directory of the user inside the VM via sshfs.

Option ``refresh``
~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Interval to check the job status.

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

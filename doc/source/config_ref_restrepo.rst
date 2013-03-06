.. _sec_fg-restrepo.conf:

Image Repository Rest Interface configuration file
--------------------------------------------------

.. _fg-restrepo_global:

Section ``[Global]``
********************

Option ``log.error_file``
~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the error logs will be stored.

Option ``log.accessfile``
~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the file where the access logs will be stored.

Option ``server.socket_host``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** String

**Required:** Yes

Address of the Rest Interface.

Option ``server.socket_port``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Port where the Rest Interface is listening.

Option ``server.thread_pool``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** Integer

**Required:** Yes

Number of concurrent threads.

Option ``server.ssl_module``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Valid values:** ``builtin``, ``pyopenssl``

**Required:** Yes

Determine the ssl module.


Option ``server.ssl_certificate``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** ssl-cert

**Required:** No

Location of the certificate used for https. If this option is not provided the protocol will be http.


Option ``server.ssl_private_key``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type:** log-file

**Required:** Yes

Location of the certificate key for the certificate specified in ``server.ssl_certificate``. If this option is not provided 
the protocol will be http.
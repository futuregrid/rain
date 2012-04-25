.. _support:

Support
=======

If you run into problems when using FutureGrid Rain and Image Management, please use our 
help form at `https://portal.futuregrid.org/help <https://portal.futuregrid.org/help>`_


Known problems
==============

Depending of the configuration of your machines, you may have problems installing some python modules. In particular, we have notice problems 
with the ldap modules, which is required for the installation of our software.

* Installing python-ldap

   :: 

      Ldap api
      sudo apt-get install python-ldap
      or
      sudo yum install python-ldap
      or
      sudo yum install python26-ldap  #(when the default python is the 2.4 version)    
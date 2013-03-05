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
      
* Load FutureGrid module on India.

  FutureGrid module loads the appropriated python module. Therefore, if you have previously loaded a python module, you need to unload it. Then
  load futuregrid module again.
  
  The error looks like:
  
  :: 

      $ module load futuregrid
      futuregrid version 1.1 loaded
      euca2ools version 2.0.2 loaded
      python_w-cmd2/2.7(21):ERROR:150: Module 'python_w-cmd2/2.7' conflicts with the currently loaded module(s) 'python/2.7'
      python_w-cmd2/2.7(21):ERROR:102: Tcl command execution failed: conflict python
      
      moab version 5.4.0 loaded
      torque/2.5.5 version 2.5.5 loaded
       
       
  The solution is:
  
  ::
  
      $ module unload python/2.7
      $ module load futuregrid

.. _modules_india:

Configuring a Module for FutureGrid Software
============================================

The software packages on the FutureGrid machines is manage using the `Environment Modules <http://modules.sourceforge.net/>`_. 
The Environment Modules package provides for the dynamic modification of a user's environment via modulefiles.

In this section, we explain how to create a module for our software.

#. Create a directory to place the software ``/N/soft/futuregrid-1.0/``.
#. Locate the directory where Modules is installed. In the case of India, this is installed in ``/opt/Modules/``. From now on
   we will refer to this location as ``$MODULES_PATH``.
#. Create a directory in ``$MODULES_PATH/default/modulefiles/tools/futuregrid``
#. In this directory we need to create a file with the version number. In this example the file is named 1.0. The content of this file
   is some information about the software location and the list of modules that need to be loaded as requirements. 
   
   ::
     
      #%Module1.0#########################################################

      set ver 1.0
      set path /N/soft/futuregrid-$ver
      
      proc ModulesHelp { } {
      puts stderr "This module adds the FutureGrid toolkit to your environment"
      }
      
      module-whatis "Configures your environment for the FutureGrid toolkit"
      
      prepend-path PATH $path
      prepend-path PATH $path/bin/
      
      if [ module-info mode load ] {
      puts stderr "futuregrid version $ver loaded"
      }
      
      if [ module-info mode switch2 ] {
      puts stderr "futuregrid version $ver loaded"
      }
      
      if [ module-info mode remove ] {
      puts stderr "futuregrid version $ver unloaded"
      }
      
      module load euca2ools
      module load python_w-cmd2
      module load moab
      module load torque

.. note::
   If the python is not the one installed in the system, the binaries may be inside your python directory.

#. In case the software binaries were copied into ``/usr/bin`` or ``/usr/local/bin``. We need to move them to the directory
   ``/N/soft/futuregrid-1.0/bin/``
   
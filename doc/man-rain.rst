.. _man-rain:

Rain (fg-rain)
==============

Rain is a service that a command to dynamically deploy a FutureGrid software environments and stacks.

fg-rain
-------

+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Option**                             | **Description**                                                                                                                                              |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-h/--help``                          | Shows help information and exit.                                                                                                                             |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-u/--user <userName>``               | FutureGrid HPC user name, that is, the one used to login into the FG resources.                                                                              |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-k/--kernel <version>``              | Specify the desired kernel (``fg-register`` can list the available kernels for each infrastructure).                                                         |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-i/--registeredimageid <imgId>``     | Select the image to use by specifying its Id in the target infrastructure. This assumes that the image is registered in the selected infrastructure.         |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-r/--imgid <imgId>``                 | Select the image to use by specifying its Id in the repository. The image will be automatically registered in the infrastructure before the job is executed. |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-x/--xcat <MachineName>``            | Use the HPC infrastructure named ``MachineName`` (minicluster, india ...).                                                                                   |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-e/--euca [Address:port]``           | Use the Eucalyptus Infrastructure, which is specified in the argument. The argument should not be needed.                                                    |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-s/--openstack [Address]``           | Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.                                                     |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-n/--nimbus [Address]``              | *(NOT yet supported)* Use the Nimbus Infrastructure, which is specified in the argument. The argument should not be needed.                                  |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-o/--opennebula [Address]``          | *(NOT yet supported)* Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.                               |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-v/--varfile <VARFILE>``             | Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                                          |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-m/--numberofmachines <#instances>`` | Number of machines needed.                                                                                                                                   |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-w/--walltime <hours>``              | How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.                                                                           |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-j/--jobscript <JOBSCRIPT>``         | Script to execute on the provisioned images. In the case of Cloud environments, the user home directory is mounted in ``/tmp/N/u/<username>``.               |
|                                        | The ``/N/u/<username>`` is only used for ssh between VM and store the ips of the parallel job in a file called ``/N/u/<username>/machines``                  |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-I/--interactive``                   | Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.                       |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--nopasswd``                         | If this option is used, the password is not requested. This is intended for systems daemons like Inca.                                                       |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+


Examples
--------

* Run a job in 4 nodes using an image stored in the Image Repository (This involves the registration of the image on xCAT/Moab)
  
   ::
   
      $ fg-rain -r 1231232141 -x india -m 4 -j myscript.sh -u jdiaz      

* Run a job in 2 nodes using an image already registered on xCAT/Moab
  
   ::
   
      $ fg-rain -i centosjavi434512 -x india -m 2 -j myscript.sh -u jdiaz      


* Interactive mode. Instantiate two VMs using an image already registered on OpenStack

   ::
   
      $ fg-rain -i ami-00000126 -s -v ~/novarc -m 2 -I -u jdiaz
      
      
* Run a job in a VM using an image already registered on Eucalyptus

   ::

      $ fg-rain -i ami-00000126 -e -v ~/eucarc -j myscript.sh -u jdiaz


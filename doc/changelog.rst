.. _changelogs:

Changelog and Release Notes
===========================

1.0.1
-----

Changes:

* Rain is able to create hadoop environments on demand. Users can utilize this tool to start a hadoop cluster in VMs or baremetal machines using an specific OS. 
  They can choose to run a job or to enter in interactive mode.
* Update documentation
* Small bug fixes

Known problems:

* Image Registration server can only be configured for a single Cloud infrastructure of each type. That means that you cannot use the same server to register images in 
  the Eucalyptus deployed on India and in the Eucalyptus deployed on Sierra. The problem is that the server will give you the wrong ``kernel`` and ``ramdisk`` ids to 
  register the image with. Nevertheless, it can be used with the ``-g`` option to get the image adapted to the infrastructure and then you register manually using the
  euca2ools. We plan to fix that by adding sections in the configuration file to specify kernel/ramdisk for each infrastructure. Then the user will have to specify the
  name of the FutureGrid site (India, Sierra,...)  
* Image Generation does not check the list of software packages specified. Therefore if the user misspells a package name, it will not be installed. 

1.0
---

Summary of the main functionality provided:

* Security
   * Authorization is performed using the futuregrid LDAP
* Image Generation
   * Generate CentOS and Ubuntu images
   * Install software available in the official repositories and in the FutureGrid performance repository
* Image Repository
   * Users can upload and retrieve images
   * Images can be shared or not
   * Images are described with metadata that is searchable
   * Manage users for authorization
* Image Registration
   * Adapt and register images on Eucalyptus, OpenStack, Nimbus and OpenNebula
   * Adapt and register images on HPC infrastructure based on Moab/xCAT
* Rain
   * Create customized environments by provisioning VMs/machines with the requested OS
   * In the case of HPC, this is a wrapper of the ``qsub`` command
   * In the case of cloud, it starts the VMs, designates one as the master, create a file with all the hosts involved and execute the job or ssh to the master. Therefore, 
     it could be used for HPC on Cloud.


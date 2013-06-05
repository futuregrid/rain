.. _changelogs:

Changelog and Release Notes
===========================

1.0.1
-----

Changes:

* Rain is able to create hadoop environments on demand. Users can utilize this tool to start a hadoop cluster in VMs or baremetal machines using a specific OS. 
  They can choose to run a job or to enter in interactive mode.
* Update documentation
* Small bug fixes

Known problems:

* The Image Registration server only allows configuring kernels and ramdisks for one cloud infrastructures of each type. That means that you cannot use 
  the same server to register images in the Eucalyptus infrastructure deployed on India and in the Eucalyptus infrastructure deployed on Sierra. The problem 
  is that the server will give you the wrong kernel and ramdisk ids to register the image with. Nevertheless, it can be used with the -g option to get the image 
  adapted to the infrastructure and then you register manually using the euca2ools. We plan to fix that by adding sections in the configuration file to specify 
  kernel/ramdisk for each infrastructure. Then the user will have to specify the name of the FutureGrid site (India, Sierra,...).  
* Image Generation does not check the list of software packages specified. Therefore if the user misspells a package name, it will not be installed. 

1.0
---

Summary of the main functionality provided for this version:

* Security
   * Authentication is performed using the FutureGrid LDAP server
* Image Generation
   * Generate CentOS and Ubuntu images
   * Install software available in the official repositories and in the FutureGrid performance repository
* Image Repository
   * Users can upload and retrieve images
   * Images access can be configured by the owner of the image
   * Images can be augmented with information about the software stack installed on them including versions, libraries,and available services
   * Images information is maintained in a catalog that can be searched by users and/or other FG services.
   * Includes a database to manage users for authorization, quota control and user's roles
* Image Registration
   * Adapt and register images on Eucalyptus, OpenStack, Nimbus and OpenNebula
   * Adapt and register images on HPC infrastructure based on Moab/xCAT
   * List of available kernels organized by infrastructure. New kernels can be added upon request
   * Users can select the kernel they want to have in their images    
* Rain
   * Create customized environments by provisioning VMs/machines with the requested OS and services
   * In the case of HPC, the basic functionality is a wrapper of the ``qsub`` command
   * In the case of cloud, the basic functionality starts the VMs, designates one as the master, create a file with all the hosts involved and execute the job or ssh to the master. Therefore, 
     it could be used for HPC on Cloud


.. FutureGrid documentation master file, created by
   sphinx-quickstart on Wed Jul 27 11:22:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to FutureGrid Rain!
===========================

FutureGrid Rain is a tool that will allow us to place customized environments like virtual clusters or IaaS frameworks onto resouces. 
The process of raining goes beyond the services offered by existing scheduling tools due to its higher-level toolset targeting 
virtualized and non-virtualized resources. Rain will be able to move resources from one infrastructure to another and compare the
execution of an experiment in the different supported infrastructures. 

In order to support Rain we need a flexible image management framework. Thus, Rain includes the FutureGrid Image Management framework which
defines the full life cycle of the images in FutureGrid. It involves the process of creating, customizing, 
storing, sharing and registering images for different FutureGrid environments. 

This framework allows users to generate personalized abstract images by simply specifying a list of requirements such as OS, architecture, 
software, and libraries. These images are generic enough that through manipulations they can be adapted for 
several IaaS or HPC infrastructures with little effort by the users. It will support the management of images for 
`Nimbus <http://www.nimbusproject.org>`_, `Eucalyptus <http://open.eucalyptus.com/>`_, `OpenStack <http://www.openstack.org>`_, 
`OpenNebula <http://www.opennebula.org>`_, and bare-metal HPC infrastructures.

.. ifconfig:: website == "yes"

   .. note::
          The documentation is also available as:
             
             * `Single HTML <singlehtml/index.html>`_
             * :docs-pdf:`PDF <pdf>`

.. toctree::
    :maxdepth: 2
    :hidden:
    
    whatis


User Documentation
==================

.. toctree::
    :maxdepth: 1
    
    whatis


Administrator Documentation
===========================

In this section you will find information on software deployment details.

.. toctree::
    :maxdepth: 2
    
    install
    configure_futuregrid    
    config_ref
    install_repobackend
    

Developer Documentation
=======================

In this section you will find information on lower level programming details. 

.. toctree::
    :maxdepth: 2
    
    dev_shell

Source Documentation
====================

.. toctree::
    :maxdepth: 1
 
    misc


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




Welcome to FutureGrid Rain!
===========================

FutureGrid Rain is a tool that will allow users to place customized environments like virtual clusters or IaaS frameworks onto resources. 
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


.. _chap_pub:

Publications related with Rain
==============================

[1] J. Diaz, G.v. Laszewski, F. Wang, and G. Fox. `Abstract Image Management and Universal Image Registration for Cloud and HPC Infrastructures <_static/jdiaz-IEEECloud2012_id-4656.pdf>`_, IEEE Cloud 2012, Honolulu, Hawaii, June 2012.

[2] G.v. Laszewski, J. Diaz, F. Wang, and G. Fox. `Comparison of Multiple Cloud Frameworks <_static/laszewski-IEEECloud2012_id-4803.pdf>`_, IEEE Cloud 2012, Honolulu, Hawaii, June 2012.

[3] J. Diaz, G.v. Laszewski, F. Wang, A.J. Younge, and G. Fox. `FutureGrid Image Repository: A Generic Catalog and Storage System for Heterogeneous Virtual Machine Images <_static/jdiazCloudCom2011.pdf>`_, 3rd IEEE International Conference on Cloud Computing Technology and Science (CloudCom2011), Athens, Greece, November 2011.

[4] S. Blagodurov and A. Fedorova, `"Towards the contention aware scheduling in HPC cluster environment" <http://www.sfu.ca/~sba70/files/report188.pdf>`_, High Performance Computing Symposium (HPCS), Vancouver, Canada, May 2012. 



.. toctree::
    :maxdepth: 1
    :hidden:
    
    whatis
    quickstart
    documentation
    download
    support


.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`



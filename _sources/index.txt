.. raw:: html

 <a href="https://github.com/futuregrid/rain"
     class="visible-desktop"><img
    style="position: absolute; top: 40px; right: 0; border: 0;"
    src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png"
    alt="Fork me on GitHub"></a>


Welcome to FutureGrid Rain!
===========================

.. sidebar:: Table of Contents

  .. toctree::
        :maxdepth: 2

	whatis
	quickstart
	documentation
	download
	support
 
FutureGrid Rain is a tool that will allow users to place customized
environments like virtual clusters or IaaS frameworks onto resources.
The process of raining goes beyond the services offered by existing
scheduling tools due to its higher-level toolset targeting virtualized
and non-virtualized resources. Rain will be able to move resources
from one infrastructure to another and compare the execution of an
experiment in the different supported infrastructures.

In order to support Rain we need a flexible image management
framework. Thus, Rain includes the FutureGrid Image Management
framework which defines the full life cycle of the images in
FutureGrid. It involves the process of creating, customizing, storing,
sharing and registering images for different FutureGrid environments.

This framework allows users to generate personalized abstract images
by simply specifying a list of requirements such as OS, architecture,
software, and libraries. These images are generic enough that through
manipulations they can be adapted for several IaaS or HPC
infrastructures with little effort by the users. It will support the
management of images for `Nimbus <http://www.nimbusproject.org>`_,
`Eucalyptus <http://open.eucalyptus.com/>`_, `OpenStack <http://www.openstack.org>`_, `OpenNebula <http://www.opennebula.org>`_, and bare-metal HPC infrastructures.


.. _chap_pub:

Publications & Citation Recommendation
----------------------------------------

If you use RAIN please use the citations,  [R1]_ and [R3]_ . If you have
extra space add also in the following order: [R2]_ [R5]_ [R4]_ .

The very first paper about the idea of RAIN was published in 2010 and
contained an overview of the image repository

.. [R1] `Design of the FutureGrid Experiment Management Framework <https://portal.futuregrid.org/design-futuregrid-experiment-management-framework>`_  Gregor von Laszewski, Geoffrey C. Fox, Fugang Wang, Andrew J. Younge, Archit Kulshrestha, Gregory G. Pike, Warren Smith, Jens Voeckler, Renato J. Figueiredo, Jose Fortes et al. doi> `10.1109/GCE.2010.5676126 <http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5676126>`_

However since than we have mades some significant contributions
documented in the following papers

.. [R2] `Design of a Dynamic Provisioning System for a Federated Cloud and Bare-metal Environment <http://cyberaide.googlecode.com/svn/trunk/papers/pdf/vonLaszewski-federated-cloud-07-14-2012.pdf>`_, Gregor von Laszewski, Hyungro Lee, Javier Diaz, Fugang Wang, Koji Tanaka, Shubhada Karavinkoppa, Geoffrey C. Fox, and Tom Furlani, Proceeding FederatedClouds '12 Proceedings of the 2012 workshop on Cloud services, federation, and the 8th open cirrus summit.  doi> `10.1145/2378975.2378982 <http://dl.acm.org/citation.cfm?id=2378975.2378982>`_

.. [R3] `Abstract Image Management and Universal Image Registration for Cloud and HPC Infrastructures <_static/jdiaz-IEEECloud2012_id-4656.pdf>`_,  J. Diaz, Gregor von Laszewski, F. Wang, and G. Fox.  IEEE Cloud 2012, Honolulu, Hawaii, June 2012. doi> `10.1109/CLOUD.2012.94 <http://dl.acm.org/citation.cfm?id=2353730.2353869>`_

.. [R4] `Comparison of Multiple Cloud Frameworks <_static/laszewski-IEEECloud2012_id-4803.pdf>`_, Gregor von Laszewski,  J. Diaz, F. Wang, and G. Fox.  IEEE Cloud 2012, Honolulu, Hawaii, June 2012. doi> `10.1109/CLOUD.2012.104 <http://dx.doi.org/10.1109/CLOUD.2012.104>`_

.. [R5] `FutureGrid Image Repository: A Generic Catalog and Storage  System for Heterogeneous Virtual Machine Images <_static/jdiazCloudCom2011.pdf>`_,  J. Diaz, Gregor von Laszewski, F. Wang, A.J. Younge, and G. Fox, 3rd IEEE International Conference on Cloud Computing Technology and Science (CloudCom2011), Athens, Greece, November 2011. doi> `10.1109/CloudCom.2011.85 <http://dx.doi.org/10.1109/CloudCom.2011.85>`_



External Publications 
----------------------------------------
Poblication by others using RAIN that have been communicated to us [R6]_ 


.. [R6] `Towards the contention aware scheduling in HPC cluster environment <http://www.sfu.ca/~sba70/files/report188.pdf>`_,  S. Blagodurov and A. Fedorova , High Performance
Computing Symposium (HPCS), Vancouver, Canada, May 2012.


.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`



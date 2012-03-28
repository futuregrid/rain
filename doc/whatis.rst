.. _chap_whatis:


What is FutureGrid Rain
=======================

.. _sec_imagerepo:

**Image Repository**

The FutureGrid image repository provides a service to query, store, and update images through a unique and common interface. 
This implementation targets a variety of different user communities including end users, developers, administrators via web 
interfaces, APIs, and command line tools. The motivation for the command line interface is based on that fact that it is easy 
to use for the non-expert users. However, it also provides significant usability for administrators developing advanced 
FutureGrid scripts. In addition, the functionality of the repository is exposed through a REST interface, which enables 
the integration with Web-based services such as the FutureGrid portal.

The implementation is based on a client-server architecture, where in the client side we have the interface to interact 
with the image repository and in the server side we have the core functionality and the storage plugins. 
The backend is configured in the server side to keep users away from these kinds of details.

.. image:: image_repository.png
   :align: center
   
Currently, our repository includes several plugins to support up to four different storage systems including (a) MySQL where 
the image files are stored directly in the POSIX file system, (b) MongoDB where both data and files are stored in the NoSQL 
database (c) the OpenStack Object Store (Swift) and (d) Cumulus from the Nimbus project. For (c) and (d) the data can be stored 
in either MySQL or in MongoDB. These storage plugins not only increase the interoperability of the image repository, but they 
can also be used by the community as templates to create their own plugins to support other storage systems.

NOT FINISHED

**Image Management**


It is obvious that such a capability is advantageous to support repeatable performance experiments across a variety of
infrastructures. 

**Rain**


Due to the variety of services and limited resources provided in FG, it is necessary to enable a mechanism to provision 
needed services onto resources. This includes also the assignment of resources to different IaaS or PaaS frameworks. 

Rain makes it possible to compare the benefits of IaaS, PaaS performance issues, as well as evaluating which applications 
can benefit from such environments and how they must be efficiently configured. As part of this process, we allow the 
generation of abstract images and universal image registration with the various infrastructures including Nimbus, Eucalyptus, 
OpenNebula, OpenStack, but also bare-metal via the HPC services. 
 
It is one of the unique features about FutureGrid to provide an essential component to make comparisons between the different 
infrastructures more easily possible. Our toolkit rain is tasked with simplifying the full life cycle of the image management 
process in FG. 

Now that we have an elementary design of managing images, we can dynamically provision them to create bare-metal and virtualized 
environments while raining them onto our resources. Hence, rain will offers four main features:

* Create customized environments on demand.

* Compare different infrastructures.

* Move resources from one infrastructure to another by changing the image they are running plus doing needed changes in the framework.

* Ease the system administrator burden for creating deployable images.

This basic functionality has been tested as part of a scalability experiment motivated by our use case introduced in the introduction. 
Here, a user likes to start many virtual machines and compare the performance of this task between the different frameworks.
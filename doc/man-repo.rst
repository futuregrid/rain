.. _man-repo:

Image Repository (fg-repo)
==========================

The Image Repository is a service to query, store, and update images through a unique and common interface.

fg-repo
-------

+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| **Option**                                        | **Description**                                                                                                                           |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-h/--help``                                     | Shows help information and exit.                                                                                                          |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-u/--user <userName>``                          | FutureGrid HPC user name, that is, the one used to login into the FG resources.                                                           |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-q/--list [queryString]``                       | Get list of images that meet the criteria.                                                                                                |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-g/--get <imgId>``                              | Get an image by specifying its unique identifier.                                                                                         |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-p/--put <imgFile> [attributeString]``          | Store image into the repository and its metadata defined in ``attributeString``. Default metadata is provided if the argument is missing. |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-m/--modify <imgId> <attributeString>``         | Modify the metadata associated with the image.                                                                                            |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-r/--remove <imgId> [imgId ...]``               | Delete images from the Repository.                                                                                                        |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``-s/--setpermission <imgId> <permissionString>`` | Change the permission of a particular image. Valid values are ``public``, ``private``.                                                    |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``--histimg [imgId]``                             | Get usage information an image. If no argument provided, it shows the usage information of all images.                                    |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| ``--nopasswd``                                    | If this option is used, the password is not requested. This is intended for systems daemons like Inca.                                    |
+---------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+


The following options are available only for users with ``admin`` role.

+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Option**                            | **Description**                                                                                                                                                        |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--useradd <userId>``                | Add a new user to the image management database.                                                                                                                       |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--userdel <userId>``                | Delete an user from the image management database.                                                                                                                     |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--userlist``                        | List of users.                                                                                                                                                         |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--setuserquota <userId> <quota>``   | Modify the quota of a user. The quota is given in bytes, but math expressions are allowed (``4*1024*1024``). By default each user has 4GB of disk space.               |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--setuserrole  <userId> <role>``    | Modify the role of a user. Valid values: ``admin`` and ``user`` roles.                                                                                                 |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--setuserstatus <userId> <status>`` | Modify the status of a user. Valid values: ``pending``, ``active``, and ``inactive``.                                                                                  |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``--histuser [userId]``               | Get usage info of an User. If no argument provided, it shows the usage information of all users. This option can be used by normal users to show their own information |
+---------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+



.. note::

   While using the command line interface, the ``attributeString``, ``queryString`` and ``quotaExpression`` arguments must be enclosed by **"** characters. 


   * A ``attributeString`` can be composed by a list of metadata fields separated by the & character. Valid metadata fields are: 
   
     * ``vmtype``: it can be ``none``, ``xen``, ``kvm``, ``virtualbox``, ``vmware``.
     * ``imgtype``: it can be ``machine``, ``kernel``, ``eucalyptus``, ``nimbus``, ``opennebula``, ``openstack``.
     * ``os``: String.
     * ``arch``: String.
     * ``description``: String.
     * ``tag``: List of Strings.
     * ``permission``: it can be ``public``, ``private``.
     * ``imgStatus``: it can be ``available``, ``locked``.
   
   * Valid ``queryString`` are: 
     
     * "*"
     * "* where field=XX"
     * "field1,field2 where field3=XX"
   
   * Valid ``quotaExpression`` (in bytes): "4294967296", "2048 * 1024"



Examples
--------

* Upload an image
  
   ::
   
      $ fg-repo -p /home/javi/image.iso "vmtype=kvm&os=Centos5&arch=i386&description=this is a test description&tag=tsttag1, tsttag2&permission=private" -u jdiaz
      $ fg-repo -p /home/javi/image.iso "ImgType=Openstack&os=Ubuntu&arch=x86_64&description=this is a test description" -u jdiaz
      
.. note::
   The & character is used to separate different metadata fields.

* Get an image
  
   ::

      $ fg-repo -g 964160263274803087640112 -u jdiaz   


* Modify the metadata of an image
  
   ::

      $ fg-repo -m 964160263274803087640112 "ImgType=Opennebula&os=Ubuntu10" -u jdiaz   


* Query Image Repository

   ::
   
      $ fg-repo -q "* where vmType=kvm" -u jdiaz
        


* Add user to the Image Repository

   ::
   
      $ fg-repo --useradd juan -u jdiaz
      $ fg-repo --usersetstatus juan active

      
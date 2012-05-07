.. _man-register:

Image Registration (fg-register)
================================

This service registers images in the selected infrastructures. After this process, images become available for instantiation in such infrastructures.


fg-register
-----------

::

   usage: fg-register [-h] -u user [-d] (-i ImgFile | -r ImgId | --list | --listkernels | --listsites)
                      [-k Kernel version] [-a ramdiskId]
                      (-x MachineName | -e [Address:port] | -o [Address] | -n [Address] | -s [Address])
                      [-v VARFILE] [--getimg] [--noldap] [--wait] [--nopasswd] [--justregister]
                      
   Options between brackets are not required. Parenthesis means that you need to specify one of the options.

+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| **Option**                    | **Description**                                                                                                                        |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-h/--help``                 | Shows help information and exit.                                                                                                       |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-u/--user <userName>``      | FutureGrid HPC user name, that is, the one used to login into the FG resources.                                                        |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-i/--image <imgFile>``      | Select the image to register by specifying its location. The image is a tgz file that contains the manifest and image files.           |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-r/--imgid <imgId>``        | Select the image to register by specifying its Id in the repository.                                                                   |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-k/--kernel <version>``     | Specify the desired kernel.                                                                                                            |
|                               | **Case a)** if the image has to be adapted (any image generated with ``fg-generate``) this option can be used to select one of the     |
|                               | available kernels. Both kernelId and ramdiskId will be selected according to the selected kernel. This case is for any infrastructure. |
|                               | **Case b)** if the image is ready to be registered, you may need to specify the id of the kernel in the infrastructure.                |
|                               | This case is when ``-j/--justregister`` is used and only for cloud infrastructures.                                                    |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-a/--ramdisk <ramdiskId>``  | Specify the desired ramdisk that will be associated to your image in the cloud infrastructure. This option is only needed              |
|                               | if ``-j/--justregister`` is used.                                                                                                      |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-l/--list``                 | List images registered in the HPC or Cloud infrastructures.                                                                            |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-t/--listkernels``          | List kernels available for HPC or Cloud infrastructures.                                                                               |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``--listsites``               | List supported sites with their respective HPC and Cloud services.                                                                     |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``--removeimg``               | Remove an image from the specified infrastructure.                                                                                     |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-x/--xcat <MachineName>``   | Register the image into the HPC infrastructure named ``MachineName`` (minicluster, india ...).                                         |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-e/--euca [Address:port]``  | Register the image into the Eucalyptus Infrastructure, which is specified in the argument. The argument should not be needed.          |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-s/--openstack [Address]``  | Register the image into the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.           |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-n/--nimbus [Address]``     | Register the image into the Nimbus Infrastructure, which is specified in the argument. The argument should not be needed.              |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-o/--opennebula [Address]`` | Register the image into the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.           |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-v/--varfile <VARFILE>``    | Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                    |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-g/--getimg``               | Customize the image for a particular cloud framework but does not register it. So the user gets the image file.                        |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-p/--noldap``               | If this option is active, FutureGrid LDAP will not be configured in the image. This option only works for Cloud registrations.         |
|                               | LDAP configuration is needed to run jobs using ``fg-rain``                                                                             |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-w/--wait``                 | Wait until the image is available in the targeted infrastructure. Currently this is used by Eucalyptus and OpenStack.                  |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``--nopasswd``                | If this option is used, the password is not requested. This is intended for systems daemons like Inca.                                 |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| ``-j, --justregister``        | It assumes that the image is ready to run in the selected infrastructure. Thus, no additional configuration will be performed.         |
|                               | Only valid for Cloud infrastructures. (This is basically a wrapper of the tools that register images into the cloud infrastructures)   |
+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------+

              
      


.. note::

   * To register an image in the HPC infrastructure, users need to specify the name of that HPC machine that they want to use with 
     the -x/--xcat option. The rest of the needed information will be taken from the configuration file.
   
   * To register an image in Eucalyptus, OpenStack and Nimbus infrastructures, you need to provide a file with the environment variables 
     using the -v/--varfile option.

Examples
--------


* Register an image for the HPC Infrastructure India

   ::
   
      $ fg-register -r 964160263274803087640112 -x india -u jdiaz      
  

* Register an image for OpenStack

   ::
   
      $ fg-register -r 964160263274803087640112 -s -v ~/novarc -u jdiaz      


* Customize an image for Ecualyptus but do not register it (here ``-v ~/eucarc`` is not needed because we are not going to register the image
  in the infrastructure)

   ::
   
      $ fg-register -r 964160263274803087640112 -e -g -u jdiaz      
  

* Register an image for Nimbus

   ::
   
      $ fg-register -r 964160263274803087640112 -n -v ~/hotel.conf -u jdiaz      

* List available kernels for the HPC infrastructure India

   ::

      fg-register --listkernels -x india -u jdiaz

* List available kernels for OpenStack

   ::

      fg-register --listkernels -s -u jdiaz      
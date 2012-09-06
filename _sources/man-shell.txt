.. _man-shell:

FutureGrid Shell (fg-shell)
===========================

The FutureGrid shell simplifies the access to the different FutureGrid software components. This shell is a common entry point for every components that offer a 
customized environment where only the FutureGrid commands are available. It has features similar to the regular GNU/Linux shell like command auto-completion. 


fg-shell
--------

::

   usage: fg-shell [-h] -u user [-q] [-i] [-f script_file] [--nopasswd]
   
   Options between brackets are not required. Parenthesis means that you need to specify one of the options.

+-----------------------------+--------------------------------------------------------------------------------------------------------+
| **Option**                  | **Description**                                                                                        |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``-h/--help``               | Shows help information and exit.                                                                       |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``-u/--user <userName>``    | FutureGrid HPC user name, that is, the one used to login into the FG resources.                        |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``-q/--quiet``              | Prevent to load banner and welcome messages                                                            |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``-i/--interactive``        | After the commands are interpreted the shell is put into interactive mode                              |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``-f/--file <script_file>`` | Execute commands from a file.                                                                          |
+-----------------------------+--------------------------------------------------------------------------------------------------------+
| ``--nopasswd``              | If this option is used, the password is not requested. This is intended for systems daemons like Inca. |
+-----------------------------+--------------------------------------------------------------------------------------------------------+


Usage
-----

* The shell is executed by typing:

   ::

      fg-shell -u <username>

  After executing the previous command and typing your password, the prompt should change to ``fg>``.

.. note::

      **Using shell from outside FutureGrid:** If the shell is installed outside of FutureGrid, users will not be able to enter in the shell using their passwords. The security reasons, the LDAP server
      cannot be contacted from outside of FutureGrid. Therefore, users will have to use the option ``--nopasswd`` and set their password inside the shell by 
      executing the command ``setpasswd``. In this way, users can authenticate against the different FutureGrid components without typing the password everytime.

This is useful when a user install the shell in his local machine because he will not be able to enter in the shell typing his password.

.. note::

      **Context concept:** It is essential to understand how to use the shell the concept **CONTEXT**. A context is an environment specialized for a particular tool or service. 
      This allows us to use only the components we are interested on and organize the commands by component. For example, if we want to use the image repository, 
      we initialize its context by typing ``use repo`` and only the image repository commands will be available. See ``contexts`` and ``use`` commands.
      

* Autocompletion by pressing tab key.
* System commands can be executed directly from the shell. If the command typed does not exists inside the shell, it tries to execute it as system command.
  Moreover, the shell will execute as system commands any command preceded by the **!** character.

Next, we explain the available commands that you can find inside the FutureGrid Shell.

Generic Commands
----------------

Commands listed in this section are available in any context.

* Help Related Commands

   +--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Command**        | **Description**                                                                                                                                                         |
   +--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``help [command]`` | Show help message for a command or List of all available commands organized by context if we are in the generic context ``fg>`` (see ``use`` and ``context`` commands). |
   |                    | However, if we are in a specific context (e.g. ``fg-repo>``) it only show the generic commands and the specific commands of this particular context.                    |
   +--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``manual``         | List help message for all commands in the shell.                                                                                                                        |
   +--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``shortcuts``      | List all available shortcuts.                                                                                                                                           |
   +--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


* CONTEXT Related Commands

   +-------------------+--------------------------------------------------------------------------------------------------------------------------+
   | **Command**       | **Description**                                                                                                          |
   +-------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``contexts``      | List of available contexts.                                                                                              |
   +-------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``use [context]`` | Change the Shell CONTEXT to use a specified FG component. If no argument is provided, it returns to the default context. |
   +-------------------+--------------------------------------------------------------------------------------------------------------------------+


* History Related Commands

   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
   | **Command**                               | **Description**                                                                                                          |
   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``history``, ``hist`` and ``hi``          | Show historic of executed commands.                                                                                      |
   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``historysession``, ``hists`` and ``his`` | Show historic of the commands executed in the current session.                                                           |
   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``l``, ``li``                             | List last executed command.                                                                                              |
   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
   | ``save [N]``                              | Save session history to a file. N => number of command (from ``historysession``), or \*.  Most recent command if omitted.|
   +-------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

    
* Execution Related Commands    

   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Command**                                 | **Description**                                                                                                                                         |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``load <filename>`` and ``exec <filename>`` | Load commands from an script and stay in the shell                                                                                                      |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``pause [text]``                            | Displays the specified text then waits for the user to press RETURN.                                                                                    |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``py [command]``                            | py  <command>: Executes a Python command.                                                                                                               |
   |                                             | py: Enters interactive Python mode. End with ``Ctrl-D`` (Unix) / ``Ctrl-Z`` (Windows), ``quit()``, ``exit()``.                                          |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``run, r``                                  | Re-run the last executed command                                                                                                                        |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``script [filename]``                       | When Script is active, all commands executed are stored in a file. Activate it by executing: ``script [file]``. If no argument                          |
   |                                             | is provided, the file will be called ``script`` and will be located in your current directory. To finish and store the commands execute: ``script end`` |
   +---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+


* User-Settable Parameters Related Commands

   +-----------------------------+------------------------------------------------------------------------------------------------------+
   | **Command**                 | **Description**                                                                                      |
   +-----------------------------+------------------------------------------------------------------------------------------------------+
   | ``setpassword``             | Set the password for the current session without leaving the shell. The password is stored encrypted |
   +-----------------------------+------------------------------------------------------------------------------------------------------+
   | ``set [parameter] [value]`` | Sets a cmd2 parameter. Call without arguments for a list of settable parameters with their values.   |
   +-----------------------------+------------------------------------------------------------------------------------------------------+
   | ``show``                    | List of settable parameters with their values.                                                       |
   +-----------------------------+------------------------------------------------------------------------------------------------------+



Image Repository
----------------

These commands are available when Image Repository (``repo``) or Image Management (``image``) contexts are active. To activate the image repository context 
execute ``use repo``. If we execute ``help``, we will see which commands are generic and which ones are specific of this context.

* Image Related Commands

   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | **Command**                                  | **Description**                                                                                                                           |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``list [queryString]``                       | Get list of images that meet the criteria.                                                                                                |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``get <imgId>``                              | Get an image by specifying its unique identifier.                                                                                         |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``put <imgFile> [attributeString]``          | Store image into the repository and its metadata defined in ``attributeString``. Default metadata is provided if the argument is missing. |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``modify <imgId> <attributeString>``         | Modify the metadata associated with the image.                                                                                            |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``remove <imgId>``                           | Delete images from the Repository.                                                                                                        |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``setpermission <imgId> <permissionString>`` | Change the permission of a particular image. Valid values are ``public``, ``private``.                                                    |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
   | ``histimg [imgId]``                          | Get usage information an image. If no argument provided, it shows the usage information of all images.                                    |
   +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+


* User Related Commands

  The following options are available only for users with ``admin`` role.

   +-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Command**           | **Description**                                                                                                                                                        |
   +-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``user <options>``    | Manage image management user's database.                                                                                                                               |
   |                       |                                                                                                                                                                        |
   |                       | **options**                                                                                                                                                            |
   |                       |                                                                                                                                                                        |
   |                       | ``-a/--add <userId>``  Add a new user to the image management database.                                                                                                |
   |                       |                                                                                                                                                                        |
   |                       | ``-d/--del <userId>``  Delete an user from the image management database.                                                                                              |
   |                       |                                                                                                                                                                        |
   |                       | ``-l, --list``   List of users.                                                                                                                                        |
   |                       |                                                                                                                                                                        |
   |                       | ``-m/--modify <userId> <quota/role/status> <value>`` Modify quota, role or status of an user.                                                                          |
   +-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | ``histuser [userId]`` | Get usage info of an User. If no argument provided, it shows the usage information of all users. This option can be used by normal users to show their own information |
   +-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Image Generation
----------------

These commands are available when the Image Management (``image``) or the Rain (``rain``) contexts are active. To activate the image management context execute 
``use image``. If we execute ``help``, we will see which commands are generic and which ones are specific of this context.

+------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Command**            | **Description**                                                                                                                                                                                   |
+------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``generate <options>`` | Generates images with the requested OS and software stacks specification.                                                                                                                         |
|                        |                                                                                                                                                                                                   |
|                        | **options**                                                                                                                                                                                       |
|                        |                                                                                                                                                                                                   |
|                        | ``-o/--os <osName>``                Specify the desired Operating System for the new image. Currently, CentOS and Ubuntu are supported                                                            |
|                        |                                                                                                                                                                                                   |
|                        | ``-v/--version <osVersion>``        Operating System version. In the case of Centos, it can be 5 or 6. In the case of Ubuntu, it can be karmic(9.10), lucid(10.04), maverick(10.10), natty(11.04) |
|                        |                                                                                                                                                                                                   |
|                        | ``-a/--arch <arch>``                Destination hardware architecture (x86_64 or i386)                                                                                                            |
|                        |                                                                                                                                                                                                   |
|                        | ``--baseimage``                     Generate a Base Image that will be used to generate other images. In this way, the image generation process will be faster.                                   |
|                        |                                                                                                                                                                                                   |
|                        | ``-s/--software <software>``        List of software packages, separated by commas, that will be installed in the image.                                                                          |
|                        |                                                                                                                                                                                                   |
|                        | ``--scratch``                       Generate the image from scratch without using any Base Image from the repository.                                                                             |
|                        |                                                                                                                                                                                                   |
|                        | ``-n/--name <givenname>``           Desired recognizable name of the image.                                                                                                                       |
|                        |                                                                                                                                                                                                   |
|                        | ``-e/--description <description>``  Short description of the image and its purpose.                                                                                                               |
|                        |                                                                                                                                                                                                   |
|                        | ``-g/--getimg``                     Retrieve the image instead of uploading to the image repository.                                                                                              |
|                        |                                                                                                                                                                                                   |
|                        | ``-z/--size <SIZE>``                Specify the size of the Image in GigaBytes. The size must be large enough to install all the software required.                                               |
|                        | The default and minimum size is 1.5GB, which is enough for most cases.                                                                                                                            |
+------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Image Register
--------------

These commands are available when the Image Management (``image``) or the Rain (``rain``) contexts are active. To activate the image management context execute 
``use image``. If we execute ``help``, we will see which commands are generic and which ones are specific of this context.

+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Command**                    | **Description**                                                                                                                                               |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``register <options>``         | Registers images in the selected infrastructures. After this process, images become available for instantiation in such infrastructures.                      |
|                                |                                                                                                                                                               |
|                                | **Options**                                                                                                                                                   |
|                                |                                                                                                                                                               |
|                                | ``-k/--kernel <version>``      Specify the desired kernel.                                                                                                    |
|                                |                                                                                                                                                               |
|                                | ``-i/--image <imgFile>``       Select the image to register by specifying its location. The image is a tgz file that contains the manifest and image files.   |
|                                |                                                                                                                                                               |
|                                | ``-r/--imgid <imgId>``         Select the image to register by specifying its Id in the repository.                                                           |
|                                |                                                                                                                                                               |
|                                | ``-x/--xcat <SiteName>``    Select the HPC infrastructure named ``SiteName`` (minicluster, india ...).                                                        |
|                                |                                                                                                                                                               |
|                                | ``-e/--euca <SiteName>``   Select the Eucalyptus Infrastructure located in ``SiteName`` (india, sierra...).                                                   |
|                                |                                                                                                                                                               |
|                                | ``-s/--openstack <SiteName>``   Select the OpenStack Infrastructure located in ``SiteName`` (india, sierra...).                                               |
|                                |                                                                                                                                                               |
|                                | ``-n/--nimbus <SiteName>``      Select the Nimbus Infrastructure located in ``SiteName`` (india, sierra...).                                                  |
|                                |                                                                                                                                                               |
|                                | ``-o/--opennebula <SiteName>``  Select the OpenNebula Infrastructure located in ``SiteName`` (india, sierra...).                                              |
|                                |                                                                                                                                                               |
|                                | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                            |
|                                |                                                                                                                                                               |
|                                | ``-g/--getimg``                Customize the image for a particular cloud framework but does not register it. So the user gets the image file.                |
|                                |                                                                                                                                                               |
|                                | ``-p/--noldap``                If this option is active, FutureGrid LDAP will not be configured in the image. This option only works for Cloud registrations. |
|                                | LDAP configuration is needed to run jobs using ``fg-rain``                                                                                                    |
|                                |                                                                                                                                                               |
|                                | ``-w/--wait``                  Wait until the image is available in the targeted infrastructure. Currently this is used by Eucalyptus and OpenStack.          |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``cloudlist <options>``        | List images registered in the Cloud infrastructures.                                                                                                          |
|                                |                                                                                                                                                               |
|                                | **Options**                                                                                                                                                   |
|                                |                                                                                                                                                               |
|                                | ``-e/--euca <SiteName>`` Select the Eucalyptus Infrastructure located in ``SiteName`` (india, sierra...).                                                     |
|                                |                                                                                                                                                               |
|                                | ``-n / --nimbus <SiteName>`` Select the Nimbus Infrastructure located in ``SiteName`` (india, sierra...).                                                     |
|                                |                                                                                                                                                               |
|                                | ``-o / --opennebula <SiteName>`` Select the OpenNebula Infrastructure located in ``SiteName`` (india, sierra...).                                             |
|                                |                                                                                                                                                               |
|                                | ``-s / --openstack <SiteName>`` Select the OpenStack Infrastructure located in ``SiteName`` (india, sierra...).                                               |
|                                |                                                                                                                                                               |
|                                | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                            |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``cloudlistkernels <options>`` | List kernels available for the Cloud infrastructures.                                                                                                         |
|                                |                                                                                                                                                               |
|                                | **Options**                                                                                                                                                   |
|                                |                                                                                                                                                               |
|                                | ``-e/--euca <SiteName>`` Select the Eucalyptus Infrastructure located in ``SiteName`` (india, sierra...).                                                     |
|                                |                                                                                                                                                               |
|                                | ``-n / --nimbus <SiteName>`` Select the Nimbus Infrastructure located in ``SiteName`` (india, sierra...).                                                     |
|                                |                                                                                                                                                               |
|                                | ``-o / --opennebula <SiteName>`` Select the OpenNebula Infrastructure located in ``SiteName`` (india, sierra...).                                             |
|                                |                                                                                                                                                               |
|                                | ``-s / --openstack <SiteName>`` Select the OpenStack Infrastructure located in ``SiteName`` (india, sierra...).                                               |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``hpclist <SiteName>``         | List images registered in the HPC infrastructure named ``SiteName`` (minicluster, india ...).                                                                 |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``hpclistkernels <SiteName>``  | List kernels available for HPC infrastructure named ``SiteName`` (minicluster, india ...).                                                                    |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``listsites``                  | List supported sites with their respective HPC and Cloud services.                                                                                            |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``deregister <options>``       | Deregister an image from the specified infrastructure.                                                                                                        |
|                                |                                                                                                                                                               |
|                                | **Options**                                                                                                                                                   |
|                                |                                                                                                                                                               |
|                                | ``--deregister <imageId>``                                                                                                                                    |
|                                |                                                                                                                                                               |
|                                | ``-x/--xcat <SiteName>``    Select the HPC infrastructure named ``SiteName`` (minicluster, india ...).                                                        |
|                                |                                                                                                                                                               |
|                                | ``-e/--euca <SiteName>``  Select the Eucalyptus Infrastructure located in ``SiteName`` (india, sierra...).                                                    |
|                                |                                                                                                                                                               |
|                                | ``-n / --nimbus <SiteName>``  Select the Nimbus Infrastructure located in ``SiteName`` (india, sierra...).                                                    |
|                                |                                                                                                                                                               |
|                                | ``-o / --opennebula <SiteName>`` Select the OpenNebula Infrastructure located in ``SiteName`` (india, sierra...).                                             |
|                                |                                                                                                                                                               |
|                                | ``-s / --openstack <SiteName>``  Select the OpenStack Infrastructure located in ``SiteName`` (india, sierra...).                                              |
|                                |                                                                                                                                                               |
|                                | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                            |
+--------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+


Rain
----

These commands are available when the Rain (``rain``) contexts is active. To activate the rain context execute 
``use rain``. If we execute ``help``, we will see which commands are generic and which ones are specific of this context.

+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| **Command**                           | **Description**                                                                                                                                                                             | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``launch <options>``                  | Provision machines or VMs with the requested OS and execute a job or enter in interactive mode                                                                                              | |
|                                       |                                                                                                                                                                                             | |
|                                       | **Options**                                                                                                                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-k/--kernel <version>``      Specify the desired kernel.                                                                                                                                  | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-i/--image <imgFile>``       Select the image to register by specifying its location. The image is a tgz file that contains the manifest and image files.                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-r/--imgid <imgId>``         Select the image to register by specifying its Id in the repository.                                                                                         | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-x/--xcat <SiteName>``    Select the HPC infrastructure named ``SiteName`` (minicluster, india ...).                                                                                      | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-e/--euca <SiteName>``   Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).                                                                                     | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-s/--openstack <SiteName>``   Select the OpenStack Infrastructure located in SiteName (india, sierra...).                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-n/--nimbus <SiteName>``      Select the Nimbus Infrastructure located in SiteName (india, sierra...).                                                                                    | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-o/--opennebula <SiteName>``  Select the OpenNebula Infrastructure located in SiteName (india, sierra...).                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                                          | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-m/--numberofmachines <#instances>`` Number of machines needed.                                                                                                                           | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``--volume <size>`` This creates and attaches a volume of the specified size (in GiB) to each instance. The volume will be mounted in /mnt/. This is supported by Eucalyptus and OpenStack. | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-t/--instance-type <instancetype>``   VM Image type to run the instance as. Valid values: ['m1.small', 'm1.large', 'm1.xlarge']                                                           | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-w/--walltime <hours>``      How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.                                                                           | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-j/--jobscript <JOBSCRIPT>`` Script to execute on the provisioned images. In the case of Cloud environments, the user home directory is mounted in ``/tmp/N/u/<username>``.               | |
|                                       | The ``/N/u/<username>`` is only used for ssh between VM and store the ips of the parallel job in a file called ``/N/u/<username>/machines``                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-I/--interactive``           Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.                       | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-b, --background``      Background mode. It boots VMs or provisions bare-metal machines. Then, it gives you the information you need to know to log in anytime.                           | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-w/--wait``                  Wait until the image is available in the targeted infrastructure. Currently this is used by Eucalyptus and OpenStack.                                        | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``launchhadoop <options>``            | Provision machines or VMs with the requested OS, install/configure Hadoop and execute a job or enter in interactive mode.                                                                   | |
|                                       |                                                                                                                                                                                             | |
|                                       | **Options**                                                                                                                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | Same options that ``launch``.                                                                                                                                                               | |
|                                       |                                                                                                                                                                                             | |
|                                       | **Additional Hadoop Option**                                                                                                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``--inputdir <inputdir>``      Location of the directory containing the job input data that has to be copied to HDFS. The HDFS directory will have the same name.                           | |
|                                       | Thus, if this option is used, the job script has to specify the name of the directory (not to all the path).                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``--outputdir <outputdir>``    Location of the directory to store the job output data from HDFS. The HDFS directory will have the same name.                                                | |
|                                       | Thus, if this option is used, the job script has to specify the name of the directory (not to all the path).                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-hdfsdir <hdfsdir>``         Location of the HDFS directory to use in the machines. If not provided /tmp/ will be used.                                                                   | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``cloudinstanceslist <options>``      | List the information of the instance/s submitted to the selected cloud.                                                                                                                     | |
|                                       |                                                                                                                                                                                             | |
|                                       | **Options**                                                                                                                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-i/--instance [InstanceId/s]``    Id of the instance to check status. This is optional, if not provided all instances will be listed.                                                     | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-e/--euca <SiteName>``   Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).                                                                                     | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-s/--openstack <SiteName>``   Select the OpenStack Infrastructure located in SiteName (india, sierra...).                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-n/--nimbus <SiteName>``      Select the Nimbus Infrastructure located in SiteName (india, sierra...).                                                                                    | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-o/--opennebula <SiteName>``  Select the OpenNebula Infrastructure located in SiteName (india, sierra...).                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                                          | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``hpcjobslist [job/s]``               | List the information of the HPC job/s.                                                                                                                                                      | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``cloudinstancesterminate <options>`` | Terminate instance/s from the selected cloud. You can specify a list of instances ids and also reservations ids.                                                                            | |
|                                       |                                                                                                                                                                                             | |
|                                       | **Options**                                                                                                                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-i/--instance <InstanceId/s>``    Id/s of the instance/s or reservation/s to terminate.                                                                                                   | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-e/--euca <SiteName>``   Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).                                                                                     | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-s/--openstack <SiteName>``   Select the OpenStack Infrastructure located in SiteName (india, sierra...).                                                                                 | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-n/--nimbus <SiteName>``      Select the Nimbus Infrastructure located in SiteName (india, sierra...).                                                                                    | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-o/--opennebula <SiteName>``  Select the OpenNebula Infrastructure located in SiteName (india, sierra...).                                                                                | |
|                                       |                                                                                                                                                                                             | |
|                                       | ``-v/--varfile <VARFILE>``     Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                                          | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``hpcjobsterminate <job/s>``          | Terminate HPC job/s.                                                                                                                                                                        | |
+---------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+


  
 

Examples
--------


**Context Usage**

* Show list of available contexts

  ::

   $ fg-shell -u jdiaz      
   fg> contexts


  * The output shows all available contexts

    ::

      FG Contexts:
      ------------
      repo
      image
      rain
      hadoop

* Users can select any of the previous contexts with the ``use`` command. Then, the environment of this particular context is initialized.

  ::

   fg> use repo
   fg-repo>

* Return to the normal context

  ::  

   fg-repo> use
   fg>
 

**Help Usage**

* List available commands in the generic context

  ::

   $ fg-shell -u jdiaz
   fg> help

  * The output shows the list of generic commands and the list of commands that are available in each of the contexts. Note that the commands listed for each context 
    are only available when that particular context has been loaded. Some contexts load other contexts as part of their requirements, as we explained before. 
  
    ::
    
      A complete manual can be found in https://portal.futuregrid.org/man/fg-shell
      
      Generic Documented commands (type help <topic>):
      ================================================
      contexts  history         load    py    save    setpasswd  use
      exec      historysession  manual  quit  script  shortcuts
      help      li              pause   run   set     show     
      
      Image Repository commands. Execute "use repo" to use them. (type help <topic>):
      ===============================================================================
      get  histimg  histuser  list  modify  put  remove  setpermission  user
      
      Image Management commands. Execute "use image" to use them. (type help <topic>):
      ================================================================================
      cloudlist  cloudlistkernels  generate  hpclist  hpclistkernels  register
      
      FG Dynamic Provisioning commands. Execute "use rain" to use them. (type help <topic>):
      ======================================================================================
      launch  launchhadoop
      
      Please select a CONTEXT by executing use <context_name>
      Execute 'contexts' command to see the available context names 


* List available commands in the ``image`` context (this contexts also loads the ``repo`` contexts)

  ::

   fg> use image
   fg-image> help
      
  * The output is something like this.

    ::

      A complete manual can be found in https://portal.futuregrid.org/man/fg-shell
      
      General documented commands (type help <topic>):
      ================================================
      contexts  history         load    py    save    setpasswd  use
      exec      historysession  manual  quit  script  shortcuts
      help      li              pause   run   set     show     
      
      Specific documented commands in the repo context (type help <topic>):
      =====================================================================
      get  histimg  histuser  list  modify  put  remove  setpermission  user
      
      Specific documented commands in the image context (type help <topic>):
      ======================================================================
      cloudlist  cloudlistkernels  generate  hpclist  hpclistkernels  register

**General Shell Usage**

* Session example where we get an image, list all the images which ``os`` is centos, add an user and activate it.

  ::

   $ fg-shell
   
   fg> use repo
   fg-repo> get image123123123
   fg-repo> list * where os=centos
   fg-repo> user -a javi
   fg-repo> user -m javi status active

* Record the executed commands in an script.  

  ::
  
   $fg-shell
   fg> script myscript.txt
   fg> use repo
   fg-repo> put /tmp/image.img vmtype=xen & imgtype=opennebula & os=linux & arch=x86_64
   fg-repo> list
   fg-repo> script end

  * This will create a file called myscript.txt with this content:
   
   ::  
   
      use repo
      put /tmp/image.img vmtype=xen & imgtype=opennebula & os=linux & arch=x86_64
      list

* Execute shell commands stored in a file. Then exits from the shell

  ::
  
   $ cat myscript.txt| fg-shell

* Execute shell commands stored in a file from the shell. This stay in the shell.

  :: 
  
   $ fg-shell -u jdiaz
   fg> load myscript.txt
   
   
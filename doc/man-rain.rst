.. _man-rain:

Rain (fg-rain)
==============

Rain is a service that a command to dynamically deploy a FutureGrid software environments and stacks.

fg-rain
-------

::

   usage: fg-rain [-h] -u user [-d] [-k Kernel version]
                  (-i ImgId | -r ImgId) (-x MachineName | -e [Address:port] | -s [Address]) 
                  [-v VARFILE] [-m #instances] [-w hours]
                  (-j JOBSCRIPT | -I) [--nopasswd] 
                  [--hadoop] [--inputdir INPUTDIR] [--outputdir OUTPUTDIR] [--hdfsdir HDFSDIR]

   Options between brackets are not required. Parenthesis means that you need to specify one of the options.

+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| **Option**                             | **Description**                                                                                                                                                          | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-h/--help``                          | Shows help information and exit.                                                                                                                                         | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-u/--user <userName>``               | FutureGrid HPC user name, that is, the one used to login into the FG resources.                                                                                          | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-k/--kernel <version>``              | Specify the desired kernel (``fg-register`` can list the available kernels for each infrastructure).                                                                     | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-i/--registeredimageid <imgId>``     | Select the image to use by specifying its Id in the target infrastructure. This assumes that the image is registered in the selected infrastructure.                     | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-r/--imgid <imgId>``                 | Select the image to use by specifying its Id in the repository. The image will be automatically registered in the infrastructure before the job is executed.             | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-x/--xcat <MachineName>``            | Use the HPC infrastructure named ``MachineName`` (minicluster, india ...).                                                                                               | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-e/--euca [Address:port]``           | Use the Eucalyptus Infrastructure, which is specified in the argument. The argument should not be needed.                                                                | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-s/--openstack [Address]``           | Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.                                                                 | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-n/--nimbus [Address]``              | *(NOT yet supported)* Use the Nimbus Infrastructure, which is specified in the argument. The argument should not be needed.                                              | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-o/--opennebula [Address]``          | *(NOT yet supported)* Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.                                           | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-v/--varfile <VARFILE>``             | Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.                                                                      | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-m/--numberofmachines <#instances>`` | Number of machines needed.                                                                                                                                               | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--volume <size>``                    | This creates and attaches a volume of the specified size (in GiB) to each instance. The volume will be mounted in /mnt/. This is supported by Eucalyptus and OpenStack.  | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-t/--instance-type <instancetype>``  | VM Image type to run the instance as. Valid values: ['m1.small', 'm1.large', 'm1.xlarge']                                                                                | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-w/--walltime <hours>``              | How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.                                                                                       | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-j/--jobscript <JOBSCRIPT>``         | Script to execute on the provisioned images. In the case of Cloud environments, the user home directory is mounted in ``/tmp/N/u/<username>``.                           | |
|                                        | The ``/N/u/<username>`` is only used for ssh between VM and store the ips of the parallel job in a file called ``/N/u/<username>/machines``                              | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``-I/--interactive``                   | Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.                                   | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--nopasswd``                         | If this option is used, the password is not requested. This is intended for systems daemons like Inca.                                                                   | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| **Hadoop Option**                      | **Additional options to run hadoop jobs or go interactive into a hadoop cluster**                                                                                        | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--hadoop``                           | Specify that your want to execute a Hadoop job. Rain will setup a hadoop cluster in the selected infrastructure. It assumes that Java is installed in the image/machine. | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--inputdir <inputdir>``              | Location of the directory containing the job input data that has to be copied to HDFS. The HDFS directory will have the same name. Thus, if this option is used, the     | |
|                                        | job script has to specify the name of the directory (not to all the path).                                                                                               | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--outputdir <outputdir>``            | Location of the directory to store the job output data from HDFS. The HDFS directory will have the same name. Thus, if this option is used, the job script has to        | |
|                                        | specify the name of the directory (not to all the path).                                                                                                                 | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+
| ``--hdfsdir <hdfsdir>``                | Location of the HDFS directory to use in the machines. If not provided /tmp/ will be used.                                                                               | |
+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-+



Examples
--------

.. note:
   This examples only work with images generated and registered with our tools. The reason is because the image has to have LDAP client configured and sshfs installed.

* Run a job in four nodes using an image stored in the Image Repository (This involves the registration of the image on xCAT/Moab)
  
   ::
   
      $ fg-rain -r 1231232141 -x india -m 4 -j myscript.sh -u jdiaz      

* Run a job in four nodes using an image already registered on the HPC infrastructure (xCAT/Moab)
  
   ::
   
      $ fg-rain -i centosjavi434512 -x india -m 2 -j myscript.sh -u jdiaz      


* Interactive mode. Instantiate two VMs using an image already registered on OpenStack

   ::
   
      $ fg-rain -i ami-00000126 -s -v ~/novarc -m 2 -I -u jdiaz
      
      
* Run a job in a VM using an image already registered on Eucalyptus

   ::

      $ fg-rain -i ami-00000126 -e -v ~/eucarc -j myscript.sh -u jdiaz

* Run an MPI job in six VM using an image already registered on Eucalyptus (the image has to have the ``mpich2`` package installed)

   ::

      $ fg-rain -i ami-00000126 -e -v ~/eucarc -j mpichjob.sh -m 6 -u jdiaz

  Content of ``mpichjob.sh``:
  
   ::
  
      #!/bin/bash

      #real home is /tmp/jdiaz/
      #VM home is /N/u/jdiaz/
      #$HOME/machines is a file with the VMs involved in this job 
      
      cd /tmp/N/u/jdiaz/mpichexample/
            
      mpiexec.hydra -machinefile /N/u/jdiaz/machines -np `wc -l /N/u/jdiaz/machines |  cut -d" " -f1` /tmp/N/u/jdiaz/example/a.out > /tmp/N/u/jdiaz/output.mpichexample

Hadoop Examples
+++++++++++++++

* Run Hadoop job on three VMs using an image already registered on OpenStack  (the image has to have ``java`` package installed. Hadoop is automatically installed/configured by the tool.)

   ::
     
     $ fg-rain -i ami-000001bf -s -v ~/novarc -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir -u jdiaz
     
   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir
   

* Interactive mode. Setup a Hadoop cluster in three VMs using an image already registered on OpenStack  (the image has to have ``java`` package installed. Hadoop is automatically installed/configured by the tool.)

   ::
     
     $ fg-rain -i ami-000001bf -s -v ~/novarc -I -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir -u jdiaz
     
   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir


* Run Hadoop job three machines using an image already registered on the HPC infrastructure  (the image has to have ``java`` package installed. Hadoop is automatically installed/configured by the tool.)

   ::
     
     $ fg-rain -x india -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir --walltime 1 -u jdiaz 
     
   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir


 
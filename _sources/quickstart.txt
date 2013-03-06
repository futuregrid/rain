.. raw:: html

 <a href="https://github.com/futuregrid/rain"
     class="visible-desktop"><img
    style="position: absolute; top: 40px; right: 0; border: 0;"
    src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png"
    alt="Fork me on GitHub"></a>


.. _quickstart:

Rain QuickStart
===============

.. raw:: html

    <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
    <script src="http://code.jquery.com/ui/1.10.1/jquery-ui.js"></script>
    <script>
    $(function() {
      $( ".accordion" ).accordion({  active: false, collapsible: true} );

    });
    </script>


Requirements
------------

Our software provides a very convenient shell environment. In
addition, we also provide a less convenient command line
interface. Users need access to the machine where the client
is installed. Currently, it is installed on FutureGrid in the machine
called (``india.futuregrid.org``), a 128 node
cluster. Since our
software is going to interact with different cloud infrastructures,
users need to have the appropriated credentials for each of
them. Hence you need to have the following acomplished before you can
start:

* If users want to register and run images on Eucalyptus, they need an
  Eucalyptus account, download and uncompress the credentials (see `FG
  Eucalyptus Tutorial
  <https://portal.futuregrid.org/tutorials/eucalyptus>`_). The
  important file is the ``eucarc`` that contains the needed
  information about Eucalyptus and the user.

* If users want to register and run images on OpenStack, they need an
  OpenStack account (see `FG OpenStack Tutorial
  <https://portal.futuregrid.org/tutorials/openstack>`_). User
  credentials should be in his ``HOME`` directory of the India
  cluster. After uncompressing the credentials file, user will find
  the ``novarc`` file that contains important information about Nimbus
  and the user.

* If users want to register and run images on Nimbus, they need a
  Nimbus account (`FG Nimbus Tutorial
  <https://portal.futuregrid.org/tutorials/nimbus>`_). We are going to
  use the Nimbus infrastructure available in the Hotel cluster from
  India (The other Nimbus deployments should work if they have the
  kernels needed by the images).  User credentials should be in his
  ``HOME`` directory of the Hotel cluster
  (``hotel.futuregrid.org``). Users have to copy and uncompress their
  credentials in their ``HOME`` directory of India. Then, users have
  to create a directory called ``.nimbus`` in their ``HOME`` directory
  of India and copy the files ``usercert.pem`` and
  ``userkey.pem``. Other important file is the ``hotel.conf`` that
  contains information about Nimbus and the user user.
  
Once users have the appropriate accounts, they can login on India and
use the module functionality to load the environment variables::

      $ ssh <username>@india.futuregrid.org
      $ module load futuregrid

.. note::
   If you got an error such as::
   
      module load futuregrid
      futuregrid version 1.1 loaded
      euca2ools version 2.1.2 loaded
      python_w-cmd2/2.7(21):ERROR:150: Module 'python_w-cmd2/2.7' conflicts with the currently loaded module(s) 'python/2.7'
      python_w-cmd2/2.7(21):ERROR:102: Tcl command execution failed: conflict python
      moab version 5.4.0 loaded
      torque/2.5.5 version 2.5.5 loaded

   ..
   
   You have to unload the python module first due to a version conflict with::

       module unload python

.. note::
   At this point, users have to explicitly request access to the Image Management and rain tools by sending a ticket to `https://portal.futuregrid.org/help <https://portal.futuregrid.org/help>`_.

FG-Shell vs Command Line Interfaces
-----------------------------------

To ease the use of the FG tools, we have created a shell that provides
a common interface for all these tools. So, users just need to
remember how to execute the shell. Once users login into the shell, a
number of features will be exposed to them. These features include
help, command's auto-completion, and list of available commands
organized by tool. Moreover, users only need to type the password when
they login into the shell.

Users can log into the shell by executing::

      $ fg-shell -u <username>

.. note::
   Users need to use their FutureGrid portal password.

More information about using the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.

After you have sucessfully entered your password, you will be
authorized to use the convenient fg-shell commands. You will see an
image such as::

     Changing to rain context
     -------------------------
     Init Rain
     Init Repo
     Init Image
	 ______      __                  ______     _     __
	/ ____/_  __/ /___  __________  / ____/____(_)___/ /
       / /_  / / / / __/ / / / ___/ _ \/ / __/ ___/ / __  / 
      / __/ / /_/ / /_/ /_/ / /  /  __/ /_/ / /  / / /_/ /  
     /_/    \__,_/\__/\__,_/_/   \___/\____/_/  /_/\__,_/   

     Welcome to the FutureGrid Shell
     -------------------------------

     fg-rain>

..

By default we will start the rain module for you. This will load
several useful commands. To see the commands you can enter the word
``help`` in the shell::

    fg-rain>help

    A complete manual can be found in https://portal.futuregrid.org/man/fg-shell

    General documented commands (type help <topic>):
    ================================================
    contexts  history         load    py    save    setpasswd  use
    exec      historysession  manual  quit  script  shortcuts
    help      li              pause   run   set     show     

    Specific documented commands in the rain context (type help <topic>):
    ===============================================================================
    cloudinstanceslist       hpcjobslist       launch      
    cloudinstancesterminate  hpcjobsterminate  launchhadoop

    Specific documented commands in the repo context (type help <topic>):
    ===============================================================================
    get  repohistimg  histuser  list  modify  put  reporemove  setpermission  user

    Specific documented commands in the image context (type help <topic>):
    ================================================================================
    cloudlist         deregister  hpclist         listsites
    cloudlistkernels  generate    hpclistkernels  register 

    fg-rain>

..



Using Image Repository
----------------------

The Image Repository is a service to query, store, and update images
through a unique and common interface. Next, we show some examples of
the Image Repository usage (``fg-repo`` command). More details can be
found in the :ref:`Image Repository Manual <man-repo>`.

Additionally, the Image Repository manages the user database for all
the image management components. This database is used to authorize
users, to control the user's quotas and to record usage
information. Therefore, this database complements the LDAP server
which is mainly focused on the user authentication.

When using ``fg-shell``, users need to load the Image Repository
context by executing ``use repo`` inside the shell. The Image
Repository environment is also included in the Image Management
(``image``) and Rain (``rain``) contexts. Once there is an active
context, the ``help`` command will show only the available commands
for such context. Available contexts can be listed using the
``contexts`` command. More information about the shell can be found in
the :ref:`FutureGrid Shell Manual <man-shell>`.

Upload an image
^^^^^^^^^^^^^^^^^

Here we show how to upload an image with the shell::

      put  /home/javi/image.iso ImgType=Openstack&os=Ubuntu&arch=x86_64&description=this is a test description
      
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
    $ fg-repo -p /home/javi/image.iso "vmtype=kvm&os=Centos5&arch=i386&description=this is a test description&tag=tsttag1, tsttag2&permission=private" -u $USER
    $ fg-repo -p /home/javi/image.iso "ImgType=Openstack&os=Ubuntu&arch=x86_64&description=this is a test description" -u $USER
     </pre></div></div></div></div>

.. note::
   The & character is used to separate different metadata fields.


Get an image
^^^^^^^^^^^^^^

Here we show how to get and download an image with the shell::

      get 964160263274803087640112


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-repo -g 964160263274803087640112 -u $USER</pre>
     </div></div></div>  

Modify the metadata of an image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To modify the meta data of an image you can use the following shell command::

      modify 964160263274803087640112 ImgType=Opennebula&os=Ubuntu10

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
     $ fg-repo -m 964160263274803087640112 "ImgType=Opennebula&os=Ubuntu10" -u $USER</pre>
    </div></div></div>


Query Image Repository
^^^^^^^^^^^^^^^^^^^^^^

To list the images in the repository, please use the ``list``
command. You can also add simple search parameters to it::

      list * where vmType=kvm

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>  
      $ fg-repo -q "* where vmType=kvm" -u $USER
     </pre></div></div></div>
  


Add user to the Image Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Administrators have the ability to add new users to the repository::

      user -a juan
      user -m juan status active


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre> 
      $ fg-repo --useradd juan -u $USER
      $ fg-repo --usersetstatus juan active
     </pre></div></div></div>
  


Using Image Generation
----------------------

This component creates images, according to user requirements, that
can be registered in FutureGrid. Since FG is a testbed that supports
different type of infrastructures like HPC or IaaS frameworks, the
images created by this tool are not aimed at any specific
environment. Thus, it is at registration time when the images are
customized to be successfully integrated into the desired
infrastructure.

Next, we provide some examples of the Image Generation usage
(``fg-generate`` command). More details can be found in the
:ref:`Image Generation Manual <man-generate>`.


When using ``fg-shell``, users need to load the Image Management
context by executing ``use image`` inside the shell. The Image
Management environment is also included in the Rain (``rain``)
contexts. Once there is an active context, the ``help`` command will
show only the available commands for such context. Available contexts
can be listed using the ``contexts`` command. More information about
the shell can be found in the :ref:`FutureGrid Shell Manual
<man-shell>`.


Generate a CentOS image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An image can be gerenated quite simply. YOu can specifiey default
pacakges from our repository   ::

      generate -o centos -v 5 -a x86_64 -s wget,emacs,python26
 
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-generate -o centos -v 5 -a x86_64 -s wget,emacs,python26 -u $USER      
     </pre></div></div></div>
  


Generate an Ubuntu image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just as you can generate images for centos, you can also generate
images for ubuntu::

      generate -o ubuntu -v 10.10 -a x86_64 -s wget,emacs,python26


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-generate -o ubuntu -v 10.10 -a x86_64 -s wget,openmpi-bin -u $USER      
     </pre></div></div></div>
  


Using Image Registration
------------------------

This tool is responsible for customizing images for specific
infrastructures and registering them in such infrastructures.
Currently, we fully support HPC (bare-metal machines), Eucalyptus,
OpenStack, and Nimbus infrastructures. OpenNebula is also implemented
but we do not have this infrastructure in production yet.

Next, we provide some examples of the image registration usage
(``fg-register`` command). A detailed manual can be found in the
:ref:`Image Registration Manual <man-register>`


When using ``fg-shell``, users need to load the Image Management
context by executing ``use image`` inside the shell. The Image
Management environment also loads the Image Repository context. The
Image Management is also included in the Rain (``rain``)
contexts. Once there is an active context, the ``help`` command will
show only the available commands for such context. Available contexts
can be listed using the ``contexts`` command. More information about
the shell can be found in the :ref:`FutureGrid Shell Manual
<man-shell>`.

List Information of the available sites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is useful which sites are registered with RAIN. we provide a simple
command called listsites that you can invoke::

     listsites 

.. raw:: html
  
    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
     $fg-register --listsites -u $USER
     </pre></div></div></div>

   
The output would look something like this::
     
         Supported Sites Information
         ===========================
         
         Cloud Information
         -----------------
         SiteName: sierra
           Description: In this site we support Eucalyptus 3.
           Infrastructures supported: ['Eucalyptus']
         SiteName: hotel
           Description: In this site we support Nimbus 2.9.
           Infrastructures supported: ['Nimbus']
         SiteName: india
           Description: In this site we support Eucalyptus 2, OpenStack Folsom.
           Infrastructures supported: ['Eucalyptus', 'OpenStack']
         
         HPC Information (baremetal)
         ---------------------------
         SiteName: india
           RegisterXcat Service Status: Active
           RegisterMoab Service Status: Active


.. note::

   * To register an image in the HPC infrastructure, users need to
     specify the name of that HPC machine that they want to use with
     the -x/--xcat option. The rest of the needed information will be
     taken from the configuration file.
   
   * To register an image in Eucalyptus, OpenStack and Nimbus
     infrastructures, you need to provide a file with the environment
     variables using the -v/--varfile option.

Register an image for the HPC Infrastructure India
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To register an  image on a host simply add the abbreviation for the
host. Here ``india``::

      register -r 964160263274803087640112 -x india

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register -r 964160263274803087640112 -x india -u $USER      
     </pre></div></div></div>
  

Register an image for OpenStack 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you followed the FG Openstack tutorial, your novarc will probably
be in ``~/.futuregrid/openstack/novarc``. Use it for this tutorial

To register an image not just with the host, but a specific cloud
infrastructure you can use::

      register -r 964160263274803087640112 -s india -v ~/novarc
   
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register -r 964160263274803087640112 -s india -v ~/novarc -u $USER      
     </pre></div></div></div>
  
Customize images for Eucalyptus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Customize an image for Ecualyptus but do not register it (here ``-v
  ~/eucarc`` is not needed because we are not going to register the
  image in the infrastructure)::

      register -r 964160263274803087640112 -e india -g


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register -r 964160263274803087640112 -e india -g -u $USER      
     </pre></div></div></div>
  

Register an image for Nimbus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here is an example on how to register an image with hotel::

      register -r 964160263274803087640112 -n hotel -v ~/hotel.conf


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register -r 964160263274803087640112 -n hotel -v ~/hotel.conf -u $USER      
     </pre></div></div></div>
  

List available kernels for the HPC infrastructure India
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The available kernels for a host can be listed as follows::

      hpclistkernels india  


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register --listkernels -x india -u $USER
     </pre></div></div></div>


List available kernels for OpenStack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For openstack we sue the ``-s`` option::

      cloudlistkernels -s india

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register --listkernels -s india -u $USER  
     </pre></div></div></div>



Deregister an image from OpenStack 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(if you followed the FG Openstack
  tutorial, your novarc will probably be in ``~/openstack/novarc``)

To deregister, you can use::

      deregister --deregister ami-00000126 -s india -v ~/novarc
   
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register --deregister ami-00000126 -s india -v ~/novarc -u $USER
     </pre></div></div></div>

   


Deregister an image from HPC 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

User role must be ``admin``. To deregister an image from HPC you can use::

     deregister --deregister centosjdiaz1610805121 -x india 
   

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-register --deregister centosjdiaz1610805121 -x india -u $USER
     </pre></div></div></div>



Using RAIN
----------

This component allow users to dynamically register FutureGrid software
environments as requirement of a job submission.  This component will
make use of the previous registration tool. Currently we only support
HPC job submissions.

Next, we provide some examples of the Rain usage (``fg-rain``
command). A detailed manual can be found in the :ref:`Rain Manual <man-rain>`.

When using ``fg-shell``, users need to load the Image Management
context by executing ``use rain`` inside the shell. The Rain
environment also loads the Image Repository and Image Management
contexts. Once there is an active context, the ``help`` command will
show only the available commands for such context. Available contexts
can be listed using the ``contexts`` command. More information about
the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.


.. note::

   * To register an image in the HPC infrastructure, users need to
     specify the name of that HPC machine that they want to use with
     the -x/--xcat option. The rest of the needed information will be
     taken from the configuration file.
   
   * To register an image in Eucalyptus, OpenStack and Nimbus
     infrastructures, you need to provide a file with the environment
     variables using the -v/--varfile option.
 

Run a job in four nodes on India 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run a job in four nodes on India using an image stored in the Image
Repository (This involves the registration of the image in the HPC
infrastructure)::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -r 1231232141 -x india -m 4 -j myscript.sh

   
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-rain -r 1231232141 -x india -m 4 -j myscript.sh -u $USER      
     </pre></div></div></div>
  


Run a job in two nodes on India using an image already registered in the HPC Infrastructure India
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run a job in two nodes on India using an image already registered in the HPC Infrastructure India::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -i centosjavi434512 -x india -m 2 -j myscript.sh 

   
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-rain -i centosjavi434512 -x india -m 2 -j myscript.sh -u $USER      
     </pre></div></div></div>
  


Interactive mode. 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instantiate two VMs using an image already registered on OpenStack::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -i ami-00000126 -s india -v ~/novarc -m 2 -I


   
.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-rain -i ami-00000126 -s india -v ~/novarc -m 2 -I -u $USER      
     </pre></div></div></div>
  

Run an MPI job 
^^^^^^^^^^^^^^^^^^^^

Run an MPI job in six VM using an image already registered on Eucalyptus (the image has to have the ``mpich2`` package installed)

  .. note:: Please replace $USER with your own username

  Content of ``mpichjob.sh``:
  
   ::
  
      #!/bin/bash

      #real home is /tmp/$USER/
      #VM home is /N/u/$USER/
      #$HOME/machines is a file with the VMs involved in this job 
      
      cd /tmp/N/u/$USER/mpichexample/
            
      mpiexec.hydra -machinefile /N/u/$USER/machines -np `wc -l /N/u/$USER/machines |  cut -d" " -f1` /tmp/N/u/$USER/example/a.out > /tmp/N/u/$USER/output.mpichexample

Once you have that file, you can run it as follows::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -i ami-00000126 -e india -v ~/eucarc -j mpichjob.sh -m 6


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
      $ fg-rain -i ami-00000126 -e india -v ~/eucarc -j mpichjob.sh -m 6 -u $USER
     </pre></div></div></div>


Hadoop Examples
+++++++++++++++

* Run Hadoop job on three VMs using an image already registered on
  OpenStack (the image has to have ``java`` package installed. Hadoop
  is automatically installed/configured by the tool.)
     
   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir
       
Once you have that file you can run it as follows::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launchadoop -i ami-000001bf -s india -v ~/novarc -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir

.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
     $ fg-rain -i ami-000001bf -s india -v ~/novarc -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir -u $USER
     </pre></div></div></div>


Interactive mode 
^^^^^^^^^^^^^^

Setup a Hadoop cluster in three VMs using an image already registered on OpenStack  (the image has to have ``java`` package installed. Hadoop is automatically installed/configured by the tool.)

     
   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir

Now you can run it interactively as follows::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launchadoop -i ami-000001bf -s india -v ~/novarc -I -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
     $ fg-rain -i ami-000001bf -s india -v ~/novarc -I -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir -u $USER
     </pre></div></div></div>


Run Hadoop on HPC
^^^^^^^^^^^^^^^^

Run Hadoop job on three machines using an image already registered on the HPC infrastructure  (the image has to have ``java`` package installed. Hadoop is automatically installed/configured by the tool.)

   For this example, the ``inputdir1`` directory contains ebooks from the Project Gutenberg downloaded in ``Plain Text UTF-8`` encoding:  
      * `The Outline of Science, Vol. 1 (of 4) by J. Arthur Thomson <http://www.gutenberg.org/etext/20417>`_
      * `The Notebooks of Leonardo Da Vinci <http://www.gutenberg.org/etext/5000>`_
      * `Ulysses by James Joyce <http://www.gutenberg.org/etext/4300>`_
 
   Content of ``hadoopword.sh``:
   
     ::
     
       hadoop jar $HADOOP_CONF_DIR/../hadoop-examples*.jar wordcount  inputdir1 outputdir

To run it on HPC you can do this::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launchadoop -x india -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir --walltime 1


.. raw:: html

    <div class="accordion"><h5 align="right" > ... press to see the commandline version</h5><div><div class="highlight-python"><pre>
     $ fg-rain -x india -j ~/hadoopword.sh -m 3 --inputdir ~/inputdir1/ --outputdir ~/outputdir --walltime 1 -u $USER
     </pre></div></div></div>


 
      

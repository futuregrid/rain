.. _chap_dev_shell:

FG-Shell Development
********************

In this section we explain how to develop a new module for the FutureGrid Shell. More information about the FutureGrid Shell 
can be found in 

.. warning:: link to the Shell user manual 

Requirement
===========

* Download the FutureGrid code:

  ::

   git clone git@github.com:futuregrid/rain.git

* Create a branch

  ::

   git checkout -b <branch_name>

* Install in developer mode:

  ::

   sudo python setup.py develop

* Copy configuration files from etc directory to /etc/futuregrid or to ~/.fg/  and set them up (:ref:admin)

Add Your Component Functionality as a New Module
================================================

Next, we explain the steps needed to include a new module in the FutureGrid shell. As an example, we use the 
repository module, called "repo"

#. Create a file to develop your functionality. This file will be called fgShellRepo.py and will be located in 
   src/futuregrid/shell/ (change Repo with your module name). The file includes a class with the same name that inherits 
   from cmd2. See the fgShellRepo.py file for more details.

#. Add your methods that has to be like "do_<module><method>" i.e. do_repoget. In this way, in the shell we will have a 
   command called repoget. You can also include a method called help_repoget that show information when execute "help repoget" 
   in the shell. 

   .. note::
         These methods will not have functionality. They only are a new command line interface for your existing methods. 
         In the repository example, the functionality is in the class IRServiceProxy. 

#. Go to file fgCLI.py and make the fgShell class to inherit from your class. For that you have to do three steps

   * Import your class.
   
     ::
   
      from futuregrid.shell.fgShellRepo import fgShellRepo
         
   * Add it to the fgShell class.
       
     ::
          
      classfgShell(Cmd,
                   fgShellUtils,
                   fgShellRepo):
                      
   * We have the list of available commands in a set called self.env to determine the available contexts (each module 
     will have a context, see section Contexts). Here you have to add the name of your context as a string. This variable 
     is in the constructor of the class fgShell (__init__(...)) and looks like:
     
     ::
   
      self.env=["repo","rain",""]
   
   * In the constructor we also have to write some information about the module.
     
     ::
       
      self.text = {'repo': 'Image Repository,
                   'rain': 'FG Dynamic Provisioning'}
                
   * Next, we have to specify the modules that are required for the new. In this way, we only initialize the components 
     that the user needs. This is done in the do_use method (see next section Contexts) of the fgCLI.py file. Thus, we need 
     to add a condition and a list of requirements that the new module has. Note that the requirements strings MUST be as in 
     the name of the classes that usually have the first character in uppercase.
   
     ::
       
      if (arg=="repo"):
         requirements=["Repo"]
      elif (arg == "rain"):
         requirements=["Repo","Image","Rain"]
      
#. Attention to the arguments of your methods. No matter how many arguments you have, all them are sent in a unique string. 
   Then, in your method you have to get them by using the  “getArgs(in: string): list” method, that is in the fgShellUtils class.

#. In your class (fgShellRepo in this example) you will have an  __init__ method to initialize your module. However, it will 
   be called only if you change to your module's context, see next Section.

Contexts
========

We have created contexts make easier the use of the FutureGrid commands by removing the prefix of your module. For that we have 
the show and use command. The show command list the available contexts and the use command change to a particular context. In this 
way, we can change to the repo context by executing “use repo”. Note that the prompt change from “fg>” to “fg-repo>” Now, the get 
command point to the repoget command.

We have already done several steps focused to enable the context. Here, we explain some other optional steps, but highly 
recommendable. All this is done in the fgShellUtils.py file.

#. If your have a command that is already in this class, you do not need to add anything to it.

#. If your command is not in this class, you can add it by creating a method. For example, let assume that you have a hello method.

   
   ::
   
       def do_hello(self, args):
           """
           Generic get command that changes its behavior depending on the
           context specified with use command.
           """
           if(self._use != ""):
               found = False
               for i in self._requirements:
                   prefix=string.lower(i)
                   command = "self.do_" + prefix + "hello(\"" + args + "\")"            
                   try:
                       eval(command)
                       found = True
                       break
                   except AttributeError:
                       pass
               if not found:
                   print "There is no hello method in any of the active contexts (" + str(self.requirements) + " )"
                   self._log.error(str(sys.exc_info()))           
           else:
               self.generic_error()
   
       help_hello = generic_help

#. This code will call a different method depending of the context. If your context is "repo", you need to have a method called 
   do_repohello(args) in your fgShellRepo class.

Log File
========

We have created a log file system to be use in the Shell. To use it, you only need to import the fgLog.py file:

from futuregrid.utils import fgLog
Then you can write in the logs using any of this methods:


::

   fgLog.degug(“text”)
   fgLog.error(“text”)
   fgLog.warning(“text”)
   fgLog.info(“text”)

The log file will be store in log file specified in the "fg-shell" section of the fg-client.conf configuration file. This file 
is placed in /etc/futuregrid/ or in ~/.fg/


Commit the Changes
==================

After you have created your new module, you need to push your branch into github and request to merge it with the official dev branch. 


#. Upload new branch to github

   ::
   
      git push origin <branch_name>


#. Send us a message via github to merge the code

#!/usr/bin/env python
# -------------------------------------------------------------------------- #
# Copyright 2010-2011, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #

"""Vdkhadke : Changes made, Gregor and Viplav had found many redundancies in the code and
hence decided on implementing  common code for the changes to reduce the size of the source code the original methods are commented starting from do_get to do_hpcjobslist

    Changelog: addition of helper method call_command() which contains all the redundant code inside the methods. Original methods are commented and stored.
    
"""


"""
FutureGrid Command Line Interface

Some code has been taken from Cyberade CoG kit shell (http://cogkit.svn.sourceforge.net/viewvc/cogkit/trunk)
"""
__author__ = 'Javier Diaz'

import os
#import cmd
import readline
import atexit
import sys
import textwrap
from cmd2 import Cmd
import pkgutil
import string
import inspect

class fgShellUtils(Cmd):


    def __init__(self):
        '''initialize the fgshellutils'''
        self._script = False
        self._scriptList = []
        self._scriptFile = self._conf.getScriptFile()


    ############################################################

    def getArgs(self, args):
        '''Convert the string args to a list of arguments.'''
        aux = args.strip()
        argsList = []
        
        if(aux != ""):
            values = aux.split(" ")
            
            for i in values:
                istriped = i.strip()
                if (istriped != ""):
                    argsList.append(istriped)
        return argsList

    ############################################################
    #SCRIPT
    ############################################################

    def do_script(self, arg):
        '''executs the script'''
        args = self.getArgs(arg)
        if not self._script:
            self._scriptList = []
            if(len(args) == 0):  #default file NO force
                if not (os.path.isfile(self._scriptFile)):
                    print "Script module activated"
                    self._script = True
                else:
                    print "File " + self._scriptFile + " exists. Use argument force to overwrite it"
            elif(len(args) == 1):
                if(args[0] == "end"):
                    print "Script is not active."
                elif(args[0] == "force"):  ##default file force
                    print "Script module activated "
                    self._script = True
                else:    #custom file NO force
                    print "Script module activated"
                    self._scriptFile = os.path.expanduser(args[0])
                    if not (os.path.isfile(self._scriptFile)):
                        self._script = True
                    else:
                        print "File " + self._scriptFile + " exists. Use argument force to overwrite it"
            elif(len(args) == 2):  ##custom file and maybe force
                if (args[0] == "force"):
                    print "Script module activated"
                    self._scriptFile = os.path.expanduser(args[1])
                    self._script = True
                if (args[1] == "force"):
                    print "Script module activated"
                    self._scriptFile = os.path.expanduser(args[0])
                    self._script = True
            else:
                self.help_script()
        elif(len(args) == 1):
            if(args[0] == "end"):
                print "Ending Script module and storing..."
                self._script = False
                with open(self._scriptFile, "w") as f:
                    for line in self._scriptList:
                        f.write(line + "\n")
            else:
                print "Script is activated. To finish it use: script end"
        else:
            print "Script is activated. To finish it use: script end"

    def help_script(self):
        '''help message for the script'''
        message = " When Script is active, all commands executed are stored " + \
        "in a file. Activate it by executing: script [file]. If no argument is " + \
        "provided, the file will be called \'script\' and will be located in your " + \
        "current directory. To finish and store the commands use: script end"
        self.print_man("script [file]", message)

    ############################################################
    # manual
    ############################################################

    def print_man(self, name, msg):
        '''print the manual'''
        print "\n"
        print "----------------------------------------------------------------------"
        print "%s" % (name)
        print "----------------------------------------------------------------------"
        man_lines = textwrap.wrap(textwrap.dedent(msg), 64)
        for line in man_lines:
            print "    %s" % (line)
        print ""

    def do_manual (self, args):
        '''print all manual pages'''
        "Print all manual pages organized by contexts"
        print "######################################################################"
        print "Generic commands (available in any context)\n"
        print "######################################################################"
        for i in self._docHelp:

            try:
                func = getattr(self, 'help_' + i)
                func()
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + i).__doc__
                    if doc:
                        print "----------------------------------------------------------------------"
                        print "%s" % (i)
                        print "----------------------------------------------------------------------"
                        self.stdout.write("%s\n" % str(doc))
                        print ""
                except AttributeError:
                    pass
        
        for cntxt in self.env:            
            if (cntxt.strip() != ""):    
                bold = "\033[1m"
                reset = "\033[0;0m"            
                print "######################################################################"
                print "\nSpecific Commands for the context: " + bold + cntxt + reset
                print "######################################################################"

                self.getDocUndoc(cntxt)
                for i in self._specdocHelp:
                    if (i.strip().startswith(cntxt)):
                        i = i[len(cntxt):]
                    try:                        
                        func = getattr(self, 'help_' + cntxt + i)
                        func()
                    except AttributeError:                        
                        try:
                            doc = getattr(self, 'do_' + cntxt + i).__doc__
                            if doc:
                                print "----------------------------------------------------------------------"
                                print "%s" % (i)
                                print "----------------------------------------------------------------------"
                                self.stdout.write("%s\n" % str(doc))
                        except AttributeError:                            
                            pass
                        except:
                            print "General exception: "+str(sys.exc_info())                        
                    except SystemExit:
                        pass
                    except:
                        print "General exception: "+str(sys.exc_info())
                    

    """
    def do_manual (self, args):
        all_manpages = ['use',
               'show',
               'history',
               'historysession',
               'print_man',
               'help',
               'EOF',
               'hadooprunjob',
               'repotest',
               'repohistimg',
               'repohistuser',
               'repouseradd',
               'repouserdel',
               'repouserlist',
               'reposetuserquota',
               'reposetuserrole',
               'reposetuserstatus',
               'repolist',
               'repomodify',
               'reposetpermission',
               'repoget',
               'repoput',
               'reporemove',
               'script',
               'manual',
               'runjob',
               'get',
               'modify',
               'setpermission',
               'put',
               'remove',
               'list',
               'useradd',
               'userdel',
               'userlist',
               'setuserquota',
               'setuserrole',
               'setuserstatus',
               'histimg',
               'histuser',
               'exec']
        for manualpage in all_manpages:
            self.print_man(manualpage,manualpage)
#            eval("self.help_"+manualpage+"()")
        this_function_name = sys._getframe().f_code.co_name
        print this_function_name
    """
    def generic_error(self):
        '''print the generic error'''
        print "    Please select a CONTEXT by executing use <context_name>.\n" + \
                  "    Execute \'contexts\' command to see the available context names. \n" + \
                  "    Help information is also different depending on the context. \n" + \
                  "    Note that this command may not be available in all CONTEXTS."

    def generic_help(self):
        '''help message for the generic command'''
        msg = "Generic command that changes its behaviour depending on the CONTEXT. "
        for line in textwrap.wrap(msg, 64):
            print "    %s" % (line)
        print ""
        self.generic_error()


        
    """
    This was for the old hadoop that now is integrated in Rain    
    #################################
    #Run JOB
    #################################
    def do_runjob(self, args):
        '''run the job'''
        if(self._use != ""):            
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "runjob(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no runjob method in any of the active contexts (" + str(self.self._requirementss) + " )"
                self._log.error(str(sys.exc_info()))            
        else:
            self.generic_error()

    help_runjob = generic_help

    #################################
    #Run JOB
    #################################    
    def do_runscript(self, args):
        '''run the script'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "runscript(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no runscript method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))           
        else:
            self.generic_error()

    help_runjob = generic_help
    """    
    #Helper method to eliminate the redundancies in code
    
    def call_command(self, args):
        '''Shortens all the redundant methods having duplicate code'''
        func_name = inspect.stack()[1][3]
        sh_func_name = func_name[3:] #trim the 'do_' part from the function_name
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + sh_func_name + "(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no " + sh_func_name + " method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()

    
    def do_get(self, args):
        '''TODO: get'''
        self.call_command(args)
    help_get = generic_help
    
    #################################
    #MODIFY
    #################################

    
    def do_modify(self, args):
        '''TODO: modify'''
        self.call_command(args)
    help_modify = generic_help
    #################################
    #Set permission
    #################################
    
    
    def do_setpermission(self, args):
        '''set permissions'''
        self.call_command(args)
    help_setpermissions = generic_help

    ################################
    #PUT
    ################################
    
    
    def do_put(self, args):
        '''TODO: put'''
        self.call_command(args)
    help_put = generic_help

    ################################
    #REMOVE
    ################################
    

    #def do_prueba(self,args):
    #    '''Prueba Help'''
    #    pass         
    
    #def do_remove(self, args):
        #'''TODO: put'''
        #self.call_command(args)
    #help_remove = generic_help

    ################################
    #List
    ################################
    
    def do_list(self, args):
        '''TODO: put'''
        self.call_command(args)
    help_list = generic_help

    #################################
    #User Del
    #################################
    
    
    def do_user(self, args):
        '''TODO: user'''
        self.call_command(args)
    help_user = generic_help
    
    #################################
    #Hist img
    #################################
    
    
    def do_user(self, args):
        '''TODO: user'''
        self.call_command(args)
    help_user = generic_help

    #################################
    #Hist users
    #################################
    
    
    def do_histuser(self, args):
        '''TODO: histuser'''
        self.call_command(args)
    help_histuser = generic_help


    #################################
    #Move nodes
    #################################
    
    
    def do_move(self, args):
        '''TODO: histuser'''
        self.call_command(args)
    help_move = generic_help

    #################################
    #Group nodes
    #################################
    
    
    def do_group(self, args):
        '''TODO: group'''
        self.call_command(args)
    help_group = generic_help

    #################################
    #Register nodes/images
    #################################
    
    
    def do_register(self, args):
        '''TODO: register'''
        self.call_command(args)
    help_register = generic_help

    

    def do_deregister(self, args):
        '''TODO: deregister'''
        self.call_command(args)
    help_deregister = generic_help

    #################################
    #Generate image
    #################################
    
    def do_generate(self, args):
        '''TODO: generate'''
        self.call_command(args)
    help_generate = generic_help

    
    def do_launch(self, args):
        '''TODO: launch'''
        self.call_command(args)    
    help_launch = generic_help
        

    def do_launchhadoop(self, args):
        '''TODO: launchhadoop'''
        self.call_command(args)    
    help_launchhadoop = generic_help

    
    def do_hpclist(self, args):
        '''TODO: listhpc'''
        self.call_command(args)    
    help_hpclist = generic_help
    
    
    def do_hpclistkernels(self, args):
        '''TODO: listhpc'''
        self.call_command(args)    
    help_hpclistkernels = generic_help
    
    
    def do_cloudlist(self, args):
        '''TODO: list clouds'''
        self.call_command(args)    
    help_cloudlist = generic_help
    

    def do_cloudlistkernels(self, args):
        '''TODO: list cloud kernels'''
        self.call_command(args)    
    help_cloudlistkernels = generic_help
    
    
    def do_listsites(self, args):
        '''TODO: list sites'''
        self.call_command(args)    
    help_listsites = generic_help
    

    def do_cloudinstancesterminate(self, args):
        '''TODO: terminate cloud kernels'''
        self.call_command(args)    
    help_cloudinstancesterminate = generic_help
    

    def do_hpcjobsterminate(self, args):
        '''TODO: terminate HPC jobs'''
        self.call_command(args)    
    help_cloudinstancesterminate = generic_help

    
    def do_cloudinstanceslist(self, args):
        '''TODO: list cloud instances'''
        self.call_command(args)    
    help_cloudinstanceslist = generic_help
        
    
    def do_hpcjobslist(self, args):
        '''TODO: list hpc jobs'''
        self.call_command(args)    
    help_hpcjobslist = generic_help

    ##########################################################################
    # LOAD
    ##########################################################################

    def do_exec(self, script_file):
        '''execute the script'''
        if script_file.strip() == "":
            self.help_exec()
            return

        if os.path.exists(script_file):
            with open(script_file, "r") as f:
                for line in f:
                    print ">", line   # runCLI originally had "line.strip()" here.
                    self.onecmd(line)
        else:
            ##ERROR('"%s" does not exist, could not evaluate it.' % script_file) #CHANGE TO PYTHON LOG
            pass

    def help_exec(self):
        msg = "Runs the specified script file. Lines from the script file are " + \
        "printed out with a '>' preceding them, for clarity."
        self.print_man("exec <script_file>", msg)


    #####################################
    # IO
    #####################################

    def loadhist(self, arguments):
        """Load history from the $HOME/.fg/hist.txt file
        """
        histfile = self._conf.getHistFile()

        try:
            readline.read_history_file(histfile)
        except IOError:
            #print "error"
            pass

        atexit.register(readline.write_history_file, histfile)

    def loadBanner(self):
        """Load banner from a file"""
        banner = pkgutil.get_data('futuregrid.shell','banner.txt') + \
            "\nWelcome to the FutureGrid Shell\n" + \
            "-------------------------------\n"
        return banner


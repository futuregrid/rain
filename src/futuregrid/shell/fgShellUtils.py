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
                print "######################################################################"
                print "\nSpecific Commands for the context: " + cntxt
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
    
    #################################
    #GET
    #################################

    def do_get(self, args):
        '''TODO: get'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "get(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no get method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_get = generic_help

    #################################
    #MODIFY
    #################################

    def do_modify(self, args):
        '''TODO: modify'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "modify(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no modify method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_modify = generic_help

    #################################
    #Set permission
    #################################

    def do_setpermission(self, args):
        '''set permissions'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "setpermission(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no setpermission method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_setpermission = generic_help

    ################################
    #PUT
    ################################

    def do_put(self, args):
        '''TODO: put'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "put(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no put method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_put = generic_help

    ################################
    #REMOVE
    ################################

    def do_remove(self, args):
        '''TODO: remove'''
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "remove(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no remove method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_remove = generic_help

    #def do_prueba(self,args):
    #    """Prueba Help"""
    #    pass         

    ################################
    #List
    ################################

    def do_list(self, args):
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "list(\"" + args + "\")"
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no list method in any of the active contexts (" + str(self._requirements)
                self._log.error(str(sys.exc_info()))
        else:
            self.generic_error()
    help_list = generic_help

    #################################
    #User Del
    #################################

    def do_user(self, args):        
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "user(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no user method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))
        else:
            self.generic_error()
    help_user = generic_help

    
    #################################
    #Hist img
    #################################

    def do_histimg(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "histimg(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no histimg method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_histimg = generic_help

    #################################
    #Hist users
    #################################

    def do_histuser(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "histuser(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no histuser method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_histuser = generic_help


    #################################
    #Move nodes
    #################################

    def do_move(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "move(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no move method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_move = generic_help

    #################################
    #Group nodes
    #################################

    def do_group(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "group(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no group method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_group = generic_help

    #################################
    #Register nodes/images
    #################################

    def do_register(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "register(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no register method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_register = generic_help

    #################################
    #Generate image
    #################################

    def do_generate(self, args):

        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "generate(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no generate method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_generate = generic_help

    def do_launch(self, args):
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                print prefix
                
                command = "self.do_" + prefix + "launch(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    print str(sys.exc_info())
                    pass
            if not found:
                print "There is no launch method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_launch = generic_help

    def do_launchhadoop(self, args):
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                print prefix
                
                command = "self.do_" + prefix + "launchhadoop(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    print str(sys.exc_info())
                    pass
            if not found:
                print "There is no launchhadoop method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_launchhadoop = generic_help

    def do_hpclist(self, args):        
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "hpclist(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no hpclist method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_hpclist = generic_help
    
    def do_hpclistkernels(self, args):        
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "hpclistkernels(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no hpclistkernels method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_hpclistkernels = generic_help
    
    def do_cloudlist(self, args):        
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "cloudlist(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no cloudlist method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_cloudlist = generic_help


    def do_cloudlistkernels(self, args):        
        if(self._use != ""):
            found = False
            for i in self._requirements:
                prefix=string.lower(i)
                command = "self.do_" + prefix + "cloudlistkernels(\"" + args + "\")"            
                try:
                    eval(command)
                    found = True
                    break
                except AttributeError:
                    pass
            if not found:
                print "There is no cloudlistkernels method in any of the active contexts (" + str(self._requirements) + " )"
                self._log.error(str(sys.exc_info()))         
        else:
            self.generic_error()
    help_cloudlistkernels = generic_help
    

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


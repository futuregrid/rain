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

A portion of this code has been taken from Cyberaide CoG kit shell 
(http://cogkit.svn.sourceforge.net/viewvc/cogkit/trunk)
cyberaide.org, cogkit.org

We have also use source code from the python library cmd 
"""

import inspect

from cmd2 import Cmd, make_option, options, Cmd2TestCase
import unittest, sys
import os
import cmd
import readline
import sys
import logging
import string
from getpass import getpass
import hashlib

from futuregrid.utils.fgLog import fgLog
from futuregrid.shell.fgShellUtils import fgShellUtils
from futuregrid.shell.fgShellRepo import fgShellRepo
#from futuregrid.shell.fgShellHadoop import fgShellHadoop
from futuregrid.shell.fgShellRain import fgShellRain
from futuregrid.shell.fgShellConf import fgShellConf
from futuregrid.shell.fgShellImage import fgShellImage
from futuregrid.utils import FGAuth
from futuregrid.utils.FGTypes import FGCredential

class fgShell(fgShellUtils,
              Cmd,
              fgShellRepo,
              fgShellRain,
              fgShellImage):

    # TODO: when a script file is used, we must switch on echo, when
    # it than gost to interactive it needs to be switched of?

    # TODO: the list command to list the last executed command is not
    # executable as it does not have a context and seems to have been
    # overwritten?

    # TODO: integrate the transcript feature via the --test flag,
    # e.g. we can reexecute a log file

    # TODO: provide nice documentation that shows how to load scripts
    # with @ and @@

    # TODO: document a use case that shows how to use timing e.g. set
    # timing True ...

    # TODO: documnet the "show" command and set --long

    # TODO: do we need multiline commands? should all commands be multiline?

    # TODO: we could use printing of feedback/info with pfeedback and
    # set quiet True/false. NOt sure if we want that

    # #####################################################################
    # setting variables that can be manipulated with a set method
    # #####################################################################

    maxrepeats = 3
    Cmd.settable.append('maxrepeats')

    # #####################################################################

    def __init__(self, silent, user, passwd):

        self.base_cmds = ['exec', 
                          'help', 
                          'history',
                          'manual', 
                          'quit', 
                          'use', 
                          'contexts', 
                          'script',
                          'setpasswd']
        base_cmd2 = ['li', 
                     'load', 
                     'pause', 
                     'py', 
                     'run', 
                     'save', 
                     'shortcuts', 
                     'set', 
                     'show', 
                     'historysession']

        self.base_cmds += base_cmd2

        self._locals = {}
        self._globals = {}

        self.user = user
        self.passwd = ""
        
        self.passwdtype = "ldappass"
        
        if passwd != "None":        
            userCred = FGCredential(self.passwdtype,passwd)
            if not self.check_simpleauth(userCred):
                sys.exit()


        #Load Config
        self._conf = fgShellConf()
        
        #Setup log  
        self._log = fgLog(self._conf.getLogFile(), self._conf.getLogLevel(), "FGShell", False)

        self._log.debug("\nReading Configuration file from " + self._conf.getConfigFile() + "\n")

        Cmd.__init__(self)        
        fgShellUtils.__init__(self)        

        #Context        
        self.env = ["repo", "image", "rain", ""] 
        self.text = {'image': 'Image Management',
                     'repo':'Image Repository',
                     'rain':'FG Dynamic Provisioning'}
                     
        self._use = ""
        self._requirements = []
        self._contextOn = [] # initialized contexts

        #Help
        self._docHelp = []
        self._undocHelp = []
        self._specdocHelp = []
        self.getDocUndoc("")

        self.prompt = "fg> "
        self.silent = silent
        if self.silent:
            self.intro = ""
        else:
            self.intro = self.loadBanner()
        ##Load History
        self.loadhist("no argument needed")
        #e = sysCheck()
        self.do_use("rain")        
    

    #TODO: GVL: Do wer realy need that method, its just from the original cmd2 code. I commented it out.
    """
    @options([make_option('-p', '--piglatin', action="store_true", help="atinLay"),
              make_option('-s', '--shout', action="store_true", help="N00B EMULATION MODE"),
              make_option('-r', '--repeat', type="int", help="output [n] times")
             ])
    def do_speak(self, arg, opts=None):
        '''Repeats what you tell me to.'''
        #self.maxrepeats = 3
        arg = ''.join(arg)
        if opts.piglatin:
            arg = '%s%say' % (arg[1:].rstrip(), arg[0])
        if opts.shout:
            arg = arg.upper()
        repetitions = opts.repeat or 1
        for i in range(min(repetitions, self.maxrepeats)):
            self.stdout.write(arg)
            self.stdout.write('\n')
    """

    def check_simpleauth(self, userCred):
        endloop = False
        passed = False        
        max_try=3
        cur_try=0
        while not endloop:                        
            if FGAuth.simpleauth(self.user, userCred):                
                print "Authentication OK"                
                endloop = True
                passed = True
                m = hashlib.md5()
                m.update(userCred.getCred())
                passwd = m.hexdigest()                
                self.passwd = passwd
            else:
                if cur_try<max_try:
                    msg = "Permission denied, please try again. User is " + self.user                    
                    print msg                    
                    userCred = FGCredential(self.passwdtype,getpass())
                    cur_try+=1
                else:
                    print "Permission denied."
                    endloop = True
                    passed = False
        return passed

    def do_setpasswd(self, arg):
        print "Please introduce the password for the user " + self.user
        m = hashlib.md5()
        m.update(getpass())
        self.passwd = m.hexdigest()
        
    def help_setpasswd(self):
        '''Help message for setpasswd'''
        msg = "setpasswd command: Modifies the password for the current session without leaving the shell"
        self.print_man("setpasswd", msg)    

    ################################
    # USE
    ###############################
    def do_use(self, arg):

        if (arg in self.env and self._use != arg):

            self._requirements = []
            self._use = arg

            if self._use == "":
                welcomestr = "\nChanging to default context"
            else:
                welcomestr = "\nChanging to " + self._use + " context"

            print welcomestr
            dashstr = ""
            for i in range(len(welcomestr)):
                dashstr += "-"
            print dashstr

            if (arg == "repo"):                
                self._requirements = ["Repo"]
            elif (arg == "rain"):
                self._requirements = ["Rain", "Repo", "Image"]#,"Gene","Rain"] #rain context requires initialize repo and generation
            elif (arg == "image"):
                self._requirements = ["Repo","Image"]

            allspec = {}
            for i in self._requirements:    
                self.getDocUndoc(string.lower(i))
                allspec[string.lower(i)]=self._specdocHelp                
                         
                if not i in self._contextOn:                    
                    try:
                        eval("fgShell" + i + ".__init__(self)")
                        self._contextOn.append(i)
                    except AttributeError:
                        print "The " + self._use + " context may not be initialized correctly"
                        self._log.error(str(sys.exc_info()))
            
            self.searchduplicated(allspec)
                        
            allspec_aux = []
            for i in self._requirements:
                allspec_aux.extend(allspec[string.lower(i)])
                                  
            self._specdocHelp = allspec_aux 
            
            temp = ""
            if not (arg == ""):
                temp = "-"
            self.prompt = "fg" + temp + "" + arg + ">"
        else:            
            print "ERROR: Incorrect Context. Available contexts are: " + \
                str(self.env) + \
                " For more information about the contexts execute the contexts command."           


    def help_use(self):
        msg = "Change the Shell CONTEXT to use a specific FG component. To see " + \
        "the available contexts use the \'contexts\' command. If no argument is " + \
        "provided it returns to the default context."

        self.print_man("use [context]", msg)

    def searchduplicated(self,allspec):
        #allspec={'repo': ['get', 'histimg', 'histuser', 'list', 'modify', 'put', 'remove', 'setpermission', 
        #                  'setuserquota', 'setuserrole', 'setuserstatus', 'useradd', 'userdel', 'userlist'], 
        #         'image': ['deploy', 'generate'],
        #         'rain' : ['deploy', 'move'],
        #         'another' : ['acomna','deploy', 'list']}
        #self._requirements=['repo','image','rain','another']
        #print allspec
        conflicset=set([])
        for i in range(len(self._requirements)):                             
            for j in range(i+1, len(self._requirements)):                
                newset=set(allspec[string.lower(self._requirements[i])]).intersection(set(allspec[string.lower(self._requirements[j])]))
                if len(newset) > 0:                    
                    conflicset = conflicset | newset                    
                    #print "newset" + str(newset)
                    #print "conflict" + str(conflicset)
                    for z in conflicset:
                        try:
                            allspec[string.lower(self._requirements[i])].remove(z)
                            allspec[string.lower(self._requirements[j])].remove(z)
                        except:
                            pass
                        allspec[string.lower(self._requirements[i])].append(string.lower(self._requirements[i])+z)
                        allspec[string.lower(self._requirements[j])].append(string.lower(self._requirements[j])+z)
                        #print allspec[string.lower(self._requirements[i])]
                
    ############################
    #CONTEXTS
    ############################

    def do_contexts(self, argument):
        '''Show the available CONTEXTS in FG Shell'''
        print "FG Contexts:"
        print "-------------"
        for i in self.env:
            if i != "":
                print i
                print "    " + self.text[i]

    def help_contexts(self):
        '''Help message for contexts'''
        self.print_man("contexts", self.do_contexts.__doc__)

    ##########################################################################
    # HISTORY
    ##########################################################################

    def do_history(self, line):
        '''Print a list of commands that have been entered.'''
        hist = []
        for i in range(readline.get_current_history_length()):
            hist.append(readline.get_history_item(i + 1))
        print hist

    do_hi = do_hist = do_history

    def help_history (self):
        '''Help message for the history command'''
        self.print_man("history", self.do_history.__doc__)
    help_hi = help_hist = help_history


    def do_historysession(self, line):
        '''Print a list of commands that have been entered in the current session'''
        Cmd.do_history(self, line)

    do_his = do_hists = do_historysession

    def help_historysession (self):
        '''Help message for the historysession command'''
        self.print_man("historysession", self.do_historysession.__doc__)

    help_his = help_hists = help_historysession

    ###########################
    # HELP 
    ###########################


    def getDocUndoc(self, args):
        
        final_doc = []
        final_undoc = []
        spec_doc = []
        names = dir(self.__class__)
        help = {}
        cmds_doc = []
        cmds_undoc = []
        use_doc = []
        use_undoc = []
        for name in names:
            if name[:5] == 'help_':
                help[name[5:]] = 1
        names.sort()
        prevname = ''
        for name in names:
            if name[:3] == 'do_':
                if name == prevname:
                    continue
                prevname = name
                com = name[3:]
                if (args == ""):
                    showit = True
                    for i in self.env:
                        if(i != "" and com.startswith(i)):
                            showit = False
                    if (showit):
                        if com in help:
                            cmds_doc.append(com)
                            del help[com]
                        elif getattr(self, name).__doc__:
                            cmds_doc.append(com)
                        else:
                            cmds_undoc.append(com)
                else:
                    if(com.startswith(args.strip())):
                        if com in help:
                            use_doc.append(com)
                            del help[com]
                        elif getattr(self, name).__doc__:
                            use_doc.append(com)
                        else:
                            use_undoc.append(com)
                    else:
                        if com in help:
                            cmds_doc.append(com)
                            del help[com]
                        elif getattr(self, name).__doc__:
                            cmds_doc.append(com)
                        else:
                            cmds_undoc.append(com)
        for i in self.base_cmds:
            if (i in cmds_doc):
                final_doc.append(i)
            elif (i in cmds_undoc):
                final_undoc.append(i)

        final_doc.sort()
        final_undoc.sort()

        if (args != ""):

            for i in use_doc:
                if i[len(args.strip()):] in cmds_doc:
                    #final_doc.append(i[len(self._use):])
                    spec_doc.append(i[len(args.strip()):])
                elif i[len(args.strip()):] in cmds_undoc:
                    if (self._use == ""):
                        final_undoc.append(i[len(args.strip()):])
                    else:
                        spec_doc.append(i[len(args.strip()):])
                else:
                    #final_doc.append(i)
                    spec_doc.append(i)
            for i in use_undoc:
                if i[len(args.strip()):] in cmds_undoc:
                    final_undoc.append(i[len(args.strip()):])
                else:
                    final_undoc.append(i)

            self._specdocHelp = spec_doc
        else:
            undoc = []
            allspec = []
            for i in self.env:
                if i != "":
                    self.getDocUndoc(i)
                    undoc.extend(self._undocHelp)
                    allspec.extend(self._specdocHelp)
            self._specdocHelp = allspec
            self._undocHelp.extend(undoc)

        self._docHelp = final_doc
        self._undocHelp = final_undoc


    
    def do_help(self, args):
        '''Get help on commands. 'help' or '?' with no arguments prints a 
        list of commands for which help is available. 'help <command>' or 
        ? <command>' gives help on <command>'''

        if (args.strip() == ""):
            print "\nA complete manual can be found in https://portal.futuregrid.org/man/fg-shell\n"
        ## The only reason to define this method is for the help text in the doc string        
        if (self._use == ""):
            #cmd.Cmd.do_help(self, args)
            undoc = []
            allspec = []
            self.customHelpNoContext(args)
            if (args.strip() == ""):
                for i in self.env:
                    if i != "":
                        self.getDocUndoc(i)
                        specdoc_header = self.text[i] + " commands. Execute \"use " + i + "\" to use them. (type help <topic>):"
                        cmd.Cmd.print_topics(self, specdoc_header, self._specdocHelp, 15, 80)
                        undoc.extend(self._undocHelp)
                        allspec.extend(self._specdocHelp)
                self._specdocHelp = allspec

            undoc_header = "Undocumented commands"
            self._undocHelp = undoc
            cmd.Cmd.print_topics(self, undoc_header, self._undocHelp, 15, 80)

            if (args.strip() == ""):
                print "Please select a CONTEXT by executing use <context_name>\n" + \
                      "Execute \'contexts\' command to see the available context names \n"

        else:
            self.customHelp(args)
    
    def help_help(self):
        '''Help method for the help command'''
        self.print_man("help [command]", self.do_help.__doc__)

    def customHelpNoContext(self, args):
        if args:
            try:
                #func = getattr(self, 'help_' + self._use + args)
                func = getattr(self, 'help_' + args)
            except AttributeError:
                try:
                    #doc = getattr(self, 'do_' + self._use + args).__doc__
                    doc = getattr(self, 'do_' + args).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (args,)))
                return
            func()
        else:
            self.getDocUndoc("")

            doc_header = "Generic Documented commands (type help <topic>):"
            undoc_header = "Generic Undocumented commands (type help <topic>):"

            cmd.Cmd.print_topics(self, doc_header, self._docHelp, 15, 80)
            #cmd.Cmd.print_topics(self,cmd.Cmd.misc_header, help.keys(), 15,80)
            cmd.Cmd.print_topics(self, undoc_header, self._undocHelp, 15, 80)

    def customHelp(self, args):
        if args:
            
            prefix=""
            base=False
            for i in self._requirements:
                if (args.strip().startswith(string.lower(i))):
                    args = args[len(string.lower(i)):]
                    prefix=string.lower(i)
                    break          
            
            if args in self.base_cmds:
                base=True
                
            if prefix.strip() == "" and not base:
                for i in self._requirements:
                    prefix=string.lower(i)
                    if args.strip() in self._specdocHelp:                        
                        try:
                            func = getattr(self, 'help_' + prefix + args)
                            func()
                            return
                        except AttributeError:
                            try:
                                doc = getattr(self, 'do_' + prefix + args).__doc__
                                if doc:
                                    self.stdout.write("%s\n" % str(doc))
                                    return
                            except AttributeError:
                                pass        
            else:
                try:
                    func = getattr(self, 'help_' + prefix + args)
                    func()
                    return
                except AttributeError:
                    try:
                        doc = getattr(self, 'do_' + prefix + args).__doc__
                        if doc:
                            self.stdout.write("%s\n" % str(doc))
                            return
                    except AttributeError:
                        pass
            self.stdout.write("%s\n" % str(self.nohelp % (args,)))
            return
            
        else:
            """
            self.getDocUndoc(self._use)

            doc_header = "General documented commands in the " + self._use + " context (type help <topic>):"
            undoc_header = "Undocumented commands in the " + self._use + " context (type help <topic>):"
            specdoc_header = "Specific documented commands in the " + self._use + " context (type help <topic>):"

            cmd.Cmd.print_topics(self, doc_header, self._docHelp, 15, 80)
            cmd.Cmd.print_topics(self, specdoc_header, self._specdocHelp, 15, 80)
            #cmd.Cmd.print_topics(self,cmd.Cmd.misc_header, help.keys(), 15,80)
            cmd.Cmd.print_topics(self, undoc_header, self._undocHelp, 15, 80)
            """            
            first = True
            allspec = {}
            undoc = {}
            for i in self._requirements:
                self.getDocUndoc(string.lower(i))                
                doc_header = "General documented commands (type help <topic>):"                
                if first:
                    cmd.Cmd.print_topics(self, doc_header, self._docHelp, 15, 80)
                    first=False
                
                allspec[string.lower(i)]=self._specdocHelp 
                undoc[string.lower(i)]=self._undocHelp
            
            self.searchduplicated(allspec)
                        
            allspec_aux = []
            allundoc = []
            for i in self._requirements:
                undoc_header = "Undocumented commands in the " + string.lower(i) + " context (type help <topic>):"
                specdoc_header = "Specific documented commands in the " + string.lower(i)  + " context (type help <topic>):"                
                cmd.Cmd.print_topics(self, specdoc_header, allspec[string.lower(i)], 15, 80)
                #cmd.Cmd.print_topics(self,cmd.Cmd.misc_header, help.keys(), 15,80)
                cmd.Cmd.print_topics(self, undoc_header, undoc[string.lower(i)], 15, 80)
                
                allspec_aux.extend(allspec[string.lower(i)])
                allundoc.extend(undoc[string.lower(i)])
                                  
            self._specdocHelp = allspec_aux 
            self._undocHelp = allundoc
            
    def complete_help(self, *args):
        listcmd = set(i for i in self._docHelp if i.startswith(args[0]))
        listcmd1 = set(i for i in self._undocHelp if i.startswith(args[0]))
        listcmd2 = set(i for i in self._specdocHelp if i.startswith(args[0]))
        return list(listcmd | listcmd1 | listcmd2)

    ###########################
    # Command Completion
    ###########################
    def completenames(self, *args):
        listcmd = set(i for i in self._docHelp if i.startswith(args[0]))
        listcmd1 = set(i for i in self._undocHelp if i.startswith(args[0]))
        listcmd2 = set(i for i in self._specdocHelp if i.startswith(args[0]))
        return list(listcmd | listcmd1 | listcmd2)

    ##########################################################################
    # PYTHON AND SHELL EXECUTION
    ##########################################################################

    def default(self, line):
        """Called when the command prefix is not recognized.
        
        In that case we execute the line as Python code.
        If a unix command is used it is executed without the !.
        The unix commands are defined in a function called unix."""

        # Is the line just a comment?  If so, ignore it and do nothing.
        if line.strip().startswith("#"):
            return

        command = line.strip().split(" ", 1)[0]
        if unix(command):
            os.system(line)
        else:
            try:
                exec(line) in self._locals, self._globals
            except Exception, e:
                print e.__class__, ":", e

    ##########################################################################
    # QUIT
    ##########################################################################

    def do_EOF(self, arguments):
        """Terminates the shell when a file is piped to it.
        
        This command terminates the shell when an EOF is reached in the input
        stream that has been piped to the program."""
        print "\n"
        self.do_quit(arguments)

    #def do_quit(self, arguments):
    #    """Terminates the shell, performing various clean-up actions."""

        #DEBUG("Terminating the shell")  #CHANGE TO PYTHON LOGS
    #    self.postloop()
    #    exit(1)

    #do_q = do_exit = do_quit

    def help_EOF(self):
        """Documentation for the EOF command."""

        print "The EOF character quits the command shell."
        print "This is useful for piping in commands from a script file."
        print "Functionally, this command is no different than 'quit'."
    help_eof = help_EOF

    def help_quit(self):
        msg = "This command terminates the Shell."
        self.print_man("quit", msg)
    help_q = help_exit = help_quit

    ##############################
    #PRE and POST commands
    ##############################

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)  # sets up command completion                
        self._locals = {}      # Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        cmd.Cmd.postloop(self)   # Clean up command completion
        #print "\nExiting..."

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.
        """
        lastcmd = readline.get_history_item(readline.get_current_history_length())
        if(self._script and lastcmd.strip() != "script end"):
            self._scriptList += [lastcmd.strip()]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass


def runCLI(user, passwd, filename, silent, interactive):
    '''runs the commandline shell
    
    @param filename commands within the file will be interpreted
    
    @param silent the commands will be interpreted silently

    @interactive after the commands are interpreted the shell is put
    into interactive mode
    '''
    
    if filename == None:        
        cli = fgShell(silent,user, passwd)                
        cli.cmdloop()        
    else:
        silent = True
        cli = fgShell(silent, user, passwd)
        cli.do_exec(filename)
        if interactive:
            cli.cmdloop()

def unix(command):
    """Only simple commands, cd is not supported."""

    return command in ("ls", "mkdir", "cp", "pwd")


if __name__ == '__main__':
    runCLI()


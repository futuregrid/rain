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

import sys
import os
import argparse
import hashlib
from getpass import getpass
sys.path.append(os.getcwd())

from futuregrid.shell import fgCLI

def usage():
    """Prints the usage description.
    
    Intended to be invoked when an invalid option is encountered on the command
    line."""

    print "DESCRIPTION"
    print
    print "  The fg shell is a simple command line like shell that"
    print "  assists in running small numbers of jobs in an interactive"
    print "  or script fashion on FutureGrid."
    print
    print "EXAMPLES"
    print
    print "  > fg"
    print
    print "    starts the fg shell in interactive mode"
    print
    print "  > cat file | fg"
    print
    print "    pipes the lines in the file to the cog shell and terminates"
    print
    print "  > fg -f file"
    print
    print "    reads the lines of the files, runs them and terminates"
    print
    print "  > fg -f file -i"
    print "         executes all lines in file and switches to the interactive mode"
    print


def main():
    
    parser = argparse.ArgumentParser(prog="fg-shell", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Shell Help ")
                                     #epilog=(usage()))    
    parser.add_argument('-u', '--user', dest='user', required=True, metavar='user', help='FutureGrid User name')
    parser.add_argument('-q', '--quiet', dest='quiet', action="store_true", help='Prevent to load banner and welcome messages')
    parser.add_argument('-i', '--interactive', dest='interactive', action="store_true", help='After the commands are interpreted ' 
                'the shell is put into interactive mode')
    parser.add_argument('-f', '--file', dest="file", metavar='script_file', help="Execute commands from a file" 
                        "(must be exact version and approved for use within FG). Not yet supported")
    parser.add_argument('--nopasswd', dest='nopasswd', action="store_true", default=False, help='If this option is used, the'
                        ' password is not requested. This is intended for systems daemons like Inca')
    
    args = parser.parse_args()
    
    print "Please insert the password for the user "+args.user+""
    
    passwd = getpass()
    
    #remove options from command line to avoid problems with cmd2
    sys.argv = sys.argv[:1]
        
    fgCLI.runCLI(args.user, passwd, args.file, args.quiet, args.interactive)

if __name__ == "__main__":
    main()

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

Rain
"""
__author__ = 'Javier Diaz'


import os
#import cmd
import readline
import sys
import logging
from cmd2 import Cmd
from cmd2 import options
from cmd2 import make_option
import textwrap
import argparse
import re
import time
from futuregrid.shell import fgShellUtils
from futuregrid.utils import fgLog
from futuregrid.rain.RainClient import RainClient
from futuregrid.rain.RainHadoop import RainHadoop

class fgShellRain(Cmd):

    def __init__(self):
        
        print "Init Rain"
        verbose = True
        debug = False
        self.rain = RainClient(self.user, verbose, debug)

    def do_rainlaunch(self, args):
        
        args = " " + args
        argslist = args.split(" -")[1:]        
        
        prefix = ''
        sys.argv=['']
        for i in range(len(argslist)):
            if argslist[i] == "":
                prefix = '-'
            else:
                newlist = argslist[i].split(" ")
                sys.argv += [prefix+'-'+newlist[0]]
                newlist = newlist [1:]
                rest = ""
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''
        
        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="rainlaunch", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Rain Help ")    
        #parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
        parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel" 
                        "(fg-register can list the available kernels for each infrastructure).")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-i', '--registeredimageid', dest='registeredimageid', metavar='ImgId', help='Id of the image in the target infrastructure. This assumes that the image'
                       ' is registered in the selected infrastructure.')
        group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Id of the image stored in the repository')
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='MachineName', help='Use the HPC infrastructure named MachineName (minicluster, india ...)')
        group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', help='Use the Eucalyptus Infrastructure, which is specified in the argument. The argument should not be needed.')
        #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='Use the OpenNebula Infrastructure, which is specified in the argument. The argument should not be needed.')
        #group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address', help='Use the Nimbus Infrastructure, which is specified in the argument. The argument should not be needed.')
        group1.add_argument('-s', '--openstack', dest='openstack', nargs='?', metavar='Address', help='Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        parser.add_argument('-m', '--numberofmachines', dest='machines', metavar='#instances', default=1, help='Number of machines needed.')
        parser.add_argument('-w', '--walltime', dest='walltime', metavar='hours', help='How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.')
        group2 = parser.add_mutually_exclusive_group(required=True)
        group2.add_argument('-j', '--jobscript', dest='jobscript', help='Script to execute on the provisioned images. In the case of Cloud environments, '
                        ' the user home directory is mounted in /tmp/N/u/username. The /N/u/username is only used for ssh between VM and store the ips of the parallel '
                        ' job in a file called /N/u/username/machines')
        group2.add_argument('-I', '--interactive', nargs='?', default=1, dest='interactive', help='Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.')
    
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
    
        image_source = "repo"
        image = args.imgid    
        if args.registeredimageid != None:
            image_source = "registered"
            image = args.registeredimageid
        elif args.imgid == None:  #when non imgId is provided
            image_source = "default"
            image = "default"
        if ('-j' in used_args or '--jobscript' in used_args):
            jobscript = os.path.expanduser(os.path.expandvars(args.jobscript))        
            if not os.path.isfile(jobscript):
                if not os.path.isfile("/" + jobscript.lstrip("/tmp")): #just in case the user indicates the path inside the VM
                    print 'Not script file found. Please specify an script file using the paramiter -j/--jobscript'            
                    sys.exit(1)
        else:#interactive mode
            jobscript=None
        
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))
        
        walltime=0.0
        if args.walltime != None:
            try:
                walltime=float(args.walltime)
            except:
                print "ERROR: Walltime must be a number. " + str(sys.exc_info())
                sys.exit(1)
        
        output = None
        if image_source == "repo":
            self.imgregister.setKernel(args.kernel)
            #self.imgregister.setDebug(args.debug)
            #XCAT
            if args.xcat != None:
                if args.imgid == None:
                    print "ERROR: You need to specify the id of the image that you want to register (-r/--imgid option)."
                    print "The parameter -i/--image cannot be used with this type of registration"
                    sys.exit(1)
                else:
                    output = self.imgregister.xcat_method(args.xcat, args.imgid)
                    time.sleep(3)
            else:
                ldap = True #we configure ldap to run commands and be able to login from on vm to other                                
                #EUCALYPTUS    
                if ('-e' in used_args or '--euca' in used_args):
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
                    else:    
                        output = self.imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, False, ldap, False)        
                        if output != None:
                            if re.search("^ERROR", output):
                                print output
                #OpenNebula
                elif ('-o' in used_args or '--opennebula' in used_args):
                    output = self.imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, False, ldap, False)
                #NIMBUS
                elif ('-n' in used_args or '--nimbus' in used_args):
                    #TODO        
                    print "Nimbus registration is not implemented yet"
                elif ('-s' in used_args or '--openstack' in used_args):                    
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                    else:    
                        output = self.imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, False, ldap, False)
                        if output != None:
                            if re.search("^ERROR", output):
                                print output
                else:
                    print "ERROR: You need to specify a registration target"
        elif image_source == "registered":
            output = args.registeredimageid
        else:
            output = image
        
        if output != None:   
            if not re.search("^ERROR", output):                         
                target = ""
                if args.xcat != None:          
                    if args.walltime != None:
                        walltime=int(walltime*3600)  
                    output = self.rain.baremetal(output, jobscript, args.machines, walltime)
                    if output != None:
                        print output
                else:
                    if ('-e' in used_args or '--euca' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables" 
                        else:
                            output = self.rain.euca(args.euca,output, jobscript, args.machines, varfile)
                            if output != None:
                                print output
                    elif ('-o' in used_args or '--opennebula' in used_args):
                        output = self.rain.opennebula(args.opennebula,output, jobscript, args.machines)
                    elif ('-n' in used_args or '--nimbus' in used_args):
                        output = self.rain.nimbus(args.nimbus,output, jobscript, args.machines, walltime)
                    elif ('-s' in used_args or '--openstack' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                        else:  
                            output = self.rain.openstack(args.openstack, output, jobscript, args.machines, varfile)
                            if output != None:
                                print output
                    else:
                        print "ERROR: You need to specify a Rain target (xcat, eucalyptus or openstack)"
                
            
        else:
            print "ERROR: invalid image id."
    
    def help_rainlaunch(self):
        msg = "Rain launch command: Run a command in the requested OS or enter in Interactive mode. The requested OS can be already registered in the requested " + \
              " infrastructure or stored in the Image Repository. The latter implies to register the image in the requested infrastructure"
        self.print_man("launch ", msg)
        eval("self.do_rainlaunch(\"-h\")")
    
    def do_rainlaunchhadoop(self, args):
        
        args = " " + args
        argslist = args.split(" -")[1:]        
        
        prefix = ''
        sys.argv=['']
        for i in range(len(argslist)):
            if argslist[i] == "":
                prefix = '-'
            else:
                newlist = argslist[i].split(" ")
                sys.argv += [prefix+'-'+newlist[0]]
                newlist = newlist [1:]
                rest = ""
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''
        
        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="rainlaunchhadoop", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Rain Help ")    
        #parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
        parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel" 
                        "(fg-register can list the available kernels for each infrastructure).")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-i', '--registeredimageid', dest='registeredimageid', metavar='ImgId', help='Id of the image in the target infrastructure. This assumes that the image'
                       ' is registered in the selected infrastructure.')
        group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Id of the image stored in the repository')
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='MachineName', help='Use the HPC infrastructure named MachineName (minicluster, india ...)')
        group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', help='Use the Eucalyptus Infrastructure, which is specified in the argument. The argument should not be needed.')
        #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='Use the OpenNebula Infrastructure, which is specified in the argument. The argument should not be needed.')
        #group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address', help='Use the Nimbus Infrastructure, which is specified in the argument. The argument should not be needed.')
        group1.add_argument('-s', '--openstack', dest='openstack', nargs='?', metavar='Address', help='Use the OpenStack Infrastructure, which is specified in the argument. The argument should not be needed.')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        parser.add_argument('-m', '--numberofmachines', dest='machines', metavar='#instances', default=1, help='Number of machines needed.')
        parser.add_argument('-w', '--walltime', dest='walltime', metavar='hours', help='How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.')
        group2 = parser.add_mutually_exclusive_group(required=True)
        group2.add_argument('-j', '--jobscript', dest='jobscript', help='Script to execute on the provisioned images. In the case of Cloud environments, '
                        ' the user home directory is mounted in /tmp/N/u/username. The /N/u/username is only used for ssh between VM and store the ips of the parallel '
                        ' job in a file called /N/u/username/machines')
        group2.add_argument('-I', '--interactive', nargs='?', default=1, dest='interactive', help='Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.')
        hp_group = parser.add_argument_group('Hadoop options', 'Additional options to run a hadoop job.')
        hp_group.add_argument('--inputdir', dest='inputdir', help = 'Location of the directory containing the job input data that has to be copied to HDFS. The HDFS directory will have the same name. Thus, if this option is used, the job script has to specify the name of the directory (not to all the path).')
        hp_group.add_argument('--outputdir', dest = 'outputdir', help = 'Location of the directory to store the job output data from HDFS. The HDFS directory will have the same name. Thus, if this option is used, the job script has to specify the name of the directory (not to all the path).')
        hp_group.add_argument('--hdfsdir', dest = 'hdfsdir', help = 'Location of the HDFS directory to use in the machines. If not provided /tmp/ will be used.')
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
    
        image_source = "repo"
        image = args.imgid    
        if args.registeredimageid != None:
            image_source = "registered"
            image = args.registeredimageid
        elif args.imgid == None:  #when non imgId is provided
            image_source = "default"
            image = "default"
            if not args.xcat:
                print "You need to specify the image Id using the -r/--imgid (image in the repository) or -i/--registeredimageid (image in the cloud framework)"
                sys.exit(1)
            
            
        if ('-j' in used_args or '--jobscript' in used_args):
            jobscript = os.path.expanduser(os.path.expandvars(args.jobscript))        
            if not os.path.isfile(jobscript):
                if not os.path.isfile("/" + jobscript.lstrip("/tmp")): #just in case the user indicates the path inside the VM
                    print 'Not script file found. Please specify an script file using the paramiter -j/--jobscript'            
                    sys.exit(1)
        else:#interactive mode
            jobscript=None
        
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))
        
        walltime=0.0
        if args.walltime != None:
            try:
                walltime=float(args.walltime)
            except:
                print "ERROR: Walltime must be a number. " + str(sys.exc_info())
                sys.exit(1)
        
        hadoop = RainHadoop()
        hadoop.setHdfsDir(args.hdfsdir)
        if args.inputdir != None:
            inputdir = os.path.expanduser(os.path.expandvars(args.inputdir))
            if not os.path.isdir(inputdir):
                if not os.path.isdir("/" + inputdir.lstrip("/tmp")): #just in case the user indicates the path inside the VM
                    print 'The input directory does not exists'            
                    sys.exit(1)   
            hadoop.setDataInputDir(inputdir)
        elif not args.interactive:
            print "Warning: Your are assuming that your input files are in HDFS."
        if args.outputdir != None:
            outputdir = os.path.expanduser(os.path.expandvars(args.outputdir))
            if not os.path.isdir(outputdir):
                if not os.path.isdir("/" + outputdir.lstrip("/tmp")): #just in case the user indicates the path inside the VM
                    print 'The input directory does not exists'            
                    sys.exit(1)           
            hadoop.setDataOutputDir(outputdir)
        elif not args.interactive:
            print "ERROR: You need to specify an output directory or you will not be able to get the results of your job."
            sys.exit(1)
        
        output = None
        if image_source == "repo":
            self.imgregister.setKernel(args.kernel)
            #self.imgregister.setDebug(args.debug)
            #XCAT
            if args.xcat != None:
                if args.imgid == None:
                    print "ERROR: You need to specify the id of the image that you want to register (-r/--imgid option)."
                    print "The parameter -i/--image cannot be used with this type of registration"
                    sys.exit(1)
                else:
                    output = self.imgregister.xcat_method(args.xcat, args.imgid)
                    time.sleep(3)
            else:
                ldap = True #we configure ldap to run commands and be able to login from on vm to other                                
                #EUCALYPTUS    
                if ('-e' in used_args or '--euca' in used_args):
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
                    else:    
                        output = self.imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, False, ldap, False)        
                        if output != None:
                            if re.search("^ERROR", output):
                                print output
                #OpenNebula
                elif ('-o' in used_args or '--opennebula' in used_args):
                    output = self.imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, False, ldap, False)
                #NIMBUS
                elif ('-n' in used_args or '--nimbus' in used_args):
                    #TODO        
                    print "Nimbus registration is not implemented yet"
                elif ('-s' in used_args or '--openstack' in used_args):                    
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                    else:    
                        output = self.imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, False, ldap, False)
                        if output != None:
                            if re.search("^ERROR", output):
                                print output
                else:
                    print "ERROR: You need to specify a registration target"
        elif image_source == "registered":
            output = args.registeredimageid
        else:
            output = image
        
        if output != None:   
            if not re.search("^ERROR", output):
                if args.xcat != None:
                    hadoop.setHpc(True)   
                    if args.walltime != None:
                        walltime=int(walltime*3600)  
                    output = self.rain.baremetal(output, jobscript, args.machines, walltime)
                    if output != None:
                        print output
                else:
                    hadoop.setHpc(False)
                    if ('-e' in used_args or '--euca' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables" 
                        else:
                            output = self.rain.euca(args.euca,output, jobscript, args.machines, varfile, hadoop)
                            if output != None:
                                print output
                    elif ('-o' in used_args or '--opennebula' in used_args):
                        output = self.rain.opennebula(args.opennebula,output, jobscript, args.machines, hadoop)
                    elif ('-n' in used_args or '--nimbus' in used_args):
                        output = self.rain.nimbus(args.nimbus,output, jobscript, args.machines, walltime, hadoop)
                    elif ('-s' in used_args or '--openstack' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                        else:  
                            output = self.rain.openstack(args.openstack, output, jobscript, args.machines, varfile, hadoop)
                            if output != None:
                                print output
                    else:
                        print "ERROR: You need to specify a Rain target (xcat, eucalyptus or openstack)"
                
            
        else:
            print "ERROR: invalid image id."
    
    def help_rainlaunchhadoop(self):
        msg = "Rain launchhadoop command: Run a hadoop job in the requested OS or enter in Interactive mode. The requested OS can be already registered in the requested " + \
              " infrastructure or stored in the Image Repository. The latter implies to register the image in the requested infrastructure. \n" +\
              "Rain will setup a hadoop cluster in the selected infrastructure. It assumes that Java is installed in the image/machine."
        self.print_man("launchhadoop ", msg)
        eval("self.do_rainlaunchhadoop(\"-h\")")
 
    """
    def do_rainmove(self, args):

        self.help_rainmove()

    def help_rainmove(self):
        msg = "RAIN move command: Move a node between between IaaS clouds to and from HPC. " + \
              "Available destination are: HPC, eucalyptus, nimbus\n "
        self.print_man("move <hostname> <destination>", msg)

    def do_raingroup(self, args):

        self.help_raingroup()

    def help_raingroup(self):
        msg = "RAIN group command: Define a group of nodes and reserve them. \n "
        self.print_man("group <hostname_list> <set_name>", msg)

    def do_raindeploy(self, args):

        self.help_raindeploy()

    def help_raindeploy(self):
        msg = "RAIN deploy command: Deploy an image in a particular set of nodes. " + \
              "The imgId refers to an image stored in the Image Repository or to the specification " + \
              "of an image that need to be generated\n "
        self.print_man("deploy <imgId> <infrastructure>", msg)
    """

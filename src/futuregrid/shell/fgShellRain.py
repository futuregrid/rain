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
        self.instancetypelist=['m1.small', 'm1.large', 'm1.xlarge']

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
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='SiteName', help='Select the HPC infrastructure named SiteName (minicluster, india ...).')
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', help='Select the OpenNebula Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimibus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure located in SiteName (india, sierra...).')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        parser.add_argument('-m', '--numberofmachines', dest='machines', metavar='#instances', default=1, help='Number of machines needed.')
        parser.add_argument('--volume', dest='volumes', metavar='size', default=0, help='This creates and attach a volume of the specified size to each instance. The size is in GigaBytes. This is supported by Eucalyptus and OpenStack.')
        parser.add_argument('-t','--instance-type', dest='instancetype', metavar='InstanceType', default='m1.small', help='VM Image type to run the instance as. Valid values: ' + str(self.instancetypelist))
        parser.add_argument('-w', '--walltime', dest='walltime', metavar='hours', help='How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.')
        group2 = parser.add_mutually_exclusive_group(required=True)
        group2.add_argument('-j', '--jobscript', dest='jobscript', help='Script to execute on the provisioned images. In the case of Cloud environments, '
                        ' the user home directory is mounted in /tmp/N/u/username. The /N/u/username is only used for ssh between VM and store the ips of the parallel '
                        ' job in a file called /N/u/username/machines')
        group2.add_argument('-I', '--interactive', nargs='?', default=1, dest='interactive', help='Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.')
        group2.add_argument('-b', '--background', action="store_true", default=False, dest='background', help='Background mode. It boots VMs or provisions bare-metal machines. Then, it gives you the information you need to know to log in anytime.')
        
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
        elif ('-b' in used_args or '--background' in used_args):
            jobscript="background"  
        else:
            jobscript="interactive"
        
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))
        
        if not args.instancetype in self.instancetypelist:
            print "ERROR: Instance type must be one of the following values: " + str(self.instancetypelist)
            sys.exit(1)
        
        volume=int(args.volume)
        
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
                            output = self.rain.euca(args.euca,output, jobscript, args.machines, varfile, None, args.instancetype, volume)
                            if output != None:
                                print output
                    elif ('-o' in used_args or '--opennebula' in used_args):
                        output = self.rain.opennebula(args.opennebula,output, jobscript, args.machines, None, args.instancetype)
                    elif ('-n' in used_args or '--nimbus' in used_args):
                        output = self.rain.nimbus(args.nimbus,output, jobscript, args.machines, walltime, None, args.instancetype)
                    elif ('-s' in used_args or '--openstack' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                        else:  
                            output = self.rain.openstack(args.openstack, output, jobscript, args.machines, varfile, None, args.instancetype, volume)
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
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='SiteName', help='Select the HPC infrastructure named SiteName (minicluster, india ...).')
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', help='Select the OpenNebula Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimibus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure located in SiteName (india, sierra...).')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        parser.add_argument('-m', '--numberofmachines', dest='machines', metavar='#instances', default=1, help='Number of machines needed.')
        parser.add_argument('--volume', dest='volume', metavar='size', default=0, help='This creates and attach a volume of the specified size to each instance. The size is in GigaBytes. This is supported by Eucalyptus and OpenStack.')
        parser.add_argument('-t','--instance-type', dest='instancetype', metavar='InstanceType', default='m1.small', help='VM Image type to run the instance as. Valid values: ' + str(self.instancetypelist))
        parser.add_argument('-w', '--walltime', dest='walltime', metavar='hours', help='How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.')
        group2 = parser.add_mutually_exclusive_group(required=True)
        group2.add_argument('-j', '--jobscript', dest='jobscript', help='Script to execute on the provisioned images. In the case of Cloud environments, '
                        ' the user home directory is mounted in /tmp/N/u/username. The /N/u/username is only used for ssh between VM and store the ips of the parallel '
                        ' job in a file called /N/u/username/machines')
        group2.add_argument('-I', '--interactive', nargs='?', default=1, dest='interactive', help='Interactive mode. It boots VMs or provisions bare-metal machines. Then, the user is automatically logged into one of the VMs/machines.')
        group2.add_argument('-b', '--background', action="store_true", default=False, dest='background', help='Background mode. It boots VMs or provisions bare-metal machines. Then, it gives you the information you need to know to log in anytime.')
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
        
        if not args.instancetype in self.instancetypelist:
            print "ERROR: Instance type must be one of the following values: " + str(self.instancetypelist)
            sys.exit(1)    
            
        if ('-j' in used_args or '--jobscript' in used_args):
            jobscript = os.path.expanduser(os.path.expandvars(args.jobscript))        
            if not os.path.isfile(jobscript):
                if not os.path.isfile("/" + jobscript.lstrip("/tmp")): #just in case the user indicates the path inside the VM
                    print 'Not script file found. Please specify an script file using the paramiter -j/--jobscript'            
                    sys.exit(1)
        elif ('-b' in used_args or '--background' in used_args):
            jobscript="background"
        else:
            jobscript="interactive"
        
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))
        
        volume=math.ceil(args.volume)
        
        
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
                    output = self.rain.baremetal(output, jobscript, args.machines, walltime, hadoop)
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
                            output = self.rain.euca(args.euca,output, jobscript, args.machines, varfile, hadoop, args.instancetype, volume)
                            if output != None:
                                print output
                    elif ('-o' in used_args or '--opennebula' in used_args):
                        output = self.rain.opennebula(args.opennebula,output, jobscript, args.machines, hadoop, args.instancetype)
                    elif ('-n' in used_args or '--nimbus' in used_args):
                        output = self.rain.nimbus(args.nimbus,output, jobscript, args.machines, walltime, hadoop, args.instancetype)
                    elif ('-s' in used_args or '--openstack' in used_args):
                        if varfile == "":
                            print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                        elif not os.path.isfile(varfile):
                            print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                        else:  
                            output = self.rain.openstack(args.openstack, output, jobscript, args.machines, varfile, hadoop, args.instancetype,volume)
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
 
    def do_rainlisthpcjobs(self, args):
        '''Rain listhpcjobs command: Get list of HPC jobs. 
        '''
        
        self.do_shell("showq "+args)
                
    def help_rainlisthpcjobs(self):
        '''Help message for the rainlisthpcjobs command'''
        self.print_man("listhpcjobs <machine>", self.do_listhpcjobs.__doc__)


    def do_rainlistcloudinstances(self, args):
        
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
        
        
        parser = argparse.ArgumentParser(prog="listcloudinstances", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Rain Help ")
        parser.add_argument('-i', '--instance', dest="instance", metavar='InstanceId', help="Id of the instance to check status. This is optional, if not provided all instances will be listed.")                         
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', help='Select the OpenNebula Infrastructure located in SiteName (india, sierra...).')
        #group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimibus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure located in SiteName (india, sierra...).')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
        
        varfile = ""
        if args.varfile != None:
            varfile = os.path.expandvars(os.path.expanduser(args.varfile))

        
        
        if ('-e' in used_args or '--euca' in used_args):
            if varfile == "":
                print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
            elif not os.path.isfile(varfile):
                print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables" 
            else:
                output = self.rain.euca(args.euca,args.instance, "list", None, varfile, None, None, None)
                if output != None:
                    print output
        elif ('-o' in used_args or '--opennebula' in used_args):
            output = self.rain.opennebula(args.opennebula,args.instance, "list", None, None, None)
        elif ('-n' in used_args or '--nimbus' in used_args):
            output = self.rain.nimbus(args.nimbus,args.instance, "list", None, None, None, None)
        elif ('-s' in used_args or '--openstack' in used_args):
            if varfile == "":
                print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
            elif not os.path.isfile(varfile):
                print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
            else:  
                output = self.rain.openstack(args.openstack, args.instance, "list", None, varfile, None, None, None)
                if output != None:
                    print output
        else:
            print "ERROR: You need to specify a Rain target (eucalyptus or openstack)"

    
    def help_rainlaunch(self):
        msg = "Rain launch command: Run a command in the requested OS or enter in Interactive mode. The requested OS can be already registered in the requested " + \
              " infrastructure or stored in the Image Repository. The latter implies to register the image in the requested infrastructure"
        self.print_man("launch ", msg)
        eval("self.do_rainlaunch(\"-h\")")
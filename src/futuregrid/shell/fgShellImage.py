#!/usr/bin/env python
"""
FutureGrid Command Line Interface

Image Management
"""
__author__ = 'Javier Diaz'

import os
#import cmd
import readline
import sys
from futuregrid.shell import fgShellUtils
import logging
from futuregrid.utils import fgLog
from cmd2 import Cmd
from cmd2 import options
from cmd2 import make_option
import textwrap
import argparse
import re

from futuregrid.image.management.IMRegister import IMRegister
from futuregrid.image.management.IMGenerate import IMGenerate

class fgShellImage(Cmd):

    def __init__(self):
        
        print "Init Image"
        
        self.imgen = IMGenerate(None, None, None, self.user, None, None, None, None, self.passwd, True, False, False, False,1.5)
        self.imgregister = IMRegister(None, self.user, self.passwd, True, False)
        
        
    def extra_help(self):
        msg = "Useful information about the software. Currently, we do not parse the packages names provided within the -s/--software option" +\
             "Therefore, if some package name is wrong, it won't be installed. Here we provide a list of useful packages names from the official repositories: \n" +\
             "CentOS: mpich2, python26, java-1.6.0-openjdk. More packages names can be found in http://mirror.centos.org/\n" +\
             "Ubuntu: mpich2, openjdk-6-jre, openjdk-6-jdk. More packages names can be found in http://packages.ubuntu.com/ \n\n" +\
             "FutureGrid Performance packages (currently only for CentOS 5): fg-intel-compilers, intel-compilerpro-common, " +\
             "intel-compilerpro-devel, intel-compilerproc, intel-compilerproc-common, intel-compilerproc-devel " +\
             "intel-compilerprof, intel-compilerprof-common, intel-compilerprof-devel, intel-openmp, intel-openmp-devel, openmpi-intel"
        return msg
   
    def do_imagegenerate(self, args):

        #Default params
        base_os = ""
        spacer = "-"
        # TODO: GVL: should they be in a configuration file?
        default_ubuntu = "maverick"
        default_debian = "lenny"
        default_rhel = "5.5"
        default_centos = "5.6"
        default_fedora = "13"
        #kernel = "2.6.27.21-0.1-xen"
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
        #print sys.argv
        
        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="imagegenerate", 
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description="FutureGrid Image Generation Help",
                                         epilog=self.extra_help())
        parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
        parser.add_argument("-o", "--os", dest="OS", required=True, metavar='OSName', help="Specify the desired Operating System for the new image. Currently, Centos and Ubuntu are supported")
        parser.add_argument("-v", "--version", dest="version", metavar='OSversion', help="Operating System version. In the case of Centos, it can be 5 or 6. In the case of Ubuntu, it can be karmic(9.10), lucid(10.04), maverick(10.10), natty (11.04), oneiric (11.10), precise (12.04)")
        parser.add_argument("-a", "--arch", dest="arch", metavar='arch', help="Destination hardware architecture. Currently x86_64 or i386.")
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument("--baseimage", dest="baseimage", default=False, action="store_true", help="Generate a Base Image that will be used to generate other images. In this way, the image generation process will be faster.")    
        group1.add_argument("-s", "--software", dest="software", metavar='software', help="List of software packages, separated by commas, that will be installed in the image.")
        parser.add_argument("--scratch", dest="scratch", default=False, action="store_true", help="Generate the image from scratch without using any Base Image from the repository.")
        parser.add_argument("-n", "--name", dest="givenname", metavar='givenname', help="Desired recognizable name of the image")
        parser.add_argument("-e", "--description", dest="desc", metavar='description', help="Short description of the image and its purpose")
        parser.add_argument("-g", "--getimg", dest="getimg", default=False, action="store_true", help="Retrieve the image instead of uploading to the image repository")
        parser.add_argument("-z", "--size", default=1.5, dest="size", help="Specify size of the Image in GigaBytes. The size must be large enough to install all the software required. The default and minimum size is 1.5GB, which is enough for most cases.")
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        if len(used_args) == 0:
            parser.print_help()
            return
        
        print 'Image generate client...'
        
        verbose = True
        
        if args.size < 1.5:
            args.size=1.5
        
        arch = "x86_64" #Default to 64-bit
    
        #Parse arch command line arg
        if args.arch != None:
            if args.arch == "i386" or args.arch == "i686":
                arch = "i386"
            elif args.arch == "amd64" or args.arch == "x86_64":
                arch = "x86_64"
            else:
                print "ERROR: Incorrect architecture type specified (i386|x86_64)"
                sys.exit(1)
    
        print 'Selected Architecture: ' + arch
    
        # Build the image
        version = ""
        #Parse OS and version command line args
        OS = ""
        if args.OS == "Ubuntu" or args.OS == "ubuntu":
            OS = "ubuntu"
            supported_versions = ["karmic","lucid","maverick","natty", "oneiric","precise"]
            if args.version == None:
                version = default_ubuntu
            elif args.version == "9.10" or args.version == "karmic":
                version = "karmic"
            elif args.version == "10.04" or args.version == "lucid":
                version = "lucid"
            elif args.version == "10.10" or args.version == "maverick":
                version = "maverick"
            elif args.version == "11.04" or args.version == "natty":
                version = "natty"
            elif args.version == "11.10" or args.version == "oneiric":
                version = "oneiric"
            elif args.version == "12.04" or args.version == "precise":
                version = "precise"
            else:
                print "ERROR: Incorrect OS version specified. Supported OS version for " + OS + " are " + str(supported_versions)
                sys.exit(1)
        #elif args.OS == "Debian" or args.OS == "debian":
        #    OS = "debian"
        #    version = default_debian
        #elif args.OS == "Redhat" or args.OS == "redhat" or args.OS == "rhel":
        #    OS = "rhel"
        #    version = default_rhel
        elif args.OS == "CentOS" or args.OS == "CentOS" or args.OS == "centos":
            OS = "centos"
            supported_versions = ["5","6"]
            if args.version == None:
                version = default_centos            
            elif re.search("^5", str(args.version)):
                version = "5"
            elif re.search("^6", str(args.version)):
                version = "6"
            else:
                print "ERROR: Incorrect OS version specified. Supported OS version for " + OS + " are " + str(supported_versions)
                sys.exit(1)
                
        #elif args.OS == "Fedora" or args.OS == "fedora":
        #    OS = "fedora"
        #    version = default_fedora
        else:
            print "ERROR: Incorrect OS type specified. Currently only Centos and Ubuntu are supported"
            sys.exit(1)
        
        #self.imgen = IMGenerate(arch, OS, version, self.user, args.software, args.givenname, args.desc, args.getimg, self.passwd, verbose, args.debug)
        self.imgen.setArch(arch)
        self.imgen.setOs(OS)
        self.imgen.setVersion(version)
        self.imgen.setSoftware(args.software)
        self.imgen.setGivenname(args.givenname)
        self.imgen.setDesc(args.desc)
        self.imgen.setGetimg(args.getimg)
        self.imgen.setDebug(args.debug)
        self.imgen.setBaseImage(args.baseimage)
        self.imgen.setScratch(args.scratch)
        self.imgen.setSize(args.size)
        
        status = self.imgen.generate()
        
        if status != None:
            if args.getimg:
                print "The image is located in " + str(status)
            else:
                print "Your image has be uploaded in the repository with ID=" + str(status)
            if not args.baseimage:
                print '\n The image and the manifest generated are packaged in a tgz file.' + \
                  '\n Please be aware that this FutureGrid image does not have kernel and fstab. Thus, ' + \
                  'it is not built for any infrastructure. To register the new image, use the Image Management register command.'
            else:
                print '\n The image and the manifest generated are packaged in a tgz file.' + \
                '\n Please be aware that this Base Image is not ready for registration. This is intended to be used for generating other images'
                
    def help_imagegenerate(self):
        msg = "IMAGE generate command: Generate an image "              
        self.print_man("generate ", msg)
        eval("self.do_imagegenerate(\"-h\")")

    def do_imageregister(self, args):

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
                #print newlist
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''

        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="imageregister", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Registration Help ")
        parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')        
        group = parser.add_mutually_exclusive_group(required=True)    
        group.add_argument('-i', '--image', dest='image', metavar='ImgFile', help='Select the image to register by specifying its location. The image is a tgz file that contains the manifest and image files.')
        group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Select the image to register by specifying its Id in the repository.')
        #group.add_argument('-l', '--list', dest='list', action="store_true", help='List images registered in xCAT/Moab or in the Cloud Frameworks')
        parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel. "
                        "Case a) if the image has to be adapted (any image generated with the generate command) this option can be used to select one of the available kernels. Both kernelId and ramdiskId will be selected according to the selected kernel. This case is for any infrastructure. "
                        "Case b) if the image is ready to be registered, you may need to specify the id of the kernel in the infrastructure. This case is when -j/--justregister is used and only for cloud infrastructures.")
        parser.add_argument('-a', '--ramdisk', dest="ramdisk", metavar='ramdiskId', help="Specify the desired ramdisk that will be associated to "
                        "your image in the cloud infrastructure. This option is only needed if -j/--justregister is used.")
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='SiteName', help='Select the HPC infrastructure named SiteName (minicluster, india ...).')
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...)')        
        group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', help='Select the OpenNebula Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimbus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure located in SiteName (india, sierra...)')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files.  Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        parser.add_argument('-g', '--getimg', dest='getimg', action="store_true", help='Customize the image for a particular cloud framework but does not register it. So the user gets the image file.')
        parser.add_argument('-p', '--noldap', dest='ldap', action="store_false", default=True, help='If this option is active, FutureGrid LDAP will not be configured in the image. This option only works for Cloud registrations. LDAP configuration is needed to run jobs using rain.')
        parser.add_argument('-w', '--wait', dest='wait', action="store_true", help='Wait until the image is available in the targeted infrastructure. Currently this is used by Eucalyptus and OpenStack')
        parser.add_argument('-j', '--justregister', dest='justregister', action="store_true", default=False, help='It assumes that the image is ready to run in the selected infrastructure. '
                            'Thus, no additional configuration will be performed. Only valid for Cloud infrastructures. (This is basically a wrapper of the tools that register images into the cloud infrastructures)')
        
        args = parser.parse_args()
    
        print 'Image register client...'
        
        verbose = True #to activate the print
    
        #TODO: if Kernel is provided we need to verify that it is supported. 
        
        self.imgregister.setKernel(args.kernel)
        self.imgregister.setDebug(args.debug) #this wont work, need to modify fgLog
        
    
        used_args = sys.argv[1:]
        
        #print args
        
        image_source = "repo"
        image = args.imgid    
        if args.image != None:
            image_source = "disk"
            image = args.image
            if not  os.path.isfile(args.image):            
                print 'ERROR: Image file not found'            
                sys.exit(1)
        #XCAT
        if args.xcat != None:
            if args.imgid == None:
                print "ERROR: You need to specify the id of the image that you want to register (-r/--imgid option)."
                print "The parameter -i/--image cannot be used with this type of registration"
                sys.exit(1)
            
            else:
                imagename = self.imgregister.xcat_method(args.xcat, args.imgid, "register")
                if imagename != None:            
                    print 'Your image has been registered in xCAT as ' + str(imagename) + '\n Please allow a few minutes for xCAT to register the image before attempting to use it.'
                    print 'To run a job in a machine using your image you use the launch command of the rain context (use rain). For more info type: help launch'
                    print 'You can also do it by executing the next command: qsub -l os=<imagename> <scriptfile>' 
                    print 'In the second case you can check the status of the job with the checkjob and showq commands'
                    print 'qsub, checkjob and showq are Moab/torque commands. So you need to execute them from outside of this shell or type the ! character before the command'
        else:    
            ldap = args.ldap #configure ldap in the VM
            varfile=""
            if args.varfile != None:
                varfile=os.path.expanduser(args.varfile)
            #EUCALYPTUS    
            if ('-e' in used_args or '--euca' in used_args):
                if args.justregister:
                    output = self.imgregister.iaas_justregister(args.euca, image, image_source, args.ramdisk, "euca", varfile, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
                elif not args.getimg:            
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
                    
                    else:    
                        output = self.imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, args.getimg, ldap, args.wait)
                        if output != None:
                            if re.search("^ERROR", output):
                                print output             
                
                else:    
                    self.imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, args.getimg, ldap, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output        
            #OpenNebula
            elif ('-o' in used_args or '--opennebula' in used_args):            
                output = self.imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, args.getimg, ldap, args.wait)
            #NIMBUS
            elif ('-n' in used_args or '--nimbus' in used_args):
                if args.justregister:
                    output = self.imgregister.iaas_justregister(args.nimbus, image, image_source, args.ramdisk, "nimbus", varfile, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
                elif not args.getimg:
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the Nimbus environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the Nimbus environment variables"
                    
                    else:    
                        output = self.imgregister.iaas_generic(args.nimbus, image, image_source, "nimbus", varfile, args.getimg, ldap, args.wait)
                        if output != None:
                            if re.search("^ERROR", output):
                                print output 
                
                else:    
                    output = self.imgregister.iaas_generic(args.nimbus, image, image_source, "nimbus", varfile, args.getimg, ldap, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
            elif ('-s' in used_args or '--openstack' in used_args):
                if args.justregister:
                    output = self.imgregister.iaas_justregister(args.openstack, image, image_source, args.ramdisk, "openstack", varfile, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
                elif not args.getimg:
                    if args.varfile == None:
                        print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                    elif not os.path.isfile(str(os.path.expanduser(varfile))):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                    
                    else:    
                        output = self.imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, args.getimg, ldap, args.wait)
                        if output != None:
                            if re.search("^ERROR", output):
                                print output 
                
                else:    
                    output = self.imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, args.getimg, ldap, args.wait)
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
            else:
                print "ERROR: You need to specify the targeted infrastructure where your image will be registered"

    def help_imageregister(self):
        msg = "IMAGE register command: Register an image in a FG infrastructure. \n "
        self.print_man("register ", msg)
        eval("self.do_imageregister(\"-h\")")

    def do_imagehpclist(self, args):
        '''Image Management hpclist command: Get list of images registered in the specified HPC machine (India for example). 
        '''
        args = self.getArgs(args)

        if(len(args) == 1):
            hpcimagelist = self.imgregister.xcat_method(args[0], None, "list")
            if hpcimagelist != None:
                print "The list of available images on xCAT/Moab is:"
                for i in hpcimagelist:
                    print "  "+ i
                print "You can get more details by querying the image repository using the list command and the query string: * where tag=imagename. \n" +\
                      "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username."
                    
        else:
            self.help_imagehpclist()
        
    def help_imagehpclist(self):
        '''Help message for the imagehpclist command'''
        self.print_man("hpclist <machine>", self.do_imagehpclist.__doc__)
    
    def do_imagehpclistkernels(self, args):
        '''Image Management hpclistkernels command: Get list of kernels for HPC. You need to specify a machine (India for example). 
        '''
        args = self.getArgs(args)

        if(len(args) == 1):
            kernelslist = self.imgregister.xcat_method(args[0], None, "kernels")
            if kernelslist != None:
                print "The list of available kernels for HPC is:"
                output = kernelslist.split("&")
                defaultkernels=eval(output[0])
                kernels=eval(output[1])
                print "\nDefault Kernels"
                print "---------------"
                for i in defaultkernels:
                    print i
                    print defaultkernels[i]
                print "\nAuthorized Kernels"
                print "-------------------"
                for i in kernels:
                    print i
                    print kernels[i]                    
        else:
            self.help_imagehpclistkernels()
        
    def help_imagehpclistkernels(self):
        '''Help message for the imagehpclistkernels command'''
        self.print_man("hpclistkernels <SiteName>", self.do_imagehpclistkernels.__doc__)
    
    def do_imagecloudlist(self, args):
        '''Image Management cloudlist command: Get list of images registered in the specified Cloud infrastructure (nimbus, eucalyptus, openstack...). 
        '''
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
                #print newlist
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''

        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="imagecloudlist", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Cloud List Help ")
        group1 = parser.add_mutually_exclusive_group()        
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='List images registered into the Eucalyptus Infrastructure located in SiteName (india, sierra...)')        
        #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='List images registered into the OpenNebula Infrastructure, which is specified in the argument. The argument should not be needed.')
        group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='List images registered into the Nimbus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='List images registered into the OpenStack Infrastructure located in SiteName (india, sierra...)')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
        if len(used_args) == 0:
            parser.print_help()
            return
        
        if args.varfile != None:
            varfile=os.path.expanduser(args.varfile)
        #EUCALYPTUS    
        if ('-e' in used_args or '--euca' in used_args):                        
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
            else:    
                output = self.imgregister.cloudlist(str(args.euca),"euca", varfile)
                if output != None:   
                    if not isinstance(output, list):
                        print output
                    else: 
                        print "The list of available images on OpenStack is:"                    
                        for i in output:                       
                            print i   
                        print "You can get more details by querying the image repository using the list command and the query string: \"* where tag=imagename\". \n" +\
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img.manifest.xml"        
      
        #OpenNebula
        elif ('-o' in used_args or '--opennebula' in used_args):
            pass #TODO when OpenNebula is on FutureGrid            
            #output = self.imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, args.getimg, ldap)
        #NIMBUS
        elif ('-n' in used_args or '--nimbus' in used_args):
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the Nimbus environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the Nimbus environment variables"
            else:    
                output = self.imgregister.cloudlist(str(args.nimbus),"nimbus", varfile)
                if output != None:   
                    if not isinstance(output, list):
                        print output
                    else:
                        print "The list of available images on Nimbus is:"                  
                        for i in output:                       
                            print i
                        print "You can get more details by querying the image repository using the list command and the query string: \"* where tag=imagename\". \n" +\
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img.manifest.xml"
        elif ('-s' in used_args or '--openstack' in used_args):            
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
            else:    
                output = self.imgregister.cloudlist(str(args.openstack),"openstack", varfile)
                if output != None:   
                    if not isinstance(output, list):
                        print output
                    else:
                        print "The list of available images on OpenStack is:"                  
                        for i in output:                       
                            print i
                        print "You can get more details by querying the image repository using the list command and the query string: \"* where tag=imagename\". \n" +\
                    "NOTE: To query the repository you need to remove the OS from the image name (centos,ubuntu,debian,rhel...). " + \
                      "The real name starts with the username and ends before .img.manifest.xml"
        
        
    def help_imagecloudlist(self):
        msg = "IMAGE cloudlist command: List Images registered in the specified Cloud Framework \n "
        self.print_man("cloudlist ", msg)
        eval("self.do_imagecloudlist(\"-h\")")
    
    def do_imagecloudlistkernels(self, args):
        '''Image Management cloudlistkernels command: Get list kernels available for the specified Cloud. 
        '''
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
                #print newlist
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''

        #TODO: GVL: maybe do some reformating to smaller line length

        parser = argparse.ArgumentParser(prog="imagecloudlistkernels", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Cloud List Kernels Help ")
        group1 = parser.add_mutually_exclusive_group(required=True)        
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', default="", help='List available Kernels for Eucalyptus located in SiteName (india, sierra...)')        
        group1.add_argument('-o', '--opennebula', dest='opennebula', metavar='SiteName', default="", help='List available Kernels for OpenNebula located in SiteName (india, sierra...)')
        group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', default="", help='List available Kernels for Nimbus located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', default="", help='List available Kernels for OpenStack located in SiteName (india, sierra...)')        
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
        if len(used_args) == 0:
            parser.print_help()
            return
        
        #EUCALYPTUS    
        if ('-e' in used_args or '--euca' in used_args):            
            kernelslist = self.imgregister.iaas_generic(args.euca, "kernels", "", "euca", "", False, False, False)
            if kernelslist != None:
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                if defaultkernels != "" and kernels:
                    print "The list of available kernels for Eucalyptus on " + str(args.euca) + " is:"
                    print "\nDefault Kernels"
                    print "---------------"                          
                    print defaultkernels
                    print "\nAuthorized Kernels"
                    print "-------------------"
                    kernelsout = []                                
                    for i in kernels:          
                        kernelsout.append(i)
                    print kernelsout
                else:
                    print "ERROR: Eucalytpus is not supported on " + str(args.euca) + "\n"
      
        #OpenNebula
        elif ('-o' in used_args or '--opennebula' in used_args):            
            kernelslist = self.imgregister.iaas_generic(args.opennebula, "kernels", "", "opennebula", "", False, False, False)
            if kernelslist != None:
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                if defaultkernels != "" and kernels:
                    print "The list of available kernels for OpenNebula " + str(args.opennebula) + " is:"
                    print "\nDefault Kernels"
                    print "---------------"                
                    print defaultkernels
                    print "\nAuthorized Kernels"
                    print "-------------------"
                    kernelsout = []                                
                    for i in kernels:          
                        kernelsout.append(i)
                    print kernelsout
                else:
                    print "ERROR: OpenNebula is not supported on " + str(args.nimbus) + "\n"
        #NIMBUS
        elif ('-n' in used_args or '--nimbus' in used_args):
            kernelslist = self.imgregister.iaas_generic(args.nimbus, "kernels", "", "nimbus", "", False, False, False)
            if kernelslist != None:
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                if defaultkernels != "" and kernels:
                    print "The list of available kernels for the Nimbus located on " + str(args.nimbus) + " is:"
                    print "\nDefault Kernels"
                    print "---------------"                
                    print defaultkernels
                    print "\nAuthorized Kernels"
                    print "-------------------"
                    kernelsout = []                                
                    for i in kernels:          
                        kernelsout.append(i)
                    print kernelsout
                else:
                    print "ERROR: Nimbus is not supported on " + str(args.nimbus) + "\n"
        elif ('-s' in used_args or '--openstack' in used_args):            
            kernelslist = self.imgregister.iaas_generic(args.openstack, "kernels", "", "openstack", "", False, False, False)
            if kernelslist != None:
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]                    
                kernels = kernelslist_dic["Authorized"]
                if defaultkernels != "" and kernels:
                    print "The list of available kernels for the OpenStack located on " + str(args.openstack) + " is:"
                    print "\nDefault Kernels"
                    print "---------------"                
                    print defaultkernels
                    print "\nAuthorized Kernels"
                    print "-------------------"
                    kernelsout = []                                
                    for i in kernels:          
                        kernelsout.append(i)
                    print kernelsout
                else:
                    print "ERROR: OpenStack is not supported on " + str(args.openstack) + "\n"
        
    def help_imagecloudlistkernels(self):
        msg = "IMAGE cloudlistkernels command: List kernels available for the specified Cloud Framework \n "
        self.print_man("cloudlistkernels ", msg)
        eval("self.do_imagecloudlistkernels(\"-h\")")
    
    def do_imagederegister(self, args):
        '''Image Management deregister command: Deregister image from the specified infrastructure. 
        '''
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
                #print newlist
                for j in range(len(newlist)):
                    rest+=" "+newlist[j]
                if rest.strip() != "":
                    rest=rest.strip()
                    sys.argv += [rest]
                #sys.argv += [prefix+'-'+argslist[i]]
                prefix = ''

        parser = argparse.ArgumentParser(prog="imagederegister", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Image Deregister Help ")
        parser.add_argument('--deregister', dest='deregister', metavar='ImgId', required=True, help='Deregister an image from the specified infrastructure.')
        group1 = parser.add_mutually_exclusive_group()        
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='SiteName', help='Select the HPC infrastructure named SiteName (minicluster, india ...).')    
        group1.add_argument('-e', '--euca', dest='euca', metavar='SiteName', help='Select the Eucalyptus Infrastructure located in SiteName (india, sierra...)')        
        #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='List images registered into the OpenNebula Infrastructure, which is specified in the argument. The argument should not be needed.')
        group1.add_argument('-n', '--nimbus', dest='nimbus', metavar='SiteName', help='Select the Nimbus Infrastructure located in SiteName (india, sierra...)')
        group1.add_argument('-s', '--openstack', dest='openstack', metavar='SiteName', help='Select the OpenStack Infrastructure located in SiteName (india, sierra...)')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus, OpenStack and Nimbus.')
                
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
        if len(used_args) == 0:
            parser.print_help()
            return
        
        if args.varfile != None:
            varfile=os.path.expanduser(args.varfile)
        
        #XCAT
        if args.xcat != None:
            imagename = self.imgregister.xcat_method(args.xcat, args.imgid, "remove")
            if imagename != None:  
                if re.search("^ERROR", imagename):
                    print imagename
                else:
                    print "The image " + args.deregister + " has been deleted successfully."
            else:
                print "ERROR: removing image"  
        #EUCALYPTUS
        elif ('-e' in used_args or '--euca' in used_args):                        
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
            else:    
                output = self.imgregister.cloudremove(str(args.euca),"euca", varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output        
      
        #OpenNebula
        elif ('-o' in used_args or '--opennebula' in used_args):
            pass #TODO when OpenNebula is on FutureGrid            
            #output = self.imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, args.getimg, ldap)
        #NIMBUS
        elif ('-n' in used_args or '--nimbus' in used_args):
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the Nimbus environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the Nimbus environment variables"
            else:    
                output = self.imgregister.cloudremove(str(args.nimbus),"nimbus", varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output
        elif ('-s' in used_args or '--openstack' in used_args):            
            if args.varfile == None:
                print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
            elif not os.path.isfile(str(os.path.expanduser(varfile))):
                print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
            else:    
                output = self.imgregister.cloudremove(str(args.openstack),"openstack", varfile, str(args.deregister))
                if output == True:
                    print "Image removed successfully"
                elif output == False:
                    print "ERROR removing image. Please verify that the imageid is " + str(args.deregister)
                else:
                    print output
        
        
    def help_imagederegister(self):
        msg = "IMAGE deregister command: Deregister an image from the specified infrastructure \n "
        self.print_man("cloudlist ", msg)
        eval("self.do_imagederegister(\"-h\")")
        
    def do_imagelistsites(self, args):
        cloudinfo = self.imgregister.iaas_generic(None, "infosites", "", "", "", None, False, False)
        if cloudinfo != None:
            cloudinfo_dic = eval(cloudinfo)
            print "Supported Sites Information"
            print "===========================\n"
            print "Cloud Information"
            print "-----------------"
            for i in cloudinfo_dic:
                print "SiteName: " + i
                print "  Description: " + cloudinfo_dic[i][0]
                print "  Infrastructures supported: " + str(cloudinfo_dic[i][1:])
        
        self.imgregister.setVerbose(False)
        
        hpcinfo_dic = self.imgregister.xcat_sites()
        if len(hpcinfo_dic) != 0:
            print "\nHPC Information (baremetal)"
            print "---------------------------"
            for i in hpcinfo_dic:
                print "SiteName: " + i
                print "  RegisterXcat Service Status: " + hpcinfo_dic[i][0]
                print "  RegisterMoab Service Status: " + hpcinfo_dic[i][1]
        self.imgregister.setVerbose(True)
            
    def help_imagelistsites(self):
        msg = "IMAGE listsites command: List supported sites with their respective HPC and Cloud services \n "
        self.print_man("cloudlist ", msg)
        eval("self.do_imagederegister(\"-h\")")


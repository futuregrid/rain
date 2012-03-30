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
                                         description="FutureGrid Image Generation Help")
        parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
        parser.add_argument("-o", "--os", dest="OS", metavar='OSName', help="specify destination Operating System. Currently only Centos and Ubuntu are supported")
        parser.add_argument("-v", "--version", dest="version", metavar='OSversion', help="Operating System version. In the case of Centos it can be 5 or 6. In the case of Ubuntu karmic(9.10), lucid(10.04), maverick(10.10), natty (11.04)")
        parser.add_argument("-a", "--arch", dest="arch", metavar='arch', help="Destination hardware architecture. Currently x86_64 or i386.")
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument("--baseimage", dest="baseimage", default=False, action="store_true", help="Generate a Base Image that will be used to generate user's images. This base image will NOT be ready for registration.")    
        group1.add_argument("-s", "--software", dest="software", metavar='software', help="Software list to be automatically installed")
        parser.add_argument("--scratch", dest="scratch", default=False, action="store_true", help="Generate the image from scratch without using any Base Image from the repository.")
        parser.add_argument("-n", "--name", dest="givenname", metavar='givenname', help="Desired recognizable name of the image")
        parser.add_argument("-e", "--description", dest="desc", metavar='description', help="Short description of the image and its purpose")
        parser.add_argument("-g", "--getimg", dest="getimg", default=False, action="store_true", help="Retrieve the image instead of uploading to the image repository")
        parser.add_argument("-z", "--size", default=1.5, dest="size", help="Specify size of the Image in GigaBytes. The size must be large enough to install all the software required. The default size is 1.5GB, which is enough for most cases.")
        
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
            supported_versions = ["karmic","lucid","maverick","natty"]
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
        parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel" 
                            "(must be exact version and approved for use within FG). Not yet supported")
        group = parser.add_mutually_exclusive_group(required=True)    
        group.add_argument('-i', '--image', dest='image', metavar='ImgFile', help='tgz file that contains manifest and img')
        group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Id of the image stored in the repository')
        #group.add_argument('-l', '--list', dest='list', action="store_true", help='List images registered in xCAT/Moab or in the Cloud Frameworks')
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('-x', '--xcat', dest='xcat', metavar='MachineName', help='Register image to xCAT. The argument is the machine name (minicluster, india ...)')
        group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', help='Register the image to Eucalyptus, which is in the specified addr')        
        group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='Register the image to OpenNebula, which is in the specified addr')
        group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address', help='Register the image to Nimbus, which is in the specified addr')
        group1.add_argument('-s', '--openstack', dest='openstack', nargs='?', metavar='Address', help='Register the image to OpenStack, which is in the specified addr')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus and OpenStack')
        parser.add_argument('-g', '--getimg', dest='getimg', action="store_true", help='Customize the image for a particular cloud framework but does not register it. So the user gets the image file.')
        parser.add_argument('-p', '--ldap', dest='ldap', action="store_true", help='Configure ldap in the VM. This is needed if you plan to use you VM with the rain commands')
        parser.add_argument('-w', '--wait', dest='wait', action="store_true", help='Wait until the image is available. Currently this is used by Eucalyptus and OpenStack')
        
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
                imagename = self.imgregister.xcat_method(args.xcat, args.imgid)
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
                if not args.getimg:            
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
                if not args.getimg:
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
                if not args.getimg:
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
            hpcimagelist = self.imgregister.xcat_method(args[0], "list")
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
            kernelslist = self.imgregister.xcat_method(args[0], "kernels")
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
        self.print_man("hpclistkernels <machine>", self.do_imagehpclistkernels.__doc__)
    
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
        group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', help='List Images registered in Eucalyptus, which is in the specified addr')        
        #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='List Image from OpenNebula, which is in the specified addr')
        group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address', help='List Images registered in Nimbus, which is in the specified addr')
        group1.add_argument('-s', '--openstack', dest='openstack', nargs='?', metavar='Address', help='List Images registered OpenStack, which is in the specified addr')
        parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus and OpenStack')
        
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
        group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', default="", help='List available Kernels for Eucalyptus, which is in the specified addr')        
        group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address:port', default="", help='List available Kernels for OpenNebula, which is in the specified addr')
        group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address:port', default="", help='List available Kernels for Nimbus, which is in the specified addr')
        group1.add_argument('-s', '--openstack', dest='openstack',nargs='?', metavar='Address:port', default="", help='List available Kernels for OpenStack, which is in the specified addr')        
        
        args = parser.parse_args()
        
        used_args = sys.argv[1:]
        
        if len(used_args) == 0:
            parser.print_help()
            return
        
        #EUCALYPTUS    
        if ('-e' in used_args or '--euca' in used_args):            
            kernelslist = self.imgregister.iaas_generic("", "kernels", "", "euca", "", False, False, False)
            if kernelslist != None:
                print "The list of available kernels for Eucalyptus is:"                
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                print "\nDefault Kernels"
                print "---------------"                          
                print defaultkernels
                print "\nAuthorized Kernels"
                print "-------------------"
                kernelsout = []                                
                for i in kernels:          
                    kernelsout.append(i)
                print kernelsout        
      
        #OpenNebula
        elif ('-o' in used_args or '--opennebula' in used_args):            
            kernelslist = self.imgregister.iaas_generic("", "kernels", "", "opennebula", "", False, False, False)
            if kernelslist != None:
                print "The list of available kernels for OpenNebula is:"                
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                print "\nDefault Kernels"
                print "---------------"                
                print defaultkernels
                print "\nAuthorized Kernels"
                print "-------------------"
                kernelsout = []                                
                for i in kernels:          
                    kernelsout.append(i)
                print kernelsout
        #NIMBUS
        elif ('-n' in used_args or '--nimbus' in used_args):
            kernelslist = self.imgregister.iaas_generic("", "kernels", "", "nimbus", "", False, False, False)
            if kernelslist != None:
                print "The list of available kernels for Nimbus is:"                
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                print "\nDefault Kernels"
                print "---------------"                
                print defaultkernels
                print "\nAuthorized Kernels"
                print "-------------------"
                kernelsout = []                                
                for i in kernels:          
                    kernelsout.append(i)
                print kernelsout
        elif ('-s' in used_args or '--openstack' in used_args):            
            kernelslist = self.imgregister.iaas_generic("", "kernels", "", "openstack", "", False, False, False)
            if kernelslist != None:
                print "The list of available kernels for OpenStack is:"                
                kernelslist_dic = eval(kernelslist)
                defaultkernels = kernelslist_dic["Default"]
                kernels = kernelslist_dic["Authorized"]
                print "\nDefault Kernels"
                print "---------------"                
                print defaultkernels
                print "\nAuthorized Kernels"
                print "-------------------"
                kernelsout = []                                
                for i in kernels:          
                    kernelsout.append(i)
                print kernelsout
        
    def help_imagecloudlistkernels(self):
        msg = "IMAGE cloudlistkernels command: List kernels available for the specified Cloud Framework \n "
        self.print_man("cloudlistkernels ", msg)
        eval("self.do_imagecloudlistkernels(\"-h\")")
        

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
It generates the images for different OS
"""
__author__ = 'Javier Diaz, Andrew Younge'

from optparse import OptionParser
from types import *
import re
import logging
import logging.handlers
import glob
import random
import os
import sys
import socket
from subprocess import *
import time
import re
#from xml.dom.ext import *
from xml.dom.minidom import Document, parse


logger = None
def main():
    global tempdir
    global namedir #this == name is to clean up when something fails
    global http_server
    global bcfg2_url
    global bcfg2_port
    global baseimageuri
    global onlybaseimage
    global size
    

    #Set up random string    
    random.seed()
    randid = str(random.getrandbits(32))

    

    #Default params
    base_os = ""
    spacer = "-"
    latest_ubuntu = "lucid"
    latest_debian = "lenny"
    latest_rhel = "5.5"
    latest_centos = "5.6"
    latest_fedora = "13"
    #kernel = "2.6.27.21-0.1-xen"

    #ubuntu-distro = ['lucid', 'karmic', 'jaunty']
    #debian-distro = ['squeeze', 'lenny', 'etch']
    #rhel-distro = ['5.5', '5.4', '4.8']
    #fedora-distro = ['14','12']


    parser = OptionParser()
    #help is auto-generated
    parser.add_option("-o", "--os", dest="os", help="specify destination Operating System")
    parser.add_option("-v", "--version", dest="version", help="Operating System version")
    parser.add_option("-a", "--arch", dest="arch", help="Destination hardware architecture")
    parser.add_option("-s", "--software", dest="software", help="Software stack to be automatically installed")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Enable debugging")
    parser.add_option("-u", "--user", dest="user", help="FutureGrid username")
    parser.add_option("-n", "--name", dest="givenname", help="Desired recognizable name of the image")
    parser.add_option("-e", "--description", dest="desc", help="Short description of the image and its purpose")
    parser.add_option("-t", "--tempdir", dest="tempdir", help="directory to be use in to generate the image")
    parser.add_option("-c", "--httpserver", dest="httpserver", help="httpserver to download config files")    
    parser.add_option("-i", "--baseimageuri", dest="baseimageuri", help="Base Image URI. This is used to generate the user image")
    parser.add_option("-b", "--baseimage", action="store_true", default=False, dest="baseimage", help="Generate Base Image")
    parser.add_option("-l", "--logfile", default='fg-image-generate.log', dest="logfile", help="Generate Base Image")
    parser.add_option("-z", "--size", default=1.5, dest="size", help="Size of the Image. The default one is 1.5GB.")
        
    #parser.add_option("-b", "--bcfg2url", dest="bcfg2url", help="address where our IMBcfg2GroupManagerServer is listening")
    #parser.add_option("-p", "--bcfg2port", dest="bcfg2port", help="port where our IMBcfg2GroupManagerServer is listening")
    (ops, args) = parser.parse_args()
    
    
    #Set up logging
    log_filename = ops.logfile
    
    logger = logging.getLogger("GenerateScript")
    logger.setLevel(logging.DEBUG)    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(log_filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    
    logger.info('Starting image generator...')

    #Check if we have root privs 
    if os.getuid() != 0:
        logger.error("Sorry, you need to run with root privileges")
        sys.exit(1)

    
    size = float(ops.size)
    size = int(size * 1024) # size of the image >= 1.5GB
    
    baseimageuri = ops.baseimageuri #None or uri

    onlybaseimage = ops.baseimage #True only create base image

    if type(ops.httpserver) is not NoneType:
        http_server = ops.httpserver
    else:
        logger.error("You need to provide the http server that contains files needed to create images")
        sys.exit(1)
    """    
    if type(ops.bcfg2url) is not NoneType:
        bcfg2_url = ops.bcfg2url
    else:
        logger.error("You need to provide the address of the machine where IMBcfg2GroupManagerServer.py is listening")
        sys.exit(1)
    if type(ops.bcfg2port) is not NoneType:
        bcfg2_port = int(ops.bcfg2port)
    else:
        logger.error("You need to provide the port of the machine where IMBcfg2GroupManagerServer.py is listening")
        sys.exit(1)
    """
    if type(ops.tempdir) is not NoneType:
        tempdir = ops.tempdir
        if(tempdir[len(tempdir) - 1:] != "/"):
            tempdir += "/"
    else:
        tempdir = "/tmp/"

    #the if-else is not needed, but can be useful to execute this script alone
    #user = ops.user
    if type(ops.user) is not NoneType:
        user = ops.user
    else:
        user = "default"

    logger.debug('FG User: ' + user)

    namedir = user + '' + randid

    arch = ops.arch

    logger.debug('Selected Architecture: ' + arch)

    #Parse Software stack list
    if ops.software != "None":

        #Assume its comma seperated, so parse
        packages = re.split('[, ]', ops.software)
        #packages = ops.software.split(', ')
        packs = ' '.join(packages)
        logger.debug('Selected software packages: ' + packs)
    else:
        packs = 'wget'

    # Build the image
    #OS and Version already parsed in client side, just assign it
    if baseimageuri == None:
        create_base_os = True
    else:
        create_base_os = False
        
    version = ops.version
    if ops.os == "ubuntu":
        base_os = base_os + "ubuntu" + spacer

        logger.info('Building Ubuntu ' + version + ' image')
           

        img = buildUbuntu(namedir, version, arch, packs, tempdir, create_base_os)

    elif ops.os == "debian":
        base_os = base_os + "debian" + spacer
    elif ops.os == "rhel":
        base_os = base_os + "rhel" + spacer
    elif ops.os == "centos":
        base_os = base_os + "centos" + spacer

        logger.info('Building Centos ' + version + ' image')
        
        img = buildCentos(namedir, version, arch, packs, tempdir, create_base_os)


    elif ops.os == "fedora":
        base_os = base_os + "fedora" + spacer

   # logger.info('Generated image is available at '+tempdir+' ' + img + '.img.  Please be aware that this FutureGrid image is packaged without a kernel and fstab and is not built for any deployment type.  To deploy the new image, use the fg-image-deploy command.')

    if type(ops.givenname) is NoneType:
        ops.givenname = img

    if type(ops.desc) is NoneType:
        ops.desc = " "

    manifest(user, img, ops.os, version, arch, packs, ops.givenname, ops.desc, tempdir)

    print img
    # Cleanup
    #TODO: verify everything is unmounted, delete temporary folder

#END MAIN

def handleBaseImage(tempdir, name):
    if size > int(1.5 * 1024):
        runCmd('mkdir ' + tempdir + '' + name + "_old")
        runCmd('/bin/mount -o loop ' + baseimageuri + " " + tempdir + '' + name + "_old")
        runCmd('dd if=/dev/zero of=' + tempdir + '' + name + '.img bs=1024k seek=' + str(size) + ' count=0')
        runCmd('/sbin/mke2fs -F -j ' + tempdir + '' + name + '.img')
        runCmd('mount -o loop ' + tempdir + '' + name + '.img ' + tempdir + '' + name)
        os.system('mv -f ' + tempdir + '' + name + "_old/* " + tempdir + '' + name + "/")
        runCmd('/bin/umount ' + tempdir + '' + name + "_old")
        if os.path.dirname(baseimageuri).rstrip("/") != tempdir.rstrip("/"):
            runCmd("rm -rf " + os.path.dirname(baseimageuri) + " " + tempdir + '' + name + "_old")
        
    else:
        runCmd("mv " + baseimageuri + " " + tempdir + '' + name + '.img')
        if os.path.dirname(baseimageuri).rstrip("/") != tempdir.rstrip("/"):
            runCmd("rm -rf " + os.path.dirname(baseimageuri))
        runCmd('/bin/mount -o loop ' + tempdir + '' + name + '.img ' + tempdir + '' + name)

def createBaseImageDisk(tempdir, name):
           
    runCmd('dd if=/dev/zero of=' + tempdir + '' + name + '.img bs=1024k seek=' + str(size) + ' count=0')
    runCmd('/sbin/mke2fs -F -j ' + tempdir + '' + name + '.img')
    runCmd('/bin/mount -o loop ' + tempdir + '' + name + '.img ' + tempdir + '' + name)

def buildUbuntu(name, version, arch, pkgs, tempdir, base_os):

    output = ""
    namedir = name

    ubuntuLog = logging.getLogger('GenerateScript.ubuntu')

    runCmd('mkdir ' + tempdir + '' + name)

    if not base_os:
        ubuntuLog.info('Retrieving Image: ubuntu-' + version + '-' + arch + '-base.img')        
        
        handleBaseImage(tempdir, name)
        
    elif base_os:
        ubuntuLog.info('Generation Image: centos-' + version + '-' + arch + '-base.img')
        ubuntuLog.info('Creating Disk for the image')
        
        createBaseImageDisk(tempdir, name)    
    
    #The image is mounted

    if base_os:

        #to create base_os
        #centosLog.info('Modifying repositories to match the version requested')
        ubuntuLog.info('Installing base OS')
        start = time.time()
        #runCmd('yum --installroot='+tempdir+''+name+' -y groupinstall Core')
        runCmd('debootstrap --include=grub,language-pack-en,openssh-server --components=main,universe,multiverse ' + version + ' ' + tempdir + '' + name)
        end = time.time()
        ubuntuLog.info('TIME base OS:' + str(end - start))
        
        ubuntuLog.info('Copying configuration files')

#Move next 3 to deploy        
        #os.system('echo "search idpm" > '+tempdir+''+name+'/etc/resolv.conf')
        os.system('echo "nameserver 129.79.1.1" >> ' + tempdir + '' + name + '/etc/resolv.conf')
        os.system('echo "nameserver 172.29.202.149" >> ' + tempdir + '' + name + '/etc/resolv.conf')

        os.system('echo "127.0.0.1 localhost.localdomain localhost" > ' + tempdir + '' + name + '/etc/hosts')
        
        # Setup package repositories 
        #TODO: Set mirros to IU/FGt
        ubuntuLog.info('Configuring repositories')
    
        #runCmd('wget ' + http_server + '/conf/ubuntu/' + version + '-sources.list -O ' + tempdir + '' + name + '/etc/apt/sources.list')
        f = open(tempdir + '' + name + '/etc/apt/source.list', 'w')
        f.write('deb http://us.archive.ubuntu.com/ubuntu/ ' + version + ' main restricted \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + ' main restricted \n'      
        'deb http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates main restricted \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates main restricted \n'
        'deb http://us.archive.ubuntu.com/ubuntu/ ' + version + ' universe \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + ' universe \n' 
        'deb http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates universe \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates universe \n'     
        'deb http://us.archive.ubuntu.com/ubuntu/ ' + version + ' multiverse \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + ' multiverse \n' 
        'deb http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates multiverse \n' 
        'deb-src http://us.archive.ubuntu.com/ubuntu/ ' + version + '-updates multiverse ')
        f.close()        
        
        os.system('mkdir -p ' + tempdir + '' + name + "/root/.ssh")
        
        #Mount proc and pts
        runCmd('mount --bind /proc ' + tempdir + '' + name + '/proc')
        runCmd('mount --bind /dev ' + tempdir + '' + name + '/dev')
        ubuntuLog.info('Mounted proc and dev')
    
        #key to intall packages
        runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 98932BEC')
        runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' apt-get update')
    
        #services will install, but not start
        os.system('mkdir -p /usr/sbin')
        os.system('echo "#!/bin/sh" >' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
        os.system('echo "exit 101" >>' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
        os.system('chmod +x ' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
    
        start = time.time()
        
        ubuntuLog.info('Installing some util packages')
        runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' /usr/bin/env PATH=/usr/local/sbin:/usr/sbin:/sbin:/bin:/usr/bin apt-get -y install wget nfs-common gcc make man curl time')
        
        cmd='/usr/sbin/chroot ' + tempdir + '' + name + ' /usr/bin/env PATH=/usr/local/sbin:/usr/sbin:/sbin:/bin:/usr/bin apt-get -y install libcrypto++8'
        outstat=os.system(cmd)
        if outstat != 0:
            cmd='/usr/sbin/chroot ' + tempdir + '' + name + ' /usr/bin/env PATH=/usr/local/sbin:/usr/sbin:/sbin:/bin:/usr/bin apt-get -y install libcrypto++9'
            ubuntuLog.debug(cmd)
            outstat=os.system(cmd)
        else:
            ubuntuLog.debug(cmd)
            
        end = time.time()
        ubuntuLog.info('TIME util packages:' + str(end - start))
        
        #Setup networking
        os.system('echo "localhost" > ' + tempdir + '' + name + '/etc/hostname')
        runCmd('hostname localhost')
        
        runCmd('wget ' + http_server + '/conf/ubuntu/interfaces -O ' + tempdir + '' + name + '/etc/network/interfaces')
    
        ubuntuLog.info('Injected networking configuration')
        
        #base_os done

    if not onlybaseimage:       
        if not base_os:
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + " rm -f /etc/mtab~*  /etc/mtab.tmp")
            #Mount proc and pts
            runCmd('mount --bind /proc ' + tempdir + '' + name + '/proc')
            runCmd('mount --bind /dev ' + tempdir + '' + name + '/dev')
            ubuntuLog.info('Mounted proc and dev')
            
            #services will install, but not start
            os.system('mkdir -p /usr/sbin')
            os.system('echo "#!/bin/sh" >' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
            os.system('echo "exit 101" >>' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
            os.system('chmod +x ' + tempdir + '' + name + '/usr/sbin/policy-rc.d')
    

        start = time.time()
        #Install packages
        if pkgs != None:
            ubuntuLog.info('Installing user-defined packages')
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' /usr/bin/env -i PATH=/usr/local/sbin:/usr/sbin:/sbin:/bin:/usr/bin apt-get -y install ' + pkgs)  #NON_INTERACTIVE
            ubuntuLog.info('Installed user-defined packages')
    
        end = time.time()
        ubuntuLog.info('TIME user packages:' + str(end - start))    
    
        #disable password login via ssh
        os.system('sed -i \'s/PasswordAuthentication yes/PasswordAuthentication no/g\' ' + tempdir + '' + name + '/etc/ssh/sshd_config')
        os.system('echo \"PasswordAuthentication no\" | tee -a ' + tempdir + '' + name + '/etc/ssh/sshd_config > /dev/null')
        os.system('sed -i \'s/StrictHostKeyChecking ask/StrictHostKeyChecking no/g\' ' + tempdir + '' + name + '/etc/ssh/ssh_config')
        os.system('echo \"StrictHostKeyChecking no\" | tee -a ' + tempdir + '' + name + '/etc/ssh/ssh_config > /dev/null')
            
    
    os.system('rm -f ' + tempdir + '' + name + '/usr/sbin/policy-rc.d')

    cleanup(name)

    return name

def buildDebian(name, version, arch, pkgs, tempdir):


    namedir = name
    runCmd('')


def buildRHEL(name, version, arch, pkgs, tempdir):

    namedir = name
    runCmd('')


def buildCentos(name, version, arch, pkgs, tempdir, base_os):
    
    
    output = ""
    namedir = name

    centosLog = logging.getLogger('GenerateScript.centos')
    runCmd('mkdir ' + tempdir + '' + name)
    if not base_os:
        centosLog.info('Procesing Image: centos-' + version + '-' + arch + '-base.img')
        
        handleBaseImage(tempdir, name)
        
    elif base_os:
        centosLog.info('Generation Image: centos-' + version + '-' + arch + '-base.img')

        #to create base_os    
        centosLog.info('Creating Disk for the image')        
        createBaseImageDisk(tempdir, name)    
    
    #The image is mounted

    if base_os:
        #to create base_os
        centosLog.info('Create directories image')
        runCmd('mkdir -p ' + tempdir + '' + name + '/var/lib/rpm ' + tempdir + '' + name + '/var/log ' + tempdir + '' + name + '/dev/pts ' + tempdir + '' + name + '/dev/shm')
        runCmd('touch ' + tempdir + '' + name + '/var/log/yum.log')

        #to create base_os
        centosLog.info('Getting appropiate release package')
        if (version == "5"):
            #runCmd('wget http://mirror.centos.org/centos/5/os/x86_64/CentOS/centos-release-5-7.el5.centos.x86_64.rpm -O /tmp/centos-release.rpm')
            runCmd('wget ' + http_server + '/conf/centos/centos-release-5.rpm -O /tmp/centos-release.rpm')
                        
        elif(version == "6"): #the 5.5 is not supported yet
            #runCmd('wget http://mirror.centos.org/centos/6/os/x86_64/Packages/centos-release-6-2.el6.centos.7.x86_64.rpm -O /tmp/centos-release.rpm')            
            runCmd('wget ' + http_server + '/conf/centos/centos-release-6.rpm -O /tmp/centos-release.rpm')
        runCmd('rpm -ihv --nodeps --root ' + tempdir + '' + name + ' /tmp/centos-release.rpm')
        runCmd('rm -f /tmp/centos-release.rpm')
        
        #to create base_os        
        centosLog.info('Installing base OS')
        start = time.time()
        runCmd('yum --installroot=' + tempdir + '' + name + ' -y groupinstall Core')
        #runCmd('yum -c ./yum.conf --installroot=' + tempdir + '' + name + ' -y groupinstall Core')
        end = time.time()
        centosLog.info('TIME base OS:' + str(end - start))
        
        centosLog.info('Copying configuration files')

#Move next 3 to deploy        
        os.system('echo "search idpm" > ' + tempdir + '' + name + '/etc/resolv.conf')
        os.system('echo "nameserver 129.79.1.1" >> ' + tempdir + '' + name + '/etc/resolv.conf')
        os.system('echo "nameserver 172.29.202.149" >> ' + tempdir + '' + name + '/etc/resolv.conf')

        runCmd('cp /etc/sysconfig/network ' + tempdir + '' + name + '/etc/sysconfig/')

        os.system('echo "127.0.0.1 localhost.localdomain localhost" > ' + tempdir + '' + name + '/etc/hosts')
        
        os.system('mkdir -p ' + tempdir + '' + name + "/root/.ssh")
        
        #Mount proc and pts
        runCmd('mount --bind /proc ' + tempdir + '' + name + '/proc')
        runCmd('mount --bind /dev ' + tempdir + '' + name + '/dev')
        centosLog.info('Mounted proc and dev')
    
        centosLog.info('Installing some util packages')
        #if not os.path.isfile(tempdir + '' + name +"/proc/cpuinfo"):
        #    os.system("touch "+ tempdir + '' + name +"/proc/cpuinfo")
        #runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' yum clean all')
        start = time.time()
        if (re.search("^5", version)):
            #runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' rpm -ivh http://download.fedora.redhat.com/pub/epel/5/' + arch + '/epel-release-5-4.noarch.rpm')        
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' rpm -ivh ' + http_server + '/conf/centos/epel-release-5-4.noarch.rpm')
            runCmd('wget ' + http_server + '/inca_conf/fgperf.repo_centos5 -O ' + tempdir + '' + name + '/etc/yum.repos.d/fgperf.repo')
        elif (re.search("^6", version)):
            #runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' rpm -ivh http://download.fedora.redhat.com/pub/epel/6/' + arch + '/epel-release-6-5.noarch.rpm')
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' rpm -ivh ' + http_server + '/conf/centos/epel-release-6-5.noarch.rpm')
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' yum -y install plymouth openssh-clients') 
    
        runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' yum -y install wget nfs-utils gcc make man curl time')
       
        end = time.time()
        centosLog.info('TIME util packages:' + str(end - start))
        
        #Setup networking    
        runCmd('wget ' + http_server + '/conf/centos/ifcfg-eth0 -O ' + tempdir + '' + name + '/etc/sysconfig/network-scripts/ifcfg-eth0')    
        centosLog.info('Injected generic networking configuration')
        #base_os done

    if not onlybaseimage:
        if not base_os:
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + " rm -f /etc/mtab~*  /etc/mtab.tmp")
            #Mount proc and pts
            runCmd('mount --bind /proc ' + tempdir + '' + name + '/proc')
            runCmd('mount --bind /dev ' + tempdir + '' + name + '/dev')
            
            centosLog.info('Mounted proc and dev')
    
        start = time.time()
        #Install packages
        if pkgs != None:
            centosLog.info('Installing user-defined packages')
            runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' yum -y install ' + pkgs)
            
            centosLog.info('Installed user-defined packages')
    
        end = time.time()
        centosLog.info('TIME user packages:' + str(end - start))
    
        #disable password login via ssh
        os.system('sed -i \'s/PasswordAuthentication yes/PasswordAuthentication no/g\' ' + tempdir + '' + name + '/etc/ssh/sshd_config')
        os.system('echo \"PasswordAuthentication no\" | tee -a ' + tempdir + '' + name + '/etc/ssh/sshd_config > /dev/null')
        if os.path.isfile(tempdir + '' + name + '/etc/ssh/ssh_config'):
            os.system('sed -i \'s/StrictHostKeyChecking ask/StrictHostKeyChecking no/g\' ' + tempdir + '' + name + '/etc/ssh/ssh_config')
        os.system('echo \"StrictHostKeyChecking no\" | tee -a ' + tempdir + '' + name + '/etc/ssh/ssh_config > /dev/null')
        os.system('sed -i \'s/enforcing/disabled/g\' ' + tempdir + '' + name + '/etc/selinux/config')
        #create /etc/shadow file
        #runCmd('/usr/sbin/chroot ' + tempdir + '' + name + ' pwconv')
           
    cleanup(name)

    return name


def buildFedora(name, version, arch, pkgs, tempdir):

    runCmd('')


def runCmd(cmd):
    cmdLog = logging.getLogger('GenerateScript.exec')
    cmdLog.debug(cmd)

    #os.system(cmd)
    #Use subprocess to properly direct output to log
    #p = subprocess.Popen(cmd, shell=True)    
    p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    std = p.communicate()    
    if len(std[0]) > 0:
        cmdLog.debug('stdout: ' + std[0])
    #cmdLog.debug('stderr: '+std[1])

    #cmdLog.debug('Ret status: '+str(p.returncode))
    if p.returncode != 0:
        cmdLog.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])        
        cleanup(namedir)        
        cmd = "rm -f " + tempdir + '' + namedir + ".img"
        cmdLog.debug('Executing: ' + cmd)
        os.system(cmd)
        print "error"
        print str(p.returncode) + '---' + std[1]
        sys.exit(p.returncode)



def cleanup(name):
    #Cleanup
    cleanupLog = logging.getLogger('GenerateScript.cleanup')
    if (name.strip() != ""):
        os.system('umount ' + tempdir + '' + name + '/proc')
        os.system('umount ' + tempdir + '' + name + '/dev')

        cmd = 'umount ' + tempdir + '' + name
        cleanupLog.debug('Executing: ' + cmd)
        stat = os.system(cmd)

        if (stat == 0):
            cmd = "rm -rf " + tempdir + '' + name
            cleanupLog.debug('Executing: ' + cmd)
            os.system(cmd)
    else:
        cleanupLog.error("error in clean up")

    cleanupLog.debug('Cleaned up mount points')
    time.sleep(10)

def manifest(user, name, os, version, arch, pkgs, givenname, description, tempdir):

    manifestLog = logging.getLogger('GenerateScript.manifest')

    manifest = Document()

    head = manifest.createElement('manifest')
    manifest.appendChild(head)

    userNode = manifest.createElement('user')
    userVal = manifest.createTextNode(user)
    userNode.appendChild(userVal)
    head.appendChild(userNode)

    imgNameNode = manifest.createElement('name')
    imgNameVal = manifest.createTextNode(name)
    imgNameNode.appendChild(imgNameVal)
    head.appendChild(imgNameNode)

    imgGivenNameNode = manifest.createElement('givenname')
    imgGivenNameVal = manifest.createTextNode(givenname)
    imgGivenNameNode.appendChild(imgGivenNameVal)
    head.appendChild(imgGivenNameNode)

    descNode = manifest.createElement('description')
    descVal = manifest.createTextNode(description)
    descNode.appendChild(descVal)
    head.appendChild(descNode)

    osNode = manifest.createElement('os')
    osNodeVal = manifest.createTextNode(os)
    osNode.appendChild(osNodeVal)
    head.appendChild(osNode)

    versionNode = manifest.createElement('version')
    versionNodeVal = manifest.createTextNode(version)
    versionNode.appendChild(versionNodeVal)
    head.appendChild(versionNode)

    archNode = manifest.createElement('arch')
    archNodeVal = manifest.createTextNode(arch)
    archNode.appendChild(archNodeVal)
    head.appendChild(archNode)

    #kernelNode = manifest.createElement('kernel')
    #kernelNodeVal = manifest.createTextNode(kernel)
    #kernelNode.appendChild(kernelNodeVal)
    #head.appendChild(kernelNode)

    packagesNode = manifest.createElement('packages')
    packages = pkgs.split(' ')
    for p in packages:
        packageNode = manifest.createElement('package')
        packageNodeVal = manifest.createTextNode(p)
        packageNode.appendChild(packageNodeVal)
        packagesNode.appendChild(packageNode)

    head.appendChild(packagesNode)

    filename = '' + tempdir + '' + name + '.manifest.xml'
    file = open(filename, 'w')
    #Document.PrettyPrint(manifest, file)
    #manifest.writexml(file, indent='    ', addindent='    ', newl='\n')

    output = manifest.toprettyxml()
    file.write(output)
    file.close()
    manifestLog.info('Genereated manifest file: ' + filename)

def push_bcfg2_group(name, pkgs, os, version):
    #Push the group information to the BCFG2 server via a socket connection

    bcfg2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bcfg2.connect((bcfg2_url, bcfg2_port))

    success = True

    #Send group name
    bcfg2.send(name)
    ret = bcfg2.recv(100)
    if ret != 'OK':
        logger.error('Incorrect reply from the server:' + ret)
        success = False
    else:
        #Send OS 
        bcfg2.send(os)
        ret = bcfg2.recv(100)
        if ret != 'OK':
            logger.error('Incorrect reply from the server:' + ret)
            success = False
        else:
            #Send OS Version
            bcfg2.send(version)
            ret = bcfg2.recv(100)
            if ret != 'OK':
                logger.error('Incorrect reply from the server:' + ret)
                success = False
            else:
                #Send package information
                bcfg2.send(pkgs)
                ret = bcfg2.recv(100)
                if ret != 'OK':
                    logger.error('Incorrect reply from the server:' + ret)
                    success = False

    return success



if __name__ == "__main__":
    main()
#END





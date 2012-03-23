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
Client of the FG RAIN
"""
__author__ = 'Javier Diaz'

import argparse
from types import *
import re
import logging
import logging.handlers
import glob
import random
from random import randrange
import os
import sys
import socket, ssl
from subprocess import *
from getpass import getpass
import hashlib
import time
import boto.ec2
import boto
from multiprocessing import Process
from pprint import pprint

from futuregrid.rain.RainClientConf import RainClientConf
from futuregrid.image.management.IMRegister import IMRegister 
from futuregrid.utils import fgLog

class RainClient(object):

    #(Now we assume that the server is where the images are stored. We may want to change that)    
    ############################################################
    # __init__
    ############################################################
    def __init__(self, user, verbose, printLogStdout):
        super(RainClient, self).__init__()
        
        self.user = user
        self.verbose = verbose
        self.printLogStdout = printLogStdout
        self.private_ips_for_hostlist=""
        
        self._rainConf = RainClientConf()
        self._log = fgLog.fgLog(self._rainConf.getLogFile(), self._rainConf.getLogLevel(), "RainClient", printLogStdout)
        self.refresh = self._rainConf.getRefresh()
        self.moab_max_wait = self._rainConf.getMoabMaxWait()
        self.moab_images_file = self._rainConf.getMoabImagesFile()
    
    def setDebug(self, printLogStdout):
        self.printLogStdout = printLogStdout
      
    def baremetal(self, imageidonsystem, jobscript, machines, walltime):
        self._log.info('Starting Rain Client Baremetal')
        start_all = time.time()
        if imageidonsystem != "default":
            #verify that the image requested is in Moab
            imagefoundinfile = False
            if not imagefoundinfile:
                f = open(self.moab_images_file, 'r')
                for i in f:
                    if re.search(imageidonsystem, i):
                        imagefoundinfile = True
                        break
                f.close()
                if not imagefoundinfile:
                    return "ERROR: The image is not registered on xCAT/Moab"
        
        if jobscript != None: # Non Interactive. So read jobscript file
            #read the output file and the error one to print it out to the user.
            std = []
            f = open(jobscript, 'r')
            #PBS -e stderr.txt
            #PBS -o stdout.txt
            stdoutfound = False
            stderrfound = False        
            stdout = ""
            stderr = ""
            jobname = ""
            for i in f:
                if re.search('^#PBS -e', i):
                    stderrfound = True
                    stderr = os.path.expandvars(os.path.expanduser(i.split()[2]))                    
                elif re.search('^#PBS -o', i):
                    stdoutfound = True
                    stdout = os.path.expandvars(os.path.expanduser(i.split()[2]))
                elif re.search('^#PBS -N', i):                
                    jobname = os.path.expandvars(os.path.expanduser(i.split()[2]))            
                elif not re.search('^#', i):
                    break                      
                if stderrfound and stdoutfound:
                    break
            f.close()
            
        #execute qsub
        cmd = "qsub "
        if machines >= 1:
            cmd += "-l nodes=" + str(machines)
        if imageidonsystem != "default":
            cmd += " -l os=" + imageidonsystem
        if walltime != None:
            cmd += " -l walltime=" + str(walltime)
        if jobscript != None:
            cmd += " " + jobscript
        else:
            cmd += " -I"
        
        
        
        self._log.debug(cmd)
        
        tryagain = True
        retry = 0
        maxretry = self.moab_max_wait / 5
        if jobscript != None:
            try:
                while tryagain:                
                    p_qsub = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                    std_qsub = p_qsub.communicate()
                    if p_qsub.returncode != 0:
                        if not re.search("cannot set req attribute \'OperatingSystem\'", std_qsub[1]) and not re.search('no service listening', std_qsub[1]):                    
                            self._log.debug(std_qsub[1])
                            if self.verbose:
                                print std_qsub[1]
                            return "ERROR in qsub: " + std_qsub[1]
                        if retry >= maxretry:
                            tryagain = False
                            self._log.debug(std_qsub[1])
                            if self.verbose:
                                print std_qsub[1]
                            return "ERROR in qsub: " + std_qsub[1] + " \n The image is not available on Moab (timeout). Try again later."
                        else:
                            retry += 1
                            time.sleep(5)
                    else:
                        tryagain = False
                        if jobscript != None:
                            jobid = std_qsub[0].strip().split(".")[0]
                            if self.verbose:
                                print "Job id is: " + jobid            
            except:
                self._log.error("ERROR: qsub command failed. Executed command: \"" + cmd + "\" --- Exception: " + str(sys.exc_info()))
                return "ERROR: qsub command failed. Executed command: \"" + cmd + "\" --- Exception: " + str(sys.exc_info())
        else:
            os.system(cmd)
        
        if retry >= maxretry:
            return "ERROR in qsub. " + std_qsub[1]
            
            
        if jobscript != None: #Non Interactive    
            if stdoutfound == False:
                if jobname != "":
                    stdout = jobname + ".o" + jobid
                else:
                    stdout = jobscript + ".o" + jobid
            if stderrfound == False:
                if jobname != "":
                    stderr = jobname + ".o" + jobid
                else:
                    stderr = jobscript + ".e" + jobid
            
            time.sleep(2)          
            #execute checkjob checking Status until complete or fail
            cmd = "checkjob " + jobid
            alive = True
            status = 0
            state = ""
            lines = []
            if self.verbose:
                print "Wait until the job finishes"
            while alive:            
                p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                std = p.communicate()
                lines = std[0].split('\n')
                if p.returncode != 0:
                    self._log.debug(std[1])
                    if self.verbose:
                        print std[1]                
                    status = 1
                    alive = False
                else:
                    for i in lines:
                        if re.search("^State:", i.strip()):                        
                            state = i.strip().split(":")[1].strip()
                            if self.verbose:
                                print "State: " + state
                            break
                    if state == "Completed" or state == "Removed":
                        alive = False
                    else:
                        time.sleep(self.refresh)
            completion = ""
            for i in lines:
                if re.search("^Completion Code:", i.strip()):                        
                    completion = i.strip()                    
                    break
            
            if self.verbose:
                print completion
                print "The Standard output is in the file: " + stdout
                print "The Error output is in the file: " + stderr                
                   
            
            
        end_all = time.time()
        self._log.info('TIME walltime rain client baremetal(xCAT):' + str(end_all - start_all))        
        self._log.info('Rain Client Baremetal DONE')
            
    #2. in the case of euca-run-instance, wait until the vms are booted, execute the job inside, wait until done.
    def euca(self, iaas_address, imageidonsystem, jobscript, ninstances, varfile):
        self._log.info('Starting Rain Client Eucalyptus')  
        start_all = time.time()
        
        euca_key_dir = os.path.dirname(varfile)            
        if euca_key_dir.strip() == "":
            euca_key_dir = "."
        os.environ["EUCA_KEY_DIR"] = euca_key_dir
                    
        #read variables
        f = open(varfile, 'r')
        for line in f:
            if re.search("^export ", line):
                line = line.split()[1]                    
                parts = line.split("=")
                #parts[0] is the variable name
                #parts[1] is the value
                parts[0] = parts[0].strip()
                value = ""
                for i in range(1, len(parts)):
                    parts[i] = parts[i].strip()
                    parts[i] = os.path.expanduser(os.path.expandvars(parts[i]))                    
                    value += parts[i] + "="
                value = value.rstrip("=")
                value = value.strip('"')
                value = value.strip("'") 
                os.environ[parts[0]] = value
        f.close()
            
        if iaas_address != None:
            ec2_url = "http://" + iaas_address + "/services/Eucalyptus"
            s3_url = "http://" + iaas_address + "/services/Walrus"
        else:
            ec2_url = os.getenv("EC2_URL")
            s3_url = os.getenv("S3_URL")
        
        path = "/services/Eucalyptus"
        region = "eucalyptus"
        
        output = self.ec2_common("euca", path, region, ec2_url, imageidonsystem, jobscript, ninstances, varfile)
        
        end_all = time.time()
        self._log.info('TIME walltime rain client Eucalyptus:' + str(end_all - start_all))
        self._log.info('Rain Client Eucalyptus DONE')
        return output
        
    def openstack(self, iaas_address, imageidonsystem, jobscript, ninstances, varfile):
        """
        imageidonsystem = id of the image
        jobscript = path of the script to execute machines
        varfile = openstack variable files(novarc typically)
        key_pair = ssh key file. this must be registered on openstack. The name in openstack is os.path.basename(key_pair).strip('.')[0]
        ninstances = number of instances
        """
        self._log.info('Starting Rain Client OpenStack')     
        start_all = time.time()
        nova_key_dir = os.path.dirname(varfile)            
        if nova_key_dir.strip() == "":
            nova_key_dir = "."
        os.environ["NOVA_KEY_DIR"] = nova_key_dir
                    
        #read variables
        f = open(varfile, 'r')
        for line in f:
            if re.search("^export ", line):
                line = line.split()[1]                    
                parts = line.split("=")
                #parts[0] is the variable name
                #parts[1] is the value
                parts[0] = parts[0].strip()
                value = ""
                for i in range(1, len(parts)):
                    parts[i] = parts[i].strip()
                    parts[i] = os.path.expanduser(os.path.expandvars(parts[i]))                    
                    value += parts[i] + "="
                value = value.rstrip("=")
                value = value.strip('"')
                value = value.strip("'") 
                os.environ[parts[0]] = value
        f.close()
        
        if iaas_address != None:
            ec2_url = "http://" + iaas_address + "/services/Cloud"
            s3_url = "http://" + iaas_address + ":3333"
        else:
            ec2_url = os.getenv("EC2_URL")
            s3_url = os.getenv("S3_URL")
        
        path = "/services/Cloud"
        region = "nova"
        
        output = self.ec2_common("openstack", path, region, ec2_url, imageidonsystem, jobscript, ninstances, varfile)
        
        end_all = time.time()
        self._log.info('TIME walltime rain client OpenStack:' + str(end_all - start_all))   
        self._log.info('Rain Client OpenStack DONE')
        return output
        
        
    def ec2_common(self, iaas_name, path, region, ec2_url, imageidonsystem, jobscript, ninstances, varfile):
        
        #TODO: GVL: configutartion file? 
        india_loginnode = "149.165.146.136" #to mount the home using sshfs
        endpoint = ec2_url.lstrip("http://").split(":")[0]
        
        #TODO: GVL: configutartion file? 
        #Home from login node will be in /tmp/N/u/username
        if jobscript != None:
            if re.search("^/N/u/", jobscript):
                jobscript = "/tmp" + jobscript        
        
        try:  
            region = boto.ec2.regioninfo.RegionInfo(name=region, endpoint=endpoint)
        except:
            msg = "ERROR: getting region information " + str(sys.exc_info())
            self._log.error(msg)                        
            return msg
        try:
            connection = boto.connect_ec2(str(os.getenv("EC2_ACCESS_KEY")), str(os.getenv("EC2_SECRET_KEY")), is_secure=False, region=region, port=8773, path=path)
        except:
            msg = "ERROR:connecting to EC2 interface. " + str(sys.exc_info())
            self._log.error(msg)                        
            return msg
        
        self.wait_available(connection, imageidonsystem)
        
        sshkeypair_name = str(randrange(999999999))
                
        ssh_key_pair = None
        msg = "Creating temportal sshkey pair for EC2"
        self._log.debug(msg)
        if self.verbose:
            print msg
        try:
            ssh_key_pair = connection.create_key_pair(sshkeypair_name)
        except:
            msg = "ERROR: creating key_pair " + str(sys.exc_info())
            self._log.error(msg)
            return msg
        sshkeypair_path = os.path.expanduser("~/") + sshkeypair_name + ".pem"
        msg = "Save private sshkey into a file"
        self._log.debug(msg)
        if self.verbose:
            print msg
        try:
            if not ssh_key_pair.save(os.path.expanduser("~/")):
                msg = "ERROR: saving key_pair to a file"
                self._log.error(msg)
                return msg
            else:
                os.system("chmod 600 " + sshkeypair_path)
        except:
            msg = "ERROR: saving key_pair " + str(sys.exc_info())
            self._log.error(msg)
            connection.delete_key_pair(sshkeypair_name)            
            return msg
            
        #Check that key_pair without .pem and path is in openstack
        #check that key_pairis exists. this may be done outside in argparse
        image = None
        try:
            image = connection.get_image(imageidonsystem)
            #print image.location
        except:
            msg = "ERROR: getting the image " + str(sys.exc_info())
            self._log.error(msg)
            self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
            return msg

        start = time.time()

        reservation = None
        msg = "Launching image"
        self._log.debug(msg)
        if self.verbose:
            print msg
        try:
            reservation = image.run(ninstances, ninstances, sshkeypair_name)            
        except:
            msg = "ERROR: launching the VM " + str(sys.exc_info())
            self._log.error(msg)
            self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
            return msg
                
        #do a for to control status of all instances
        msg = "Waiting for running state in all the VMs"
        self._log.debug(msg)
        if self.verbose:
            print msg
        allrunning = False
        failed = False
        while not allrunning:
            running = 0        
            for i in reservation.instances:
                status = i.update()
                if self.verbose:
                    print str(str(i.id)) + ":" + status
                if status == 'running':
                    running += 1                    
                elif status == 'shutdown' or status == 'terminate' or status == 'terminated':
                    allrunning = True
                    failed = True
            if self.verbose:
                print "-------------------------"                    
            if (running == len(reservation.instances)):
                allrunning = True
            else:
                time.sleep(5)
        
        end = time.time()
        if not failed and allrunning:
            self._log.info('TIME Boot all Images:' + str(end - start))
        else:
            self._log.info('TIME Not all Images booted:' + str(end - start))
        
        print "Number of instances booted " + str(len(reservation.instances))
                  
        if not failed and allrunning:
            
            if iaas_name == "openstack":  
                #asignar ips. this should be skipped once the new openstack is registered
                #I do not do any verification because this has to disappear. Openstack has to assign the IP automatically
                start = time.time()       
                for i in reservation.instances:
                    cmd = "euca-describe-addresses -a " + os.getenv("EC2_ACCESS_KEY") + " -s " + os.getenv("EC2_SECRET_KEY") + " --url " + ec2_url
                    #print cmd
                    p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
                    
                    cmd = "awk /None/ && /" + os.getenv("EC2_ACCESS_KEY").split(":")[1].strip("\"") + "/ {print $2}"
                    p1 = Popen(cmd.split(' ', 1), stdin=p.stdout, stdout=PIPE, stderr=PIPE)
                    cmd = "sort"
                    p2 = Popen(cmd.split(' '), stdin=p1.stdout, stdout=PIPE, stderr=PIPE) 
                    cmd = "head -n1"
                    p3 = Popen(cmd.split(' '), stdin=p2.stdout, stdout=PIPE, stderr=PIPE)
                    std = p3.communicate()
                                    
                    if (p3.returncode == 0):
                        try:                  
                            connection.associate_address(str(i.id), std[0].strip('\n'))                    
                            msg = "Instance " + str(i.id) + " associated with address " + std[0].strip('\n')
                            self._log.debug("Instance " + str(i.id) + " associated with address " + std[0].strip('\n'))
                            if self.verbose:
                                print msg
                            time.sleep(1)
                            i.update()
                            
                        except:
                            msg = "ERROR: associating address to instance " + str(i.id) + ". failed, status: " + str(p3.returncode) + " --- " + std[1]
                            self._log.error(msg)
                            self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
                            self.stopEC2instances(connection, reservation)
                            return msg
                    else:                    
                        msg = "ERROR: associating address to instance " + str(i.id) + ". failed, status: " + str(p3.returncode) + " --- " + std[1]
                        self._log.error(msg)
                        self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
                        self.stopEC2instances(connection, reservation)
                        return msg
            
                end = time.time()
                self._log.info('TIME to associate all addresses:' + str(end - start))
            
            #boto.ec2.instance.Instance.dns_name to get the public IP.
            #boto.ec2.instance.Instance.private_dns_name private IP.
            start = time.time()                                          
            self._log.debug("Waiting to have access to VMs")
            allaccessible=self.wait_allaccesible(reservation, sshkeypair_path)
            
            msg = "All VMs are accessible: " + str(allaccessible)
            self._log.debug(msg)
            if self.verbose:
                print msg 
            
            end = time.time()
            self._log.info('TIME all VM are accessible via ssh:' + str(end - start))
            
            if allaccessible:
                start = time.time()
                msg = "Creating temporal sshkey files"
                self._log.debug(msg)
                if self.verbose:
                    print msg      
                sshkey_name = str(randrange(999999999))        
                sshkeytemp = os.path.expanduser("~/") + sshkey_name                
                cmd = "ssh-keygen -N \"\" -f " + sshkeytemp + " -C " + sshkey_name + " >/dev/null"
                status = os.system(cmd)                
                os.system("cat " + sshkeytemp + ".pub >> ~/.ssh/authorized_keys")
                
                
                f = open(sshkeytemp + ".machines", "w")
                f.write(self.private_ips_for_hostlist)
                f.close()
                
                #create script
                f = open(sshkeytemp + ".sh", "w")
                f.write("#!/bin/bash \n mkdir -p /N/u/" + self.user + "/.ssh /tmp/N/u/" + self.user +                        
                        "\n cp -f /tmp/" + sshkey_name + " /N/u/" + self.user + "/.ssh/id_rsa" + 
                        "\n cp -f /tmp/" + sshkey_name + ".pub /N/u/" + self.user + "/.ssh/id_rsa.pub" + 
                        "\n cp -f /tmp/authorized_keys /N/u/" + self.user + "/.ssh/" + 
                        "\n chmod 600 /N/u/" + self.user + "/.ssh/authorized_keys" + 
                        "\n cp -f /tmp/" + sshkey_name + ".machines /N/u/" + self.user + "/machines" +
                        "\n cp -f /tmp/" + sshkey_name + ".machines /root/machines" + 
                        "\n touch /N/u/" + self.user + "/your_home_is_in_tmp" + 
                        "\n echo \"Host *\" | tee -a /N/u/" + self.user + "/.ssh/config > /dev/null" + 
                        "\n echo \"    StrictHostKeyChecking no\" | tee -a /N/u/" + self.user + "/.ssh/config > /dev/null" + 
                        "\n echo \"cd /tmp/N/u/" + self.user + "\" | tee -a /N/u/" + self.user + "/.bash_profile > /dev/null" + 
                        "\n chown -R " + self.user + ":users /tmp/N/u/" + self.user + " /N/u/" + self.user +
                        "\n hostname `ifconfig eth0 | grep 'inet addr:' | cut -d\":\" -f2 | cut -d\" \" -f1`")
                #f.write("""
                #if [ -f /usr/bin/yum ]; 
                #then 
                #    yum -y install fuse-sshfs
                #elif [ -f /usr/bin/apt-get ];
                #then
                #    apt-get -y install sshfs
                #else
                #    exit 1
                #fi
                #""")
                f.write("\n usermod -a -G fuse " + self.user + "\n")
                f.write("su - " + self.user + " -c \"cd /tmp; sshfs " + self.user + "@" + india_loginnode + ":/N/u/" + self.user + \
                         " /tmp/N/u/" + self.user + " -o nonempty -o ssh_command=\'ssh -oStrictHostKeyChecking=no\'\" \n")                
                #f.write("ln -s /tmp/" + self.user + " /N/u/" + self.user)        
                f.close()
                os.system("chmod +x " + sshkeytemp + ".sh")
         
                
                #Make this parallel
                proc_list = []
                ndone = 0
                alldone = False
                for i in reservation.instances:      
                    output = self.install_sshfs_home(sshkeypair_path, sshkeypair_name, sshkey_name, sshkeytemp, reservation, connection, i)
                    if output != "OK":
                        return output              
                    #proc_list.append(Process(target=self.install_sshfs_home, args=(sshkeypair_path, sshkeypair_name, sshkey_name, sshkeytemp, reservation, connection, i,)))                                
                    #proc_list[len(proc_list) - 1].start()
                                        
                #if some process fails inside install_sshfs_home, all will die because the VM are terminated
                #wait to finish processes
                #teminate = False
                #for i in range(len(proc_list)):
                #    if not terminate:
                #        proc_list[i].join()
                #    else:
                #        proc_list[i].terminate() 
                #    if proc_list[i].exitcode == 0:
                #        ndone += 1
                #    else:
                #        terminate = True                        
                    
                
                #if ndone == len(reservation.instances):
                #    alldone = True                
            
                #msg = "All VMs done: " + str(alldone)
                #self._log.debug(msg)
                #if self.verbose:
                #     print msg 
                   
                end = time.time()
                self._log.info('TIME configure and mount home directory (using sshfs) in /tmp in all VMs:' + str(end - start))
             
                #if alldone:
                start = time.time()
                msg = "Running Job"
                self._log.debug(msg)
                if self.verbose:
                    print msg
                #runjob 
                p=None
                if jobscript != None:                
                    cmd = "ssh -oBatchMode=yes -oStrictHostKeyChecking=no " + str(reservation.instances[0].public_dns_name) + " " + jobscript 
                    self._log.debug(cmd) 
                    p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                else:
                    if self.verbose:
                        print "You are going to be logged as root, but you can change to your user by executing su - <username>"
                        print "List of machines are in /root/machines and /N/u/<username>/machines. Your real home is in /tmp/N/u/<username>"
                    cmd = "ssh -oStrictHostKeyChecking=no -i " + sshkeypair_path + " root@" +str(reservation.instances[0].public_dns_name)  
                    self._log.debug(cmd)
                    p = Popen(cmd.split(), stderr=PIPE)
                std = p.communicate()
                if p.returncode != 0:
                    msg = "ERROR: Running job. " + str(reservation.instances[0].id) + ". failed, status: " + str(p.returncode) + " --- " + std[1]
                    self._log.error(msg)
                    self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
                    self.stopEC2instances(connection, reservation)
                    self.removeTempsshkey(sshkeytemp, sshkey_name)
                    return msg
                end = time.time()
                self._log.info('TIME run job:' + str(end - start))
                                    
                msg = "Job Done"
                self._log.debug(msg)
                if self.verbose:
                    print msg 
            self.removeTempsshkey(sshkeytemp, sshkey_name)
            
        self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)                
        self.stopEC2instances(connection, reservation)
        
    
    def wait_allaccesible(self,reservation, sshkeypair_path):
        allaccessible = False
        naccessible = 0
        self.private_ips_for_hostlist=""
        for i in reservation.instances:                
            access = False
            maxretry = 240  #this says that we wait 20 minutes maximum to allow the VM get online. 
            #this also prevent to get here forever if the ssh key was not injected propertly.
            retry = 0
            
            #print "Instance properties"
            #pprint (vars(i))
            #print "end instance properties"
            if self.verbose:
                msg = "Waiting to have access to Instance " + str(i.id) + " associated with address " + str(i.public_dns_name)
                print msg
            
            while not access and retry < maxretry:                
                cmd = "ssh -i " + sshkeypair_path + " -q -oBatchMode=yes root@" + str(i.public_dns_name) + " uname"                    
                p = Popen(cmd, shell=True, stdout=PIPE)
                status = os.waitpid(p.pid, 0)[1]
                #print status                  
                if status == 0:
                    access = True
                    naccessible += 1
                    self._log.debug("The instance " + str(str(i.id)) + " with public ip " + str(i.public_dns_name) + " and private ip " + str(i.private_dns_name) + " is accessible")
                    self.private_ips_for_hostlist += str(i.private_dns_name) + "\n"
                    #Later add parameter for number of process per machines. So, we duplicate this entry x times
                else:
                    retry += 1
                    time.sleep(5)
                    
            if retry >= maxretry:
                self._log.error("Could not get access to the instance " + str(str(i.id)) + " with public ip " + str(i.public_dns_name) + " and private ip " + str(i.private_dns_name) + "\n")                                      
                allaccessible = False
                break
            
        if naccessible == len(reservation.instances):
            allaccessible = True
            
        return allaccessible
    
    def wait_available(self, connection, imageId):
        #Verify that the image is in available status        
        start = time.time()
        available = False
        retry = 0
        fails = 0
        max_retry = 100 #wait around 15 minutes. plus the time it takes to execute the command, that in openstack can be several seconds 
        max_fails = 5
        stat = 0
        if self.verbose:
            print "Verify that the requested image is in available status or wait until it is available"
        
        while not available and retry < max_retry and fails < max_fails:
            
            try:
                image = connection.get_image(imageId)
                if str(image.state) == "available":
                    available = True
                else:
                    retry +=1
                    time.sleep(10)                
            except:
                fails+=1
            
        if stat == 1:
            msg = "ERROR: checking image status"
            self._log.error(msg)            
            return msg
        elif not available:
            msg = "ERROR: Timeout, image is not in available status"
            self._log.error(msg)            
            return msg

        end = time.time()
        self._log.info('TIME Image available:' + str(end - start))    
       
    def install_sshfs_home(self, sshkeypair_path, sshkeypair_name, sshkey_name, sshkeytemp, reservation, connection, i): 
        
        msg = "Copying temporal private and public ssh-key files to VMs"
        self._log.debug(msg)
        if self.verbose:
            print msg 
        cmd = "scp -i " + sshkeypair_path + " -q -oBatchMode=yes -oStrictHostKeyChecking=no " + sshkeytemp + " " + sshkeytemp + ".pub " + \
             sshkeytemp + ".sh /N/u/" + self.user + "/.ssh/authorized_keys " + sshkeytemp + ".machines root@" + str(i.public_dns_name) + ":/tmp/" 
        self._log.debug(cmd)                    
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        std = p.communicate()
        if p.returncode != 0:
            msg = "ERROR: sending ssh-keys and script to VM " + str(i.id) + ". failed, status: " + str(p.returncode) + " --- " + std[1]
            self._log.error(msg)
            if self.verbose:
                print msg
            self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
            self.stopEC2instances(connection, reservation)
            self.removeTempsshkey(sshkeytemp, sshkey_name)
            return msg
        
        cmd = "scp -i " + sshkeypair_path + " " + sshkeypair_path + " root@" + str(i.public_dns_name) + ":/root/.ssh/id_rsa" 
        self._log.debug(cmd)
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        std = p.communicate()
        if p.returncode != 0:
            msg = "ERROR: sending ssh-key to /root/.ssh " + str(i.id) + ". failed, status: " + str(p.returncode) + " --- " + std[1]
            self._log.error(msg)
            if self.verbose:
                print msg
        
        msg = "Configuring ssh in VM and mounting home directory (assumes that sshfs and ldap is installed)"
        self._log.debug(msg)
        if self.verbose:
            print msg 
        
        cmd = "ssh -i " + sshkeypair_path + " -q -oBatchMode=yes -oStrictHostKeyChecking=no root@" + str(i.public_dns_name) + " /tmp/" + sshkey_name + ".sh"
        self._log.debug(cmd) 
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        std = p.communicate()
        if p.returncode != 0:
            msg = "ERROR: Installing sshfs and mounting home directory. " + str(i.id) + ". failed, status: " + str(p.returncode) + " --- " + std[1]
            self._log.error(msg)
            if self.verbose:
                print msg
            self.removeEC2sshkey(connection, sshkeypair_name, sshkeypair_path)
            self.stopEC2instances(connection, reservation)
            self.removeTempsshkey(sshkeytemp, sshkey_name)
            return msg
        return "OK"
        
    def removeTempsshkey(self, sshkeytemp, sshkey_name):
        cmd = "rm -f " + sshkeytemp + " " + sshkeytemp + ".pub " + sshkeytemp + ".sh " + sshkeytemp + ".machines"
        status = os.system(cmd)
        cmd = ('sed -i /\' ' + sshkey_name + '$\'/d ~/.ssh/authorized_keys')
        status = os.system(cmd)
    
    def removeEC2sshkey(self, connection, sshkeypair_name, sshkeypair_path):
        try:
            connection.delete_key_pair(sshkeypair_name)
            os.system("rm -f " + sshkeypair_path)
        except:
            msg = "ERROR: deleting temporal sshkey. " + str(sys.exc_info())
            self._log.error(msg)
        
        
    def stopEC2instances(self, connection, reservation):        
        try:
            regioninfo=str(connection.get_all_regions()[0]).split(":")[1]
            if regioninfo == 'Eucalyptus':
                for i in reservation.instances:
                    connection.terminate_instances([str(i).split(":")[1]])
            else:
                connection.terminate_instances(reservation.instances)
        except:
            msg = "ERROR: terminating VM. " + str(sys.exc_info())
            self._log.error(msg)
    
    def opennebula(self, imageidonsystem, jobscript, machines):
        print "in opennebula method.end"

    def nimbus(self, imageidonsystem, jobscript, machines, walltime):
        print "in nimbus method.end"
    
        
    """
    def runCmd(self, cmd, std):        
        self._log.debug(cmd)
        p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
        std = p.communicate()
        status = 0
        if len(std[0]) > 0:
            self._log.debug('stdout: ' + std[0])
            self._log.debug('stderr: ' + std[1])
        if p.returncode != 0:
            cmdLog.error('Command: ' + cmd + ' failed, status: ' + str(p.returncode) + ' --- ' + std[1])
            status = 1
            #sys.exit(p.returncode)
        return status
    """
#TODO: in the case of cloud registration, we need to configure ldap to allow users to login and run parallel jobs. For that we need to modify the registration iaas to include the code that does that.
def main():
 
    #TODO: GVL: maybe less long lines
    parser = argparse.ArgumentParser(prog="RainClient", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Rain Help ")    
    parser.add_argument('-u', '--user', dest='user', required=True, metavar='user', help='FutureGrid User name')
    parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
    parser.add_argument('-k', '--kernel', dest="kernel", metavar='Kernel version', help="Specify the desired kernel" 
                        "(must be exact version and approved for use within FG). Not yet supported")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--registeredimageid', dest='registeredimageid', metavar='ImgId', help='Id of the image in the target infrastructure. This assumes that the image'
                       ' is registered in the selected infrastructure.')
    group.add_argument('-r', '--imgid', dest='imgid', metavar='ImgId', help='Id of the image stored in the repository')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-x', '--xcat', dest='xcat', metavar='MachineName', help='Register image for HPC into xCAT. The argument is the machine name (minicluster, india ...)')
    group1.add_argument('-e', '--euca', dest='euca', nargs='?', metavar='Address:port', help='Register the image into Eucalyptus, which is in the specified addr')
    #group1.add_argument('-o', '--opennebula', dest='opennebula', nargs='?', metavar='Address', help='Register the image to OpenNebula, which is in the specified addr')
    #group1.add_argument('-n', '--nimbus', dest='nimbus', nargs='?', metavar='Address', help='Register the image to Nimbus, which is in the specified addr')
    group1.add_argument('-s', '--openstack', dest='openstack', nargs='?', metavar='Address', help='Register the image into OpenStack, which is in the specified addr')
    parser.add_argument('-v', '--varfile', dest='varfile', help='Path of the environment variable files. Currently this is used by Eucalyptus and OpenStack')
    parser.add_argument('-m', '--numberofmachines', dest='machines', metavar='#instances', default=1, help='Number of machines needed.')
    parser.add_argument('-w', '--walltime', dest='walltime', metavar='hours', help='How long to run (in hours). You may use decimals. This is used for HPC and Nimbus.')
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('-j', '--jobscript', dest='jobscript', help='Script to execute on the provisioned images. In the case of Cloud environments, '
                        ' the user home directory is mounted in /tmp/N/u/username. The /N/u/username is only used for ssh between VM and store the ips of the parallel '
                        ' job in a file called /N/u/username/machines')
    group2.add_argument('-I', '--interactive', nargs='?', default=1, dest='interactive', help='Interactive mode. This just boot VMs or provision bare-metal machines')
    
    
    args = parser.parse_args()

    #print args
    

    print 'Starting Rain...'
    
    verbose = True #to activate the print
    
    print "Please insert the password for the user " + args.user + ""
    m = hashlib.md5()
    m.update(getpass())
    passwd = m.hexdigest()

    #TODO: if Kernel is provided we need to verify that it is supported. 
    
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
        imgregister = IMRegister(args.kernel, args.user, passwd, verbose, args.debug)    
        #XCAT
        if args.xcat != None:
            if args.imgid == None:
                print "ERROR: You need to specify the id of the image that you want to register (-r/--imgid option)."
                print "The parameter -i/--image cannot be used with this type of registration"
                sys.exit(1)
            else:
                output = imgregister.xcat_method(args.xcat, args.imgid)
                time.sleep(3)
        else:
            ldap = True #we configure ldap to run commands and be able to login from on vm to other            
            #EUCALYPTUS    
            if ('-e' in used_args or '--euca' in used_args):                
                if varfile == "":
                    print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                elif not os.path.isfile(varfile):
                    print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
                else:    
                    output = imgregister.iaas_generic(args.euca, image, image_source, "euca", varfile, False, ldap, False)        
                    if output != None:
                        if re.search("^ERROR", output):
                            print output
            #OpenNebula
            elif ('-o' in used_args or '--opennebula' in used_args):
                output = imgregister.iaas_generic(args.opennebula, image, image_source, "opennebula", varfile, False, ldap, False)
            #NIMBUS
            elif ('-n' in used_args or '--nimbus' in used_args):
                #TODO        
                print "Nimbus registration is not implemented yet"
            elif ('-s' in used_args or '--openstack' in used_args):                
                if varfile == "":
                    print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                elif not os.path.isfile(varfile):
                    print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                else:    
                    output = imgregister.iaas_generic(args.openstack, image, image_source, "openstack", varfile, False, ldap, False)
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
                           
            rain = RainClient(args.user, verbose, args.debug)
            target = ""
            if args.xcat != None:
                if args.walltime != None:
                    walltime=int(walltime*3600)
                output = rain.baremetal(output, jobscript, args.machines, walltime)
                if output != None:
                    print output
            else:
                if ('-e' in used_args or '--euca' in used_args):
                    if varfile == "":
                        print "ERROR: You need to specify the path of the file with the Eucalyptus environment variables"
                    elif not os.path.isfile(varfile):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the Eucalyptus environment variables"
                    else:
                        output = rain.euca(args.euca, output, jobscript, args.machines, varfile)
                        if output != None:
                            print output
                elif ('-o' in used_args or '--opennebula' in used_args):
                    output = rain.opennebula(args.opennebula, output, jobscript, args.machines)
                elif ('-n' in used_args or '--nimbus' in used_args):
                    output = rain.nimbus(args.nimbus, output, jobscript, args.machines, walltime)                    
                elif ('-s' in used_args or '--openstack' in used_args):
                    if varfile == "":
                        print "ERROR: You need to specify the path of the file with the OpenStack environment variables"
                    elif not os.path.isfile(varfile):
                        print "ERROR: Variable files not found. You need to specify the path of the file with the OpenStack environment variables"
                    else:  
                        output = rain.openstack(args.openstack, output, jobscript, args.machines, varfile)
                        if output != None:
                            print output
                else:
                    print "ERROR: You need to specify a Rain target (xcat, eucalyptus or openstack)"
        
        
    else:
        print "ERROR: invalid image id."
    #call rain with the command
    

if __name__ == "__main__":
    main()
#END

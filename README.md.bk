
SEE: https://portal.futuregrid.org/manual/dev/soft-deploy

* https://portal.futuregrid.org/manual/dev/soft-deploy/fg-shell
* https://portal.futuregrid.org/manual/dev/soft-deploy/fg-repo

For more information

The page here will be at one point merged into theabove pages


REQUIREMENTS
====================

Python 2.6.x
-------------

check while just typing in python on the commandline
(make prg out of it, integrate in shell)
(check at instalation)



Install cmd2 in your local python instalation 

1. Check if cmd2 is installed with the following command

python -c "import cmd2;"

If it is not installed (it will say ImportError: No module named cmd2)

please install it.

or simply do easy_install -U cmd2

In future we will have an egg that resolves dependencied and installes also cmd2 automatically)

    wget http://pypi.python.org/packages/2.6/c/cmd2/cmd2-0.6.2-py2.6.egg#md5=4c1804bdb53acd313ef83d150ed1cc46
    sudo easy_install cmd2-0.6.2-py2.6.egg

This will install cmd2 in your default python systems libarry


INSTALATION OF THE FG CODE
==============================

1. Please create a directory, where you place the FG source code. 

    set $FG_PATH=

    mkdir -p $FG_PATH
    cd $FG_PATH
    svn checkout https://futuregrid.svn.sourceforge.net/svnroot/futuregrid/core/trunk/src/futuregrid/
    cp futuregrid/fg.py .
    set $FG_PATH=`cwd`/futuregrid

in bash

    export FG_HOME=`pwd`


The file 

    /opt/futuregrid/futuregrid/fg.py 

must be copied to /opt/futuregrid and will be the futuregrid
executable (we need to look into that, to leave only one futuregrid).

The var directory will be in the server side and is useful to keep the
log files and mysql password. Everyone need to have write access.

Other configuration details may be needed. Thus, each component will
have a README.txt file.

For testing purpose, please add your ssh-key to your local
.ssh/authorized_keys because the Image Repository uses ssh to executer
commands in the server side (localhost). And execute ssh-add TBD


INSTALATION OF THE IMAGE REPOSITORY
========================================

see: https://portal.futuregrid.org/fg-image-repository-deployment

APPENDIX

TODO: on OSX describe how to use curl instead of wget

TODO: FInd out a way to check if cmd2 is already installed


INSTALLING CODE BEAUTIFIERS
===========================

    sudo easy_install pep8
    sudo easy_install pylint

see: 
* http://pypi.python.org/pypi/pep8
* http://www.logilab.org/card/pylint_manual


Integration into Pydev/eclipse

pylint: http://pydev.org/manual_adv_pylint.html
pep8: http://stackoverflow.com/questions/399956/how-to-integrate-pep8-py-in-eclipse

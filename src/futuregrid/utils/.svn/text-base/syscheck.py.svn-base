'''@package futuregrid.utils
checks some simple system parameters to see if we have enough to run the shell
'''

import sys

class sysCheck():

    def __init__(self):
        ''' initializes the system check class and conducts the checks'''
        self.checkPythonVersion()

    def checkPythonVersion(self):
        '''checks if the python version is above or equal to 2.7'''
        print "SYSTEM INFO"
        print "==========="
        if (sys.version_info < (2,7) ):
            sys.exit ("please upgreade to at least python version 2.7")
        else :
            print "Python Version: " + sys.version


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
'''@package fgLog
Easy to use logging. Poll test
'''
import logging
import logging.handlers
import os

class fgLog():
    ''' This class allows to conveniently create a logging file to which
    you can add warnings, errors, infos, and debug messages. For each type
    we provide a convenient method.
    '''

    def __init__(self, logfile, loglevel, whois, verbose):
        '''initializes the log file. the parameters are as follows

        @param logfile name of the log file

        @param loglevel setting of the log level. The log level has to
        be specified as an logging object. It can be logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING 

        @param whois name associated with the log

        @param verbose if True prints some information to stdout
 
       TODO: explain what the loglevels do
        '''
        self._logfile = logfile
        self._logger = logging.getLogger(whois)
        self._formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self._logger.setLevel(loglevel)

        handler = logging.FileHandler(logfile)
        # handlers.RotatingFileHandler(logfile, maxBytes=2048, backupCount=5)

        handler.setFormatter(self._formatter)

        handler.setLevel(loglevel)
        self._logger.addHandler(handler)
        self._logger.propagate = False

        # This is to print in the stdout the same that in the log
        if(verbose):
            handler = logging.StreamHandler()
            handler.setLevel(loglevel)
            handler.setFormatter(self._formatter)
            self._logger.addHandler(handler)


    def getLogger(self, name):
        return logging.getLogger(name)
    
    def getLogFile(self):
        '''returns the log file'''
        return self._logfile

    def debug(self, text):
        '''includes a debug message of "text" into the log file.
        @param text the message written into the log file'''
        self._logger.debug(text)

    def info(self, text):
        '''includes an info message of "text" into the log file
        @param text the message written into the log file'''
        self._logger.info(text)

    def warning(self, text):
        '''includes a warning message of "text" into the log file
        @param text the message written into the log file'''
        self._logger.warning(text)

    def error(self, text):
        '''includes an error message of "text" into the log file
        @param text the message written into the log file'''
        self._logger.error(text)

    def clear(self):
        '''removes the log file'''
        os.remove(self._logfile)

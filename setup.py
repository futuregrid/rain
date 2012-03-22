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

from distribute_setup import use_setuptools
use_setuptools(version="0.6.15")
from setuptools import setup, find_packages
import sys
sys.path.insert(0, './src')
from futuregrid import RELEASE

setup(
    name = 'futuregrid',
    version = RELEASE,
    description = "FutureGrid Rain and Image Management is a software for managing OS images and enabling advance dynamic provisioning to users",
    author = 'Javier Diaz, Fugang Wang, Gregor von Laszewski, Andrew J. Younge, Mike Lewis',
    author_email = 'javier.diazmontes@gmail.com',
    license = "Apache License (2.0)",
    url = "http://portal.futregrid.org",
    classifiers = [
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache 2.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Distributed Computing"
        ],
    keywords = "Cloud, Grid, HPC",
    package_dir = {'': 'src'},
    packages = find_packages("src"),
    package_data = {'futuregrid.shell': ['banner.txt']},
    data_files = [
        ('/etc/futuregrid', ['etc/fg-server.conf-sample', 'etc/fg-client.conf-sample', 'etc/fg-restrepo.conf-sample', 'etc/cumulus.conf-sample', 'etc/swift.conf-sample', 'etc/mysql.conf-sample'])
        ],
    scripts = [
        'src/futuregrid/shell/fg-shell',
        'src/futuregrid/image/management/fg-generate',
        'src/futuregrid/image/management/IMGenerateServer.py',
        'src/futuregrid/image/management/IMGenerateScript.py',
        'src/futuregrid/image/management/fg-register',
        'src/futuregrid/image/management/IMRegisterServerIaaS.py',
        'src/futuregrid/image/management/IMRegisterServerMoab.py',
        'src/futuregrid/image/management/IMRegisterServerXcat.py',
        'src/futuregrid/image/repository/client/fg-repo',
        'src/futuregrid/image/repository/server/IRServer.py',
        'src/futuregrid/image/repository/rest/IRRestServer.py',        
        ],
    install_requires = ['setuptools', 'pymongo','cmd2','argparse','boto','cherrypy','python-ldap', 'MySQL-python', 
                        'python-cloudfiles', 'pymongo'],#, 'pyopenssl'],
    zip_safe = False,
    include_package_date=True
    )


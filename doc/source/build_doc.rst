.. _build_doc:

Building the Rain Documentation
===============================

The documentation has been created using `Sphinx <http://sphinx.pocoo.org/>`_ and therefore you have to build it before you can see the final html files. The source
files of the documentation can be found under the ``doc`` directory of our software package. Next, we define the needed steps to build the documentation.

#. Install the documentation :ref:`Using a source tarball <source_tarball>` or :ref:`Downloading the latest code from GitHub <github_install>`.
#. Change your current directory to the ``doc`` one.

   ::

      cd doc

#. Build the documentation using the Makefile.

   ::
   
      make website
      
#. The documentation should be in the directory ``build/web-<version>/``. This basically contains html files that can be copied to a regular http server.
 

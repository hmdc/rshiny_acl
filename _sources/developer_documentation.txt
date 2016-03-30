Operations/Development Documentation
====================================
.. toctree::
   :maxdepth: 2
   :hidden:

   modules

Getting the source code
-----------------------
``git clone https://github.com/hmdc/rshiny_acl``

Making changes
--------------
* Make your changes
* Install pytest, if you haven't already::

    pip install pytest --user

* Run the spec tests::

    cd rshiny_acl
    ~/.local/bin/py.test

* If they pass, you're good to commit.
* Make sure to update spec tests if you're adding new functionality.

Building the documentation
--------------------------
From the RCE, run::

  git clone git@github.com:git@github.com:hmdc/rshiny_acl.git
  pip install sphinx --user --force-reinstall --upgrade
  pip install sphinx_rtd_theme --user --force-reinstall --upgrade
  cd rshiny_acl/doc
  PATH=~/.local/bin PYTHONPATH=../:$PYTHONPATH make html

Once you've installed the  ``sphinx`` and ``sphinx_rtd_theme``
pre-requisites, you can rebuild documentation by running::

  cd rshiny_acl/doc
  PATH=~/.local/bin PYTHONPATH=../:$PYTHONPATH make html

HTML output is placed in ``rce-interactive-tools/doc/build/html`` which
you can view via any web browser.

.. note::

  Sphinx and sphinx_rtd_theme are already installed on NFS in
  ``/nfs/tools/lib/python/2.6/current``. However, the Python 2.6
  virtualenv executable is unable to locate htcondor appropriately. In
  the meantime, I simply force reinstall these modules to my home
  directory in order to build the documentation. Although someone should
  look into this.

Editing the documentation
-------------------------
Documentation is written with sphinx and ReST. Here are some helpful
resources:

* `Restructed Text (reST) and Sphinx Cheat Sheet
  <http://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_
* `Documenting Your Project Using Sphinx
  <https://pythonhosted.org/an_example_pypi_project/sphinx.html>`_

Publishing documentation to GitHub pages
----------------------------------------
From the RCE, run::

  cd rshiny_acl
  PATH=~/.local/bin PYTHONPATH=../:$PYTHONPATH make html ghpages

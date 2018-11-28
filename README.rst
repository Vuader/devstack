Installation
============

Tachyonic Project devstack currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6, 3,7.

Requirements
------------

Devstack uses docker to run endpoints and services known as projects in Tachonic.

https://www.docker.com

Quick Install
-------------

.. code:: bash

   $ pip3 install https://github.com/TachyonicProject/devstack/tarball/latest#egg=devstack

Source Code Install
-------------------

Tachyonic Project devstack infrastructure and code is hosted on `GitHub <https://github.com/TachyonicProject/devstack>`_.
Making the code easy to browse, download, fork, etc. Pull requests are always welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonicProject/devstack.git

Once you have cloned the repo or downloaded a tarball from GitHub, you
can install Tachyon like this:

.. code:: bash

    $ cd devstack
    $ pip3 install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your development area, and then run the following to install it using
symbolic linking, so that when you change your code, the changes will be
automatically available to your app without having to reinstall the package.

**Keep in mind Cythonized C code for all modules is included during install
or develop. During development code alterations you need run setup.py after
each change.**

.. code:: bash

    $ cd devstack
    $ python3 setup.py develop

During development without explicitly running **setup.py** after each change,
you can use the following. It clears the compiled .cpython.so modules to ensure
code is loaded from Python sources.

.. code:: bash

    $ python3 setup.py clean

Usage
-----

Devstack creates multiple docker insances for micro-services that share a common directory on th host machine. 

The common directory contains Tachyonic Project Repositories for micro-services and dependencies. There is an additional directory known as www that contains the project deployment environment.

Example startup:

.. code:: bash

   $ mkdir tachyonic
   $ devstack -s tachyonic

Once this is completed, you can see view wether the docker instances are running using:

.. code:: bash
   
   $ docker ps

Provide atleast 2 minutes for all nodes and services to be runnining especially during initial startup.

You can access the Photonic UI via http://localhost:9000

All other endpoints/services are exposed to the host.

Mysql: 3306
UI/Photonic Port 9000 (RestAPI/JSON)
Identity/Infinitystone: 9001 (RestAPI/JSON)
Radius/Tradius: 9002 (RestAPI/JSON)

Development
-----------
By default we do not allow to push to our repositories directly.

When editing code ensure you rename origin and add your own fork as origin.

Example:

.. code:: bash

   $ git remote rename origin upstream
   $ git remote add origin git@github.com:cfrademan/tradius.git
   $ git push -u origin development

To restart endpoint gunicorn wsgi applications:

.. code:: bash

   $ devstack -r

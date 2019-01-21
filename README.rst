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

Devstack creates multiple docker insances for micro-services that share a common directory on the host machine.

The common directory contains Tachyonic Project Repositories for micro-services and dependencies.
There is an additional directory known as www that contains the project deployment environment.

Example startup:

.. code:: bash

   $ mkdir tachyonic
   $ devstack -s tachyonic

Once this is completed, you can see view wether the docker instances are running using:

.. code:: bash
   
   $ docker ps

Provide at least 2 minutes for all nodes and services to be runnining especially during initial startup.

You can access the Photonic UI via http://localhost:9000

All other endpoints/services are exposed to the host.

+-------------------------+------+----------------+
| Mysql                   | 3306 |                |
+-------------------------+------+----------------+
| UI/Photonic             | 9000 | (RestAPI/JSON) |
+-------------------------+------+----------------+
| Identity/Infinitystone  | 9001 | (RestAPI/JSON) |
+-------------------------+------+----------------+
| Radius/Tradius          | 9002 | (RestAPI/JSON) |
+-------------------------+------+----------------+

To control which modules are started, specify a json file (via ``-m`` switch) with the required builds and ports.
For example, create a file called ``modules.json``:

.. code:: json

    {
        "builds" : ["infinitystone",
                    "tradius",
                    "netrino",
                    "topenstack",
                    "photonic"
                   ],

        "ports" : {"photonic": { "80/tcp": 9000 },
                  "infinitystone": { "80/tcp": 9001 },
                  "tradius": {"80/tcp": 9002,
                         "1812/udp": 1812,
                         "1813/udp": 1813,
                         "1812/tcp": 1812,
                         "1813/tcp": 1813
                        },
                  "netrino": { "80/tcp": 9004 },
                  "topenstack": { "80/tcp": 9005 }
            }
    }

and start with:

.. code:: bash

   $ devstack -s tachyonic -m modules.json


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

When the tachyonic containers start for the first time, their entrypoint scripts does a ``pip install`` on the package
to install the package as well as their dependencies. Because this takes a bit of time, it creates a
``/installed`` file in the container, and only performs this installation if the ``/installed`` file is not present. If you
have the requirement to force a re-installation, simply remove that file from the running container.
For example, for photonic:

.. code:: bash

   $ docker exec photonic rm /installed

Next time when ``devstack -s path`` is run, the package and it's dependacies will be re-installed.

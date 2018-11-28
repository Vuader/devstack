#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import argparse
import subprocess
from tempfile import TemporaryFile


from luxon.utils.pkg import Module
from luxon.utils.files import mkdir, Open, chmod, exists, ls, rm, joinpath
from luxon.core.config import Config
from luxon.utils.dk import (start,
                            stop,
                            restart,
                            build,
                            remove_image,
                            remove_container,
                            exec)

from devstack import metadata

builds = ['infinitystone',
          'tradius',
          'photonic',
         ]

depends = ['luxon',
           'psychokinetic'
          ]

ports = {'photonic': { '80/tcp': 9000 },
         'infinitystone': { '80/tcp': 9001 },
         'tradius': { '80/tcp': 9002 }
        }

def execute(*args):
    loginfo = TemporaryFile()
    env = os.environ.copy()
    if '__PYVENV_LAUNCHER__' in env:
        del env['__PYVENV_LAUNCHER__']

    try:
        subprocess.run(*args, stdout=loginfo,
                       stderr=loginfo,
                       check=True, env=env)
        loginfo.seek(0)
        return loginfo.read().decode('utf-8')
    except Exception:
        loginfo.seek(0)
        print(loginfo.read().decode('utf-8'))
        raise

def kill(args):
    for b in builds:
        try:
            print("Stopping %s" % b)
            stop(b)
        except:
            pass
    try:
        stop('sql')
    except:
        pass

    try:
        stop('rabbitmq')
    except:
        pass

    try:
        stop('redis')
    except:
        pass

def build_images():
    module = Module('devstack')
    for b in builds:
        print("Building %s" % b)
        docker_file = '/resources/%s/Dockerfile' % b
        docker_obj = module.file(docker_file)
        image, log = build(b,
                           docker_obj)
        for l in log:
            print(l)


def clone_repos():
    for b in builds + depends:
        if not exists(b):
            origin = "https://github.com/TachyonicProject/%s.git" % b
            print(execute(['git', 'clone', '-b', 'development',  origin]))

def reload(args):
    for b in builds:
        print("Reloading %s" % b)
        exec(b, 'pkill -HUP -f gunicorn3')

def start_env(path):
    clone_repos()
    mkdir('%s/www' % path)
    print("Starting sql")
    start('sql', 'mariadb:latest',
	  ports={'3306/tcp': 3306},
	  MYSQL_ROOT_PASSWORD='tachyonic',
	  MYSQL_DATABASE='tachyonic',
	  MYSQL_USER='tachyonic',
	  MYSQL_PASSWORD='tachyonic')
    print("Starting rabbitmq")
    start('rabbitmq', 'rabbitmq:latest')
    print("Starting redis")
    start('redis', 'redis:latest')

    build_images()
    links = []
    module = Module('devstack')
    for b in builds:
        print("Starting %s" % b)
        try:
            remove_container(b)
        except:
            pass
        module.copy('resources/%s/%s.sh' % (b,b,),
                    path)
        module.copy('resources/%s/%s.nginx' % (b,b,),
                    path)
        start(b, b,
              links=['sql', 'rabbitmq', 'redis'] + links,
              volumes={path: '/opt/tachyonic'},
              ports=ports.get(b))
        links.append(b)

def main(argv):
    description = metadata.description + ' ' + metadata.version
    print("%s\n" % description)

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-s',
                       dest='path',
                       help='Start/Build environment in path')

    group.add_argument('-k',
                       action='append_const',
                       dest='funcs',
                       const=kill,
                       help='Shutdown all containers in docker environment')

    group.add_argument('-r',
                       action='append_const',
                       dest='funcs',
                       const=reload,
                       help='Reload Gunicorn Applications in all containers')


    args = parser.parse_args()

    if args.funcs is not None:
        for func in args.funcs:
            func(args)

    if args.path is not None:
        args.path = os.path.abspath(args.path)
        os.chdir(args.path)
        start_env(args.path)

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
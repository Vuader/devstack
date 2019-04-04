#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
# Copyright (c) 2018-2019 David Kruger.
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
import json
from tempfile import TemporaryFile


from luxon.utils.pkg import Module
from luxon.utils.files import mkdir, exists
from luxon.utils.dk import (start,
                            exec,
                            stop,
                            build,
                            remove_image,
                            remove_container)
from luxon.utils.dk import restart as container_restart
from devstack import metadata

builds = ['infinitystone',
          'calabiyau',
          'netrino',
          'photonic',
          ]

depends = ['luxon',
           'psychokinetic'
           ]

ports = {'photonic': {'80/tcp': 9000},
         'infinitystone': {'80/tcp': 9001},
         'calabiyau': {'80/tcp': 9002,
                       '1812/udp': 1812,
                       '1813/udp': 1813,
                       '1812/tcp': 1812,
                       '1813/tcp': 1813,
                       },
         'netrino': {'80/tcp': 9003},
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
    containers = ['syslog',
                  'sql',
                  'rabbitmq',
                  'redis',
                  *builds]

    for container in containers:
        try:
            sys.stdout.write("Stop container %s: " % container)
            sys.stdout.flush()
            stop(container)
            sys.stdout.write("Success\n")
        except Exception:
            sys.stdout.write("Failed\n")

        sys.stdout.flush()


def clear(args):
    containers = ['syslog',
                  'sql',
                  'rabbitmq',
                  'redis',
                  *builds]

    for container in containers:
        try:
            sys.stdout.write("Deleting container %s: " % container)
            sys.stdout.flush()
            remove_container(container)
            sys.stdout.write("Success\n")
        except Exception:
            sys.stdout.write("Failed\n")

        sys.stdout.flush()


def delete(args):
    containers = ['balabit/syslog-ng',
                  'mariadb',
                  'rabbitmq',
                  'redis',
                  *builds]

    for container in containers:
        try:
            sys.stdout.write("Deleting image %s: " % container)
            sys.stdout.flush()
            remove_image(container)
            sys.stdout.write("Success\n")
        except Exception:
            sys.stdout.write("Failed\n")

        sys.stdout.flush()


def build_images():
    module = Module('devstack')
    for b in builds:
        try:
            sys.stdout.write("\nBuilding %s: " % b)
            sys.stdout.flush()
            print("Building %s" % b)
            docker_file = '/resources/%s/Dockerfile' % b
            docker_obj = module.file(docker_file)
            image, log = build(b,
                               docker_obj)
            sys.stdout.write("Success\n")
            for l in log:
                print(l)
        except Exception:
            sys.stdout.write("Failed\n")
            sys.stdout.flush()
            exit()

        sys.stdout.flush()


def clone_repos():
    for b in builds + depends:
        if not exists(b):
            origin = "https://github.com/TachyonicProject/%s.git" % b
            print(execute(['git', 'clone', '-b', 'development',  origin]))


def reload(args):
    for container in builds:
        try:
            sys.stdout.write("Reloading Gunicorn %s: " % container)
            sys.stdout.flush()
            exec(container, 'pkill -HUP -f gunicorn3')
            sys.stdout.write("Success\n")
        except Exception:
            sys.stdout.write("Failed\n")

        sys.stdout.flush()


def restart(args):
    containers = ['syslog',
                  'sql',
                  'rabbitmq',
                  'redis',
                  *builds]

    for container in containers:
        try:
            sys.stdout.write("Restarting %s: " % container)
            sys.stdout.flush()
            container_restart(container)
            sys.stdout.write("Success\n")
        except Exception:
            sys.stdout.write("Failed\n")

        sys.stdout.flush()


def bash(container):
    subprocess.call(["docker", "exec", "-it", container, 'bash'])


def start_env(path):
    module = Module('devstack')
    clone_repos()
    mkdir('%s/www' % path)
    mkdir('%s/log' % path)
    print("Starting syslog")
    module.copy('resources/syslog-ng.conf',
                path)
    log_path = path.rstrip('/') + '/log'
    log_conf = path.rstrip('/') + '/syslog-ng.conf'
    start('syslog', 'balabit/syslog-ng:latest',
          volumes={log_path: '/var/log',
                   log_conf: '/etc/syslog-ng/syslog-ng.conf'
                   },
          hostname='log')
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
    for b in builds:
        print("Starting %s" % b)
        module.copy('resources/%s/%s.sh' % (b, b,),
                    path)
        module.copy('resources/%s/%s.nginx' % (b, b,),
                    path)
        start(b, b,
              links=['syslog', 'sql', 'rabbitmq', 'redis'] + links,
              volumes={path: '/opt/tachyonic'},
              ports=ports.get(b),
              hostname=b)
        links.append(b)


def main(argv):
    global builds
    global ports

    description = metadata.description + ' ' + metadata.version
    print("%s\n" % description)

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-b',
                       dest='bash',
                       help='Start Bash Shell')

    group.add_argument('-s',
                       dest='path',
                       help='Start/Build environment in path')

    group.add_argument('-c',
                       action='append_const',
                       dest='funcs',
                       const=clear,
                       help='Clear containers in docker environment')

    group.add_argument('-d',
                       action='append_const',
                       dest='funcs',
                       const=delete,
                       help='Clear images in docker environment')

    group.add_argument('-k',
                       action='append_const',
                       dest='funcs',
                       const=kill,
                       help='Shutdown all containers in docker environment')

    group.add_argument('-r',
                       action='append_const',
                       dest='funcs',
                       const=restart,
                       help='Restart all containers')

    group.add_argument('-g',
                       action='append_const',
                       dest='funcs',
                       const=reload,
                       help='Restart all gunicorn')

    parser.add_argument('-m',
                        help='Load modules from json file at '
                             'specified location',
                        dest='json_file',
                        default=None)

    args = parser.parse_args()

    if args.json_file is not None:
        modules = json.load(open(args.json_file))
        builds = modules['builds']
        ports = modules['ports']

    if args.funcs is not None:
        for func in args.funcs:
            func(args)

    if args.path is not None:
        args.path = os.path.abspath(args.path)
        os.chdir(args.path)
        start_env(args.path)

    if args.bash is not None:
        bash(args.bash)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()

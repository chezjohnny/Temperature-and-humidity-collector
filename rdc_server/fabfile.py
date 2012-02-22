#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
# the user to use for the remote commands
env.user = 'rero'
# the servers where the commands are executed
env.hosts = ['panoramix.rero.ch']

def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)

def deploy():
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '/tmp/webtest.tar.gz')
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir /tmp/webtest')
    with cd('/tmp/webtest'):
        run('tar xzf /tmp/webtest.tar.gz')
        # now setup the package with our virtual environment's
        # python interpreter
        with cd('/tmp/webtest/%s' % dist):
            run('/rero/pythonenv/webtest/bin/python ./setup.py install -f')
    # now that all is set up, delete the folder again
    run('chown -R rero:www-data /rero/pythonenv')
    run('rm -rf /tmp/webtest /tmp/webtest.tar.gz')
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('touch /var/www/webtest.wsgi')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
# the user to use for the remote commands
env.user = 'root'
# the servers where the commands are executed
env.hosts = ['chezjohnny.no-ip.org']

def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)

def deploy():
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '/tmp/rdc.tar.gz')
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir /tmp/rdc')
    with cd('/tmp/rdc'):
        run('tar xzf /tmp/rdc.tar.gz')
        # now setup the package with our virtual environment's
        # python interpreter
        with cd('/tmp/rdc/%s' % dist):
            run('/usr/local/pythonenv/rdc/bin/python ./setup.py install -f')
    # now that all is set up, delete the folder again
    #run('chown -R rero:www-data /rero/pythonenv')
    run('rm -rf /tmp/rdc /tmp/rdc.tar.gz')
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('touch /var/www/rdc_test.wsgi')

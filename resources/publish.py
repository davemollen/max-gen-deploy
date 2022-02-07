#!/usr/bin/python

from __future__ import print_function

import json
import os
import sys
import getopt
import ssl
from datetime import datetime
from hashlib import md5
from time import sleep
from urllib import urlopen

name = ""

with open('max-gen-plugin/max-gen-plugin.mk', 'r') as fh:
    for line in fh.readlines():
        if line.startswith('MAX_GEN_PLUGIN_PLUGIN_NAME = '):
            name = line.replace('MAX_GEN_PLUGIN_PLUGIN_NAME = ', '', 1).strip()
            break

if not name:
    raise Exception('Build project is missing plugin name property')

base_url = 'https://pipeline.dev.moddevices.com/maxgen/bundle/'
bundle_name = name.replace(' ','_') + '.lv2'

process = {
    'bundles': [
        {'name': bundle_name}
    ],
    'project': 'MAX gen~ Plugins',
    'developer': 'MOD Devices / Cycling \'74',
    'buildroot_pkg': 'max-gen-plugin'
}

if 'keep_environment' in sys.argv:
    process['keep_environment'] = True

print('Submitting process...')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urlopen(base_url, json.dumps(process).encode(), context=ctx)
release_process = json.loads(req.read().decode())

id = release_process['id']
print('Got release process {0}.'.format(id))
print('Uploading buildroot package...', end='')
sys.stdout.flush()

with open('max-gen-plugin.tar.gz', 'rb') as fh:
    data = fh.read()
    checksum = json.loads(urlopen(release_process['source-href'], data, context=ctx).read().decode())
print('Done')

print('Checking md5 {0} ...'.format(checksum), end='')
sys.stdout.flush()

assert checksum == md5(data).hexdigest()
print('Done')

release_process_url = release_process['href']
print('Waiting build (this can take a few minutes).', end='')
sys.stdout.flush()

timeout = 10 * 60  # 10 min
started = datetime.now()
try:
    while True:
        release_process = json.loads(urlopen(release_process_url, context=ctx).read().decode())
        status = release_process['status']
        if status == 'error':
            raise Exception('Process {0} failed, contact MOD Team for more details'.format(id))
        if status == 'finished':
            break
        if (datetime.now() - started).total_seconds() > timeout:
            raise Exception('Process {0} timed out, contact MOD Team for mode details'.format(id))
        print('.', end='')
        sys.stdout.flush()
        sleep(15)
except Exception as ex:
    print('\nError: {0}'.format(ex))
    exit(1)
finally:
    print('\n')

target = 'all'
arguments, values = getopt.getopt(sys.argv[1:], "t:", ["target="])
for currentArgument, currentValue in arguments:
    if currentArgument in ["-t", "--target"]:
        target = currentValue  

if target == 'all' or target == 'duo':
    r = urlopen('{0}bundles/{1}/duo/'.format(release_process_url, bundle_name), context=ctx)
    filename = '../{0}-duo.tar.gz'.format(bundle_name)
    with open(filename, 'wb') as fh:
        fh.write(r.read())
if target == 'all' or target == 'duox':
    r = urlopen('{0}bundles/{1}/aarch64-a53/'.format(release_process_url, bundle_name), context=ctx)
    filename = '../{0}-duox.tar.gz'.format(bundle_name)
    with open(filename, 'wb') as fh:
        fh.write(r.read())
if target == 'all' or target == 'dwarf':
    r = urlopen('{0}bundles/{1}/aarch64-a35/'.format(release_process_url, bundle_name), context=ctx)
    filename = '../{0}-dwarf.tar.gz'.format(bundle_name)
    with open(filename, 'wb') as fh:
        fh.write(r.read())

print('Finished downloading')
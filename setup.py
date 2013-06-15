#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import sys
import shutil
import hashlib
import urllib2
from zipfile import ZipFile
from distutils.core import setup

from globaleaks import __version__

def pip_to_requirements(s):
    """
    Change a PIP-style requirements.txt string into one suitable for setup.py
    """

    m = re.match('(.*)([>=]=[.0-9]*).*', s)
    if m:
        return '%s (%s)' % (m.group(1), m.group(2))
    return s.strip()

if not sys.version_info[:2] == (2, 7):
    print "Error, GlobaLeaks is tested only with python 2.7"
    print "https://github.com/globaleaks/GlobaLeaks/wiki/Technical-requirements"
    raise AssertionError

glclient_path = 'glclient-v'+__version__
def download_glclient():
    glclient_url = "https://globaleaks.org/builds/GLClient/"+glclient_path+".zip"
    print "[+] Downloading glclient from %s" % glclient_url

    o = open('glclient.zip', 'w+')
    f = urllib2.urlopen(glclient_url)
    o.write(f.read())
    o.close()
    print "    ...done."

def verify_glclient():
    print "[+] Checking GLClient hash..."
    glclient_hash = "f718c89daa4daf9c93866d0ec4fbe442c2277c8595dec27eaa5e71f1"
    with open('glclient.zip') as f:
        h = hashlib.sha224(f.read()).hexdigest()
        if not h == glclient_hash:
            raise Exception("%s != %s" % (h, glclient_hash))
    print "    ...success."

def uncompress_glclient(glclient_path):
    print "[+] Uncompressing GLClient..."
    zipfile = ZipFile('glclient.zip')
    zipfile.extractall()
    os.unlink('glclient.zip')
    shutil.move(glclient_path, 'glclient')
    print "    ...done."

def build_glclient():
    print "[+] Building GLClient..."
    os.chdir(glclient_path)
    os.system("npm install -d")
    os.system("grunt build")
    os.chdir('..')
    print "    ...done."

if not os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), 'glclient'))):
    download_glclient()
    verify_glclient()
    uncompress_glclient(glclient_path)
glclient_path = 'glclient'

requires = []
with open('requirements.txt') as f:
    requires = map(pip_to_requirements, f.readlines())

data_files = [('/usr/share/globaleaks/glclient', [os.path.join(glclient_path, 'index.html'),
    os.path.join(glclient_path, 'styles.css'),
    os.path.join(glclient_path, 'scripts.js'),
]),
    ('/usr/share/globaleaks/glclient/images', [
    os.path.join(glclient_path, 'images', 'flags.png'),
    os.path.join(glclient_path, 'images', 'glyphicons-halflings.png'),
    os.path.join(glclient_path, 'images', 'glyphicons-halflings-white.png')
]), ('/usr/share/globaleaks/glbackend', [
    'staticdata/globaleaks_logo.png'])]

setup(
    name="globaleaks",
    version = __version__,
    author="Random GlobaLeaks developers",
    author_email = "info@globaleaks.org",
    url="https://globaleaks.org/",
    package_dir={'globaleaks': 'globaleaks'},
    package_data = {'globaleaks': ['db/sqlite.sql', 'db/default_TNT.txt',
                                   'db/default_CNT.txt', 'db/default_FNT.txt']},
    packages=['globaleaks', 'globaleaks.db', 'globaleaks.handlers',
        'globaleaks.jobs', 'globaleaks.plugins',
        'globaleaks.rest', 'globaleaks.third_party', 'globaleaks.third_party.rstr'],
    data_files=data_files,
    scripts=["bin/globaleaks"],
    requires = requires
)
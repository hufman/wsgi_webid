#!/usr/bin/env python

from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

setup(name='wsgi_webid',
      version='0.1.0',
      description='WSGI Middleware for WebID authentication',
      author='Walter Huf',
      url='https://github.com/hufman/wsgi_webid',
      packages=['wsgi_webid']
     )

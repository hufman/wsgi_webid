#!/usr/bin/env python

from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

requirements = file('requirements.txt').read().split('\n')
test_requirements = file('requirements.test.txt').read().split('\n')

setup(name='wsgi_webid',
      version='0.1.1',
      description='WSGI Middleware for WebID authentication',
      author='Walter Huf',
      url='https://github.com/hufman/wsgi_webid',
      packages=['wsgi_webid'],
      install_requires=requirements,
      test_requires=requirements + test_requirements
     )

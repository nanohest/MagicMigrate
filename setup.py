#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='magmig',
      version=version,
      description='Minimalistic database migration tool',
      author='Kristian Martensen',
      author_email='km@shipbeat.com',
      requires=['pymssql'],
      packages=['MagicMigrate'],
      license='BSD')

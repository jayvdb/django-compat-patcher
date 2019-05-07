#!/usr/bin/env python

import sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # security

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Intended Audience :: Information Technology
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Framework :: Django
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: MacOS :: MacOS X
"""

packages = find_packages(exclude="tests")

setup(
    name='django-compat-patcher',
    version=read("VERSION"),
    author='Pascal Chambon & others',
    author_email='pythoniks@gmail.com',
    url='https://github.com/pakal/django-compat-patcher',
    license='MIT',
    platforms=["any"],
    description="A monkey-patching system to ease the transition between Django versions.",
    classifiers=filter(None, classifiers.split("\n")),
    long_description=read("README.rst"),
    packages=packages,
    tests_require=['django-contrib-comments'],
    # test_suite='your.module.tests',

    use_2to3=True,
    #convert_2to3_doctests=['src/your/module/README.txt'],
    #use_2to3_fixers=['your.fixers'],
    use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'],
)


#!/usr/bin/env python

import sys
import os
from distutils.core import setup

__VERSION__="MASTER"

if __VERSION__ == "MASTER":
    sys.stderr.write("Please set the version in setup.py\n")
    sys.exit(1)

setup(
    name='davis',
    version=__VERSION__,
    license='MIT',
    description='Python Data Visualizer',
    long_description="A simple graphical Python data visualizer. See https://github.com/fboender/davis for more info",
    url='https://github.com/fboender/davis',

    author='Ferry Boender',
    author_email='ferry.boender@electricmonk.nl',

    packages=['davis'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)

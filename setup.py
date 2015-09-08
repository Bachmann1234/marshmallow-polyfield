#!/usr/bin/env python
import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), fname), 'r') as infile:
        content = infile.read()
    return content

setup(
    name='marshmallow-polyfield',
    version=1.0,
    description='An extension to marshmallow to allow for polymorphic fields',
    long_description=read('README.md'),
    author='Matt Bachmann',
    author_email='bachmann.matt@gmail.com',
    url='https://github.com/Bachmann1234/marshmallow-polyfield',
    packages=['marshmallow_polyfield', 'tests'],
    license=read('LICENSE'),
    keywords=('serialization', 'rest', 'json', 'api', 'marshal',
              'marshalling', 'deserialization', 'validation', 'schema'),
    install_requires=['marshmallow>=2.0.0b5'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

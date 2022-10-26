#!/usr/bin/env python
import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), fname), 'r') as infile:
        content = infile.read()
    return content


setup(
    name='marshmallow-polyfield',
    version='5.11',
    description='An unofficial extension to Marshmallow to allow for polymorphic fields',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='Matt Bachmann',
    author_email='bachmann.matt@gmail.com',
    url='https://github.com/Bachmann1234/marshmallow-polyfield',
    packages=['marshmallow_polyfield'],
    license='Apache 2.0',
    keywords=['serialization', 'rest', 'json', 'api', 'marshal',
              'marshalling', 'deserialization', 'validation', 'schema'],
    python_requires='>=3.5',
    install_requires=['marshmallow>=3.0.0b10'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

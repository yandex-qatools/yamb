#!/usr/bin/env python
import setuptools


setuptools.setup(
    name='yamb',
    version='0.1.2',
    license='Apache License, Version 2.0',
    author="Ivan Kalinin",
    author_email="pupssman@yandex-team.ru",
    packages=["yamb"],
    description="Lightweight test data generation framework",
    long_description=open('README.rst').read(),
    install_requires=['pyyaml'],
    classifiers=[
                'Intended Audience :: Developers',
                'License :: OSI Approved :: Apache Software License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development'],
)

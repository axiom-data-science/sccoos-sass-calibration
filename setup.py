#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def pip_requirements(filename='requirements.txt'):
    reqs = []
    with open('requirements.txt', 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            if line:
                reqs.append(line)
    return reqs


setup(
    name             = 'sccoos-sass-calibration',
    version          = '0.0.1',
    description      = 'Applies calibration coefficients to SCCOOS automated shore side instruments and writes out new files',
    long_description = readme(),
    url              = 'https://git.axiom/axioim/sccoos-sass-calibration',
    packages         = find_packages(),
    install_requires = pip_requirements(),
    test_requires    = pip_requirements('dev-requirements.txt'),
    entry_points     = {
        'console_scripts': [
        ],
    },
)
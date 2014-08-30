# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

setup(
    name='sciscrape',
    version='0.1',
    packages=find_packages(),
    package_data={'' : ['tests/data/csv/*/*.csv']},
    include_package_data=True,
    install_requires=[
        str(requirement.req)
        for requirement in parse_requirements('requirements.txt')
    ],
)

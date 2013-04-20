import os
from setuptools import setup, find_packages

setup(
    name='sciscrape',
    version='0.1',
    packages=find_packages(),
    package_data={'' : ['tests/data/csv/*/*.csv']},
    include_package_data=True
)

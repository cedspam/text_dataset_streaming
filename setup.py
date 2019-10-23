import setuptools
from setuptools import setup
from setuptools.command.test import test as TestCommand

import os
import sys


base_path = os.path.dirname(__file__)




class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='text_dataset_streaming',
    version='1.0.0',
    author='cedric.lacrambe',
    author_email='cedric.lacrambe@gmail.com',
     url='',
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires =["smart_open>1.8.1","requests",
                       "pypandoc","mediawiki_parser","mwxml"],
    cmdclass={
        'test': PyTest,
    },
    zip_safe=False,
    tests_require=['pytest'],
)

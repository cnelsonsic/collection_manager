#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='CollectionManager',
      version='0.1',
      description='A stupid collection management app.'
      author='Charles Nelson',
      author_email='cnelsonsic@gmail.com',

      packages=find_packages(),

      install_requires = open('requirements.txt').read(),

      entry_points = {
          'console_scripts': [
              'manager = collection_manager.manager:main',
              ],
          },
     )

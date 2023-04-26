# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of qtapputils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Installation script """

import csv
import setuptools
from setuptools import setup
from apputils import __version__, __project_url__

LONG_DESCRIPTION = ("The qtapputils module provides various utilities "
                    "for building Qt applications in Python.")

with open('requirements.txt', 'r') as csvfile:
    INSTALL_REQUIRES = list(csv.reader(csvfile))
INSTALL_REQUIRES = [item for sublist in INSTALL_REQUIRES for item in sublist]


setup(name='qtapputils',
      version=__version__,
      description=("Utilities for building Qt applications in Python."),
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      license='MIT',
      author='Jean-Sébastien Gosselin',
      author_email='jean-sebastien.gosselin@outlook.ca',
      url=__project_url__,
      ext_modules=[],
      packages=setuptools.find_packages(),
      package_data={},
      include_package_data=True,
      install_requires=INSTALL_REQUIRES,
      classifiers=["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.6"],
      )

# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © AppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of AppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Installation script """

import setuptools
from setuptools import setup
from appconfigs import __version__, __project_url__

LONG_DESCRIPTION = ("The apputils module provides various utilities "
                    "for building Python applications.")

INSTALL_REQUIRES = ['pyqt5']

setup(name='appconfigs',
      version=__version__,
      description=("Utilities for building Python applications."),
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

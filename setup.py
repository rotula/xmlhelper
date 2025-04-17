#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Setup for XML helper
"""

from distutils.core import setup
setup(name="xmlhelper",
      version="0.23.0",
      author="Clemens Radl",
      author_email="clemens.radl@googlemail.com",
      url="http://www.clemens-radl.de/soft/xmlhelper/",
      install_requires=["lxml"],
      py_modules=['xmlhelper'])

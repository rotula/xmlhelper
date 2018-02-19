#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Run test suite for xml helper"""

import sys
import doctest

def run():
    """Run tests"""
    verbose = False
    if "-v" in sys.argv:
        verbose = True
    doctest.testfile("test/test_xmlhelper.txt", verbose=verbose)

if __name__ == "__main__":
    run()


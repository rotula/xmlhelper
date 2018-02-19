#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Create HTML documentation
"""

import sys
import os

import epydoc.markup.restructuredtext

from make_htmldoc_config import epydocpath, targetdir, doctestcsslink
from make_htmldoc_config import objects, doctesttarget, doctestfile

OUTFILENAME = "doctest.htm"
HTMLHEAD = """\
<html>
<head>
<title>XMLHelper doctests</title>
<link rel="stylesheet" href="%s" type="text/css" />
</head>
<body>
<h1>XMLHelper doctests</h1>
""" % doctestcsslink
HTMLFOOT = """\
</body>
</html>
"""

def create_epydoc(targetdir, objects):
    """Create just the epydoc documentation"""
    if not os.path.isdir(targetdir):
        os.mkdir(targetdir)
    if sys.platform == "win32":
        # double-quoting everything
        # @@@Maybe we can just do the same on Linux?
        # Would make things easier.
        command = "\"\"%s\" \"%s\" --html -o \"%s\" --name XMLHelper "\
                "--debug --docformat reStructuredText \"%s\"\"" %\
                (sys.executable, epydocpath, targetdir, objects)
    else:
        command = "%s %s --html -o %s --name XMLHelper "\
                "--docformat reStructuredText %s" %\
                (sys.executable, epydocpath, targetdir, objects)
    os.system(command)

def create_doctest(doctestfile, targetdir, outfilename, htmlhead, htmlfoot):
    """Just store the doctests"""
    errors = []  # @@@What to do about that?
    s = open(doctestfile).read().decode("UTF-8")
    pd = epydoc.markup.restructuredtext.parse_docstring(s, errors)
    html = pd.to_html(None)
    fullhtml = "%s\n%s\n%s\n" % (htmlhead, html, htmlfoot)
    outfile = open(os.path.join(targetdir, outfilename), "w")
    outfile.write(fullhtml)
    outfile.close()

def create_all():
    """Create the complete documentation"""
    create_epydoc(targetdir, objects)
    create_doctest(doctestfile, doctesttarget, OUTFILENAME, HTMLHEAD, HTMLFOOT)

if __name__ == "__main__":
    create_all()

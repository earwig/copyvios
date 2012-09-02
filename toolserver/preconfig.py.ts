# -*- coding: utf-8  -*-

"""
This module contains installation-specific import configuration for the
Toolserver. To add your own, create and put code in the file 'preconfig.py' in
this directory, or rename this file to 'preconfig.py' if you want to use this
specific configuration.
"""

import os
import site
import sys

# Add a local platform-specific site package directory:

plat = sys.platform
if plat.startswith("sunos"):
    plat = "solaris"
elif plat.startswith("linux"):
    plat = "linux"

site.addsitedir(os.path.expanduser("~/.local/" + plat + "/lib/python2.7/site-packages"))
sys.path.insert(0, os.path.expanduser("~/.local/" + plat + "/lib/python2.7/site-packages"))

# EarwigBot, in-between releases, tries to import the 'git' module and add the
# current git commit ID to its __version__ string. This behavior is useful, but
# the Toolserver can be slow at importing things. Insert a fake 'git' module
# into sys.modules so it skips the __version__ addition:

from types import ModuleType
git = ModuleType("git")
sys.modules["git"] = git

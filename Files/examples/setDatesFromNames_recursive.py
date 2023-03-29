#!/usr/bin/env python

from pathlib import Path

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import FromFileName

# Get all files in subdirectories (recursive)
# and set their dates based on file name.
for file in Path(".").glob("**/*"):
  print(file, '>>>')
  print(FromFileName(file).set_date('cma'))

print('.')
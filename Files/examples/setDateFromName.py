#!/usr/bin/env python

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import FromFileName

if len(sys.argv) > 1:
  file = sys.argv[1]
  print(file, '>>>')
  print(FromFileName(file).set_date('m'))  # or 'cma'
else:
  print('?')
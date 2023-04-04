#!/usr/bin/env python

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import CopyFileDate

if len(sys.argv) > 2:
  fileFrom, fileTo = sys.argv[1:3]
  print(f'copy timestamp: {fileFrom} >>> {fileTo}')
  print(CopyFileDate(fileFrom, fileTo).set_date('cma'))
else:
  print('copy timestamp: from? to?')

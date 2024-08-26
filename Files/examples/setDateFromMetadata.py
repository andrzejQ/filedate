#!/usr/bin/env python

import sys
sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import FromMetadata

if len(sys.argv) > 1:
	file = sys.argv[1]
	print(file, '>>>')
	print(FromMetadata(file).set_date('cm'))  # or 'm'
else:
	print('?')

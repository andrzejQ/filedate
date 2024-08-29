#!/usr/bin/env python

import sys
from pathlib import Path
sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import FromFileName

pattern="**/*"
if '-0' in sys.argv[1:]:
	print('non-recursive')
	pattern="*"

# Get all files in subdirectories (recursive, or not if option "-0")
# and set their dates based on file name.
# Accessed date of folder with date in name can be set to the current time (if recursive).
for file in Path( (sys.argv + ['.'])[1] ).glob(pattern):
	print(f'''\n>>> {file}''')
	print(FromFileName(file).set_date('m'))

print('.')

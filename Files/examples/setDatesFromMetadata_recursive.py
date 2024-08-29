#!/usr/bin/env python

import sys
from pathlib import Path
sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import FromMetadata

pattern="**/*"
if '-0' in sys.argv[1:]:
	print('non-recursive')
	pattern="*"

# Get all files in subdirectories (recursive, or not if option "-0")
# and set their dates based on files metadata.
for file in Path( (sys.argv + ['.'])[1] ).glob(pattern):
	print(f'''\n>>> {file}''')
	print(FromMetadata(file).set_date('cm'))

print('.')

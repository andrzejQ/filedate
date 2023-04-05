#!/usr/bin/env python

import os
# from datetime import datetime

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate import FileDate

# Set date of folder (recursive) based on dates of files below it
# iterative from child directories first.
# Option `-e`: remove empty folders recursively
# https://stackoverflow.com/questions/23488924/how-to-delete-recursively-empty-folders-in-python3


def set_date_of_folders(dir0):
	oldest_timestamp = 116444736000000000 if FileDate.windows else 0 # 1970-01-01

	def set_date_of_folder(root, names):
		print(f'#$# {root=} >>> {names}') #$#
		if not names: #empty folder
			ctime = oldest_timestamp
			mtime = oldest_timestamp
		else:
			ctime = None
			mtime = None
			for f in names:
				file_date = FileDate( os.path.realpath(os.path.join(root, f)) )
				dt = file_date.get_st()  #$#; print(f'#$# {dt=}') #$#
				if dt["created"] > oldest_timestamp:
					ctime = dt["created"] if ctime is None else min(mtime, dt["created"])
				mtime = dt["modified"] if mtime is None else max(mtime, dt["modified"])

		dir_date = FileDate(root)
		dir_date.set( created = ctime, modified = mtime, accessed = mtime )
		print(f'''>&> {root} : {FileDate(root)}''')
		return

	print(f'Set date of {dir0!r} and below folders:')
	for root, dirnames, filenames in os.walk(dir0, topdown=False):
		set_date_of_folder(root, dirnames + filenames)

	print('.')

###

# Sometimes will also be usefull:

def remove_empty_dirs(dir0):
	def remove_empty_dir(path):
		try:
			os.rmdir(path)
			return True
		except OSError: #not empty
			return False

	print(f'Removed empty dirs below {dir0!r}:')
	for root, dirnames, filenames in os.walk(dir0, topdown=False):
	#  print(f'{root=} >>> {dirnames=} >>> {filenames=}')
		for dirname in dirnames:
			d = os.path.realpath(os.path.join(root, dirname))
			if remove_empty_dir(d):
				print(d)
	print('.')

###


if len(sys.argv) > 1 and sys.argv[1] == '-e':
	remove_empty_dirs('.')

set_date_of_folders('.')

#!/usr/bin/env python

# import os
# from warnings import warn

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate import FileDate

#-=-=-=-#

class CopyFileDate:
	"""Utility for "copying" files dates.
	>>> FileDate.SET_SILENT = False # run "filedate.py" first or use `...` with # doctest: +ELLIPSIS
	>>> print(FileDate('../../test.txt'))  ## Unix - created is not set # doctest: +ELLIPSIS
	{'created': '...', 'modified': '2001-03-04 00:00:00', 'accessed': '2001-05-06 00:00:00'}
	>>> print(CopyFileDate("../../test.txt", "rec_20210911 134705.abc.txt").set_date('cma')) ## Unix - created is not set # doctest: +ELLIPSIS
	{'created': '...', 'modified': '2001-03-04 00:00:00', 'accessed': '2001-05-06 00:00:00'}
	"""
	def __init__(self, inpt: str, output: str):
		f =  FileDate(inpt)

		self.inp_timestamp = f.get_st()
		self.output = output
		#$# print(self.output) #$#

	def set_date(self, cma='cma'):
		"""
		Sets the date based on `inpt` file date
		for [c]reated, [m]odified, [a]ccessed date
		"""
		dt_tm_param = {'created': None, 'modified': None, 'accessed': None}
		for k in dt_tm_param.keys():
			if k[0] in cma:
				# if k[0] == 'c' and not FileDate.windows:
				#   warn('Unix system - setting creation date is obsolete')
				dt_tm_param[k] = self.inp_timestamp[k]

		return FileDate(self.output).set(**dt_tm_param) # return FileDate.self if not FileDate.SET_SILENT

#-=-=-=-#

Move = Transfer = Copy = CopyFileDate

if __name__ == '__main__':
	import doctest
	doctest.testmod()
	print('.')

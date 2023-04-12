import os
import sys
sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate.utils import CopyFileDate

# Copy timestamp from files and folders in `dir1` 
# (recursive, or not if option "-0" as 3-rd parameter)
# to all files and folders in `dir2` - if names match
# Parameters: dir1 dir2(option, dafault `.`) -0(option) 

[dir1, dir2] = (sys.argv + ['.','.'])[1:3]
#dir1 = r'..\..\..\test\Files\examples'

if os.path.samefile(dir1, dir2):
	print(f'''{dir1} == {dir2} : nothing to do.''')
	sys.exit(1)  # >>>>>>>>>>>>>>>>>>>>>>>>

nonrecursive = '-0' in sys.argv[3:]
if nonrecursive:
	print('non-recursive')

for root, dirs, files in os.walk(dir2, topdown=False or nonrecursive):
	relative_path = os.path.relpath(root, dir2)
	#$# print(f'\n{root=}\n{dirs=}\n{files=}\n{relative_path=}') #$#
	files_dirs = dirs + files
	for fd in files_dirs:
		other = os.path.join(dir1, relative_path, fd)
		to = os.path.join(root, fd)
		print(f'\ntimestamp from: {other}\nto: {to}')
		print(CopyFileDate(other, to).set_date('cma'))
	if nonrecursive:
		break

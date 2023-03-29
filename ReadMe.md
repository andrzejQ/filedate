<p align=center><img src=https://raw.githubusercontent.com/kubinka0505/filedate/master/Documents/Pictures/filedate.svg width=50%></p>

<p align=center>
<a href=http://github.com/andrzejQ/filedate/releases>
<img src=https://img.shields.io/github/v/release/andrzejQ/filedate?style=for-the-badge></a>
<a href=http://github.com/andrzejQ/filedate/commit>
<img src=https://img.shields.io/github/last-commit/andrzejQ/filedate?style=for-the-badge></a>
<a href=http://github.com/andrzejQ/filedate/blob/master/License.txt>
<img src=https://img.shields.io/github/license/andrzejQ/filedate?logo=readthedocs&color=red&logoColor=white&style=for-the-badge></a>
</p>
<p align=center>
<img src=https://img.shields.io/tokei/lines/github/andrzejQ/filedate?style=for-the-badge>　
<img src=https://img.shields.io/github/languages/code-size/andrzejQ/filedate?style=for-the-badge>
<img src=https://img.shields.io/codeclimate/maintainability/andrzejQ/filedate?logo=code-climate&style=for-the-badge>
<img src=https://img.shields.io/codacy/grade/c8aeb5f42a38414da83d4156b546a4d1?logo=codacy&style=for-the-badge>
</p>


## Description 📝

Simple, convenient and cross-platform file date changing library. 📅

Forked from [kubinka0505/filedate](https://github.com/kubinka0505/filedate)

See also  [jelmerwouters / filedate](https://github.com/jelmerwouters/filedate) -> FileDate.set() (not tested here, commented)

## Installation 🖥️

* [`git`](https://github.com/andrzejQ/filedate.git) or get source files

```bash
git clone git://github.com/andrzejQ/filedate
cd filedate
python setup.py install
```
Source can be also used without installation.
 
## Usage 📝

* see doctest examples

```python
from filedate import FileDate

# Create filedate object
file_date = FileDate('__init__.py')

# Get file date
file_date.get() 
# {'created': datetime.datetime(20..,... 'modified': ... 'accessed': ...}
print(file_date) # .get(); __str__()
# {'created': '20..

# Set file/folder date
file_date.set(
  created = "01.02.2000 12:00",
  modified = "2001/03/04",
  accessed = "2001-05-06")
# {'created': '2000-02-01 12:00:00', 'modified': '2001-03-04 00:00:00', 'accessed': '2001-05-06 00:00:00'}
file_date.set( 
  created = "01.02.2000 12:00", 
  modified = "3:40PM 2001/03/04", 
  accessed = "5rd March 2002 20:21:22"
)
# {'created': '2000-02-11 12:00:00', 'modified': '2001-04-03 15:40:00', 'accessed': '2002-03-05 20:21:22'}
```

### Copy file dates from one to another 🔃

* for [c]reated, [m]odified, [a]ccessed date

```python
from filedate.utils import CopyFileDate
CopyFileDate("../__init__.py", "rec_20210911 134705.abc.txt").set_date('cma')
```

### **Keeping files dates** ⌛
```python
from pathlib import Path
from filedate.utils import KeepFileDate

# Get all files in subdirectories (recursive!)
Files = []
for File in Path(".").glob("**/*"):
	Files.append(File)

#---#

# Initialize `Keep` object
Dates = KeepFileDate(Files)

# Pick dates
Dates.pick()

# ... Do your stuff ...
#
# from os import system
# for File in Files:
#     system(f'optimize -i "{File}"')

# Drop dates
Dates.drop()
```

### **Set file dates based on its name** 📝

* for [c]reated, [m]odified, [a]ccessed date

```python
from filedate.utils import FromFileName
FromFileName("rec_2020-09-11 13.47.05.abc.txt").set_date('cma')
```
see also examples in `_yyyy_()` and `_dd_MM_yyyy_()`

### Working examples

* Files\examples\ **setDatesFromNames_recursive.py**  
  -> Set date of folder (recursive) based on dates of files below it iterative from child directories first.
* Files\examples\ **setFolderDates_recursive.py**  
  -> Get all files in subdirectories (recursive) and set their dates based on file name.
from os import *
from setuptools import *
del open

chdir(path.abspath(path.dirname(__file__)))

#-=-=-=-#

setup(
	name = "filedate",
	description = open("ReadMe.rst").readline().rstrip(),
	version = "2.2",
	author = "kubinka0505; forked by Benjamin Design; forked by andrzejQ",
	license = "GPLv3",
	keywords = "filedate file date change changing changer",
	url = "https://github.com/andrzejQ/filedate"
	classifiers = [
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3 :: Only",
		"Operating System :: OS Independent",
		"Environment :: Console",
		"Intended Audience :: End Users/Desktop",
		"Topic :: Desktop Environment :: File Managers",
		"Natural Language :: English"
	],
	python_requires = ">=3.8",
	install_requires = "python-dateutil",
	packages = find_packages()
)
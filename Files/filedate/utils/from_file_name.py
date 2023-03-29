#!/usr/bin/env python

import re
from pathlib import Path
from datetime import datetime
from dateutil import parser

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate import FileDate

#-=-=-=-#

class FromFileName:
  """Utility for setting file date based on its name."""
  def __init__(self, input: str):
    self.input = input
    self._date = None # or timestamp or str

#-=-=-=-#
    
  def _yyyy_(inp: str) -> str:
    """_yyyy_(inp: str) -> str:
    Get date and time from file name, ignoring substring before YYYY
  >>> print(FromFileName._yyyy_("~/Downloads/rec1_20200911_134705.abc.wav"))
  20200911 134705
  >>> print(FromFileName._yyyy_("~/Downloads/rec1_2020-09-11 13.47.05.abc.wav"))
  20200911 134705
    """
    dt_tm = ''
    fNmYYYY_, cnt = re.subn(r'^.*?(?=\d\d\d\d)', '', Path(inp).stem, count =1)
    if cnt:
      yyyyyMMddhhmmss = re.sub(r'\D','',fNmYYYY_)
      dt_tm = yyyyyMMddhhmmss[:8]
      if len(yyyyyMMddhhmmss) > 8:
        dt_tm += ' '+yyyyyMMddhhmmss[8:14]
      else:
        dt_tm = (dt_tm+'0101')[:8]
    return dt_tm


  #-=-#

  def _dd_MM_yyyy_(inp: str) -> str:
    """dt_tm_dd_MM_yyyy_(inp: str) -> str:
    Get date and time from file name, ignoring substring before dd_MM_yyyy
  >>> print(FromFileName._dd_MM_yyyy_("~/Downloads/rec1_11.09.2020 13.47.05.abc.wav"))
  20200911 134705
    """
    dt_tm = ''
    fNm_dMy_, cnt = re.subn(r'^.*?(?=\d{2}\D\d{2}\D\d{4})', '', Path(inp).stem, count =1)
    if cnt:
      ddMMyyyyyhhmmss = re.sub(r'\D','',fNm_dMy_)
      dt_tm = ddMMyyyyyhhmmss[4:8]+ddMMyyyyyhhmmss[2:4]+ddMMyyyyyhhmmss[:2]
      if len(ddMMyyyyyhhmmss) > 8:
        dt_tm += ' '+ddMMyyyyyhhmmss[8:14]
      else:
        dt_tm = (dt_tm+'0101')[:8]
    return dt_tm

  #-=-#
      
  def set_date(self, cma='cma', modify = _yyyy_):
    """
  Sets the date based on `self.input` file name
  for [c]reated, [m]odified, [a]ccessed date
  >>> FileDate.SET_SILENT = False
  >>> print( FromFileName("rec_2020-09-11 13.47.05.abc.txt").set_date('cma') )
  {'created': '2020-09-11 13:47:05', 'modified': '2020-09-11 13:47:05', 'accessed': '2020-09-11 13:47:05'}
  """
    dt_tm = modify(self.input)   #$#;print(f'#$# {dt_tm=}') #$#
    try:
      self._date = FileDate._UxW_timestamp( parser.parse(dt_tm) )
    except ValueError:
      print(f'''"{dt_tm}" <- string does not contain a date''')
      return None
    except OSError:
      print(f'''"{dt_tm}" <- string does not contain valid file date''')
      return None

    if dt_tm < '1970':
      print(f'''"{dt_tm}" <- string does not contain valid file date''')
      return None

    if not self._date:
      return None
    dt_tm_param = {'created': None, 'modified': None, 'accessed': None}
    for k in dt_tm_param.keys(): 
      if k[0] in cma:
        dt_tm_param[k] = self._date

    return FileDate(self.input).set(**dt_tm_param) # return str(FileDate.self) if not FileDate.SET_SILENT

#-=-=-=-#

# FromFile = FromName = Name = FromFileName

#=========================================

def more_tests():
  """
  more tests for: _yyyy_(), _dd_MM_yyyy_()
  >>> print(FromFileName._yyyy_("~/Downloads/rec_20-09-11 13.47.05.abc.wav"))
  <BLANKLINE>
  >>> print(FromFileName._dd_MM_yyyy_("~/Downloads/rec_20-09-11 13.47.05.abc.wav"))
  <BLANKLINE>
  >>> print(FromFileName._yyyy_("~/Downloads/rec1_20200911.abc.wav"))
  20200911
  >>> print(FromFileName._yyyy_("~/Downloads/rec1_2020-09.abc.wav"))
  20200901
  >>> print(FromFileName._yyyy_("~/Downloads/rec_2x02.abc.wav"))
  <BLANKLINE>
  >>> print(FromFileName._yyyy_("x_311_y.txt"))
  <BLANKLINE>
  >>> FromFileName("x_0311_y.txt").set_date('cma')
  "03110101" <- string does not contain valid file date
  """
  pass


if __name__ == '__main__':
  import doctest
  doctest.testmod()
  print('.')
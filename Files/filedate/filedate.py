#!/usr/bin/env python

import os
from pathlib import Path
from datetime import datetime, timezone
from dateutil.parser import parse # py3: python -m pip install python-dateutil
# https://dateutil.readthedocs.io/en/stable/parser.html
import re

#-=-=-=-#

if os.sys.platform.startswith("win"):
  from ctypes import windll, wintypes, byref
  
  EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
  HUNDREDS_OF_NS = 10000000
  
  def win_tstamp_(unx_timestamp: float) -> int: 
    return EPOCH_AS_FILETIME + int(unx_timestamp * HUNDREDS_OF_NS)
  
#  def unx_tstamp_(win_timestamp: int) -> float: 
#    return (win_timestamp - EPOCH_AS_FILETIME) / HUNDREDS_OF_NS
  def datetime_win_(win_timestamp: int) -> datetime:
    # Get seconds and remainder in terms of Unix epoch
    s, ns100 = divmod(win_timestamp - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
    # Convert to datetime object, with remainder as microseconds.
    return datetime.fromtimestamp(s).replace(microsecond=(ns100 // 10))

  def quadword_(filetime) -> int:
    t = wintypes.FILETIME.from_buffer_copy(filetime)
    return (t.dwHighDateTime << 32) + t.dwLowDateTime
  
  def filetime_(quadword):
    return wintypes.FILETIME(quadword & 0xFFFFFFFF, quadword >> 32)

#-=-=-=-#

class FileDate:
  SET_SILENT = False
  DDMMYYYY = True # dayfirst=True if YYYY is not at the beginning
  TIMESPEC = 'seconds' # or 'milliseconds' or 'microseconds' or 'auto' - see __str__
  windows = os.sys.platform.startswith("win")
  
  def __init__(self, file_name: str, expand_vars = False):
    if expand_vars:
      file_name = os.path.expandvars(file_name)    # Windows
      file_name = os.path.expanduser(file_name)    # Linux
      file_name = os.path.abspath(file_name)       # Full
    file_name = str(Path(file_name).resolve())   # Normalize

    self.file_name = file_name
    self.dict_tstamps = None # cache for get_st()

  def _UxW_timestamp(date: datetime):
    date_stamp = date.timestamp()
    if FileDate.windows:
      date_stamp = win_tstamp_(date_stamp)
    return date_stamp
    
  def _UxW_datetime(timestamp) -> datetime:
    if FileDate.windows:
      return datetime_win_(timestamp)
    else:
      return datetime.fromtimestamp(timestamp)

  def _modify(date_param: str):
    """Convert `.set()` parameter to Unix/Win timestamp 
    >>> FileDate._modify('1970-02-03') - FileDate._modify(parse('1970-02-03')) < 1
    True
    """
    if isinstance(date_param, str):
      dayfirst = FileDate.DDMMYYYY and not re.match(r'\d\d\d\d', date_param)
      date_param = FileDate._UxW_timestamp( parse(date_param, dayfirst=dayfirst) )
    elif isinstance(date_param, datetime):
      date_param = FileDate._UxW_timestamp( date_param )
    return date_param
    

  def get_st(self) -> dict:
    """get_st() -> dict:
  Returns a dictionary containing `timestamp` (Unix or Windows) 
  {'created': <timestamp>,... 'modified': <timestamp>, 'accessed': <timestamp>}
  """
    if self.dict_tstamps:
      return self.dict_tstamps # >>>>>>>>>>>>>
    
    dict = None
    
    if not FileDate.windows:
      info = os.stat(self.file_name)
      dict = {
        "created" : info.st_ctime,
        "modified": info.st_mtime,
        "accessed": info.st_atime
      }
    else:
      c_FileTime, m_FileTime, a_FileTime = (wintypes.FILETIME(0,0) for i in range(3))
      # FILE_READ_ATTRIBUTES=128, 0, None,OPEN_EXISTING=3,FILE_FLAG_BACKUP_SEMANTICS=0x02000000 (get handle to directory or file)
      handle = windll.kernel32.CreateFileW(self.file_name, 128, 0, None, 3, 0x02000000, None)
      if handle != -1: # != INVALID_HANDLE_VALUE:
        windll.kernel32.GetFileTime(handle, byref(c_FileTime), byref(a_FileTime), byref(m_FileTime)) 
        windll.kernel32.CloseHandle(handle)
        dict = {
          "created" : quadword_(c_FileTime),
          "modified": quadword_(m_FileTime),
          "accessed": quadword_(a_FileTime)
        }

    self.dict_tstamps = dict  # cache
    return dict
 

  def get(self) -> dict:
    """get() -> dict:
  Returns a dictionary containing `datetime.fromtimestamp` objects - 
  when file was {'created': datetime.datetime(2023,... 'modified': ... 'accessed': ...}
  """
    dict = self.get_st() 
    for Key, Value in dict.items():
      dict[Key] = FileDate._UxW_datetime(Value)
    return dict
    
    
  def __str__(self) -> str:
    di = self.get() 
    # NOT: di = FileDate(self.file_name).get() #
    return f'''{ {k: v.isoformat(' ', FileDate.TIMESPEC) for (k, v) in di.items()} }'''
  
  def __repr__(self):
    return str(self)

  #-=-=-=-#

  def set(self, modified: str = None, created: str = None, accessed: str = None):
    """set(modified: str = None, created: str = None, accessed: str = None):
  Sets new file dates.
  
  All parameters except `self.FileDate` support:
  - String datetime representations parsable by `dateutil.parser`
  - Epoch times - from 1970-01-01 for Unix (sec., float) and 1601-01-01 for Windows (100ns, quadword or int)
  
  `created` parameter works in Windows only.
  
  >>> file_date = FileDate('../test.txt')
  >>> print(file_date.set( created = "01.02.2000 12:00", modified = "2001/03/04", accessed = "2001-05-06"))
  {'created': '2000-02-01 12:00:00', 'modified': '2001-03-04 00:00:00', 'accessed': '2001-05-06 00:00:00'}
  >>> file_date = FileDate('../examples') # folder
  >>> print(file_date.set( created = "11.02.1981 12:00", modified = "3:40PM 1982/03/04", accessed = "5rd March 1983 20:21:22"))
  {'created': '1981-02-11 12:00:00', 'modified': '1982-04-03 15:40:00', 'accessed': '1983-03-05 20:21:22'}
  >>> print(FileDate('../test.txt')) # test for __str__(), get(), get_st() ## Unix - created is not set # doctest: +ELLIPSIS 
  {'created': '...', 'modified': '2001-03-04 00:00:00', 'accessed': '2001-05-06 00:00:00'}
  """
    if modified is None and created is None and accessed is None:
      return None
    
    #---#
    
    if not FileDate.windows:

      _ = self.get_st() # get self.dict_tstamps
      
      if created is not None: # not used for Unix file
        self.dict_tstamps["created"] = FileDate._modify(created)
      if modified is not None:
        self.dict_tstamps["modified"] = FileDate._modify(modified)
      if accessed is not None:
        self.dict_tstamps["accessed"] = FileDate._modify(accessed)
      [c_tstamp, m_tstamp, a_tstamp] = [ self.dict_tstamps[k] for k in ("created", "modified", "accessed")]

      #---#
      
      # if created is not None: 
      # https://github.com/jelmerwouters/filedate
      #   if os.sys.platform == 'darwin':  # Macos   # not tested ...
      #     command = 'SetFile -d "%s" "%s"' % (datetime.fromtimestamp(c_tstamp).strftime('%m/%d/%Y %H:%M:%S'), self.file)
      #     call(command, shell=True)

      # Setting Accessed & Modified Time
      # ?? os.chmod(self.file_name, 511)
      os.utime(self.file_name, (a_tstamp, m_tstamp))
      

    else: # Windows # https://devblogs.microsoft.com/oldnewthing/20111010-00/?p=9433
                    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfiletime
      dont_modify= filetime_( 0xFFFFFFFFFFFFFFFF )
      [c_FileTime, m_FileTime, a_FileTime] = \
        [ filetime_( FileDate._modify(k) if k is not None else 0) for k in (created, modified, accessed)]
      
      # FILE_WRITE_ATTRIBUTES=256, 0, None,OPEN_EXISTING=3,FILE_FLAG_BACKUP_SEMANTICS=0x02000000 (get handle to directory or file)
      handle = windll.kernel32.CreateFileW(self.file_name, 256, 0, None, 3, 0x02000000, None)
      windll.kernel32.SetFileTime(handle, None, byref(dont_modify), byref(dont_modify)) 
      windll.kernel32.SetFileTime(handle, byref(c_FileTime), byref(a_FileTime), byref(m_FileTime))
      windll.kernel32.CloseHandle(handle)
      
      self.dict_tstamps = None
      self.get_st() # set new values in self.dict_tstamps cache

    return None if FileDate.SET_SILENT else str(self)
    #    self #-> see __str__

  #-=-=-=-#
  
# File = FileDate

if __name__ == '__main__':
  FileDate.SET_SILENT = False
  #for f in [FileDate.get, FileDate.set]: print(f.__doc__)
  import doctest
  doctest.testmod()
  print('.')

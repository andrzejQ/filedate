## 1.0
- Initial release.

## 1.1
- Modified code structure.

## 1.2
- Code refraction.
- Bug fixes.

## 1.3
- Renamed:
  - `filedate.FileDate` to `filedate.File`
  - `filedate.Utils.release` to `filedate.Utils.drop`
- Reduced code size.

## 1.4
- `filedate.Utils.copy`
- Bug fixes.

## 1.5
- Bug fixes.

## 1.6
- `filedate.Utils.swap`
- Bug fixes.

## 1.7
- Bug fixes.

## 1.8
- `filedate.Utils.fromfile`

## 2.0
- Added `Batch` alias for `filedate.Utils.Keep`
- Modified program files structure.
- Modified `filedate.File` file path system.
- Removed `filedate.Utils.Swap`
- Removed `fromfn` alias from `filedate.Utils.fromname`
- Renamed `filedate.Utils.fromfile` to `filedate.Utils.Name`
- Support for setting dates to directories.
- Support for copying dates to directories.
- Bug fixes.

## 2.1
See  [jelmerwouters / filedate] (https://github.com/jelmerwouters/filedate) -> FileDate.set()  
(not tested here, commented)

## 2.2  
[andrzejQ / filedate](https://github.com/andrzejQ/filedate) 2023-03-23 .. 29
1. FromFileName - more cases
2. doctest
3. .get_st() -> dict:
  Returns a dictionary containing original `timestamp` (Unix or Windows) 
  - float (not int) in Linux, quadword in Windows
  {'created': <timestamp>,... 'modified': <timestamp>, 'accessed': <timestamp>}
  
If after saving a new LastWriteTime, the LastAccessTime is set to the current time, there is probably a process in the background that reads the contents of the file, for example TortoiseGit for a file under git control. In this case doctest will show errors.  (To stop TGitCache.exe open TortoiseGit Settings > Icon Overlays \ "None" \ [OK]).


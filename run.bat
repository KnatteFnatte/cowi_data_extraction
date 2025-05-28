@echo off
echo WARNING: The program can and will overwrite any previous output files in the same directory. Please make sure that previous files have either been remade, moved, or backed up to avoid deleting any previous data.
echo:
echo enter path to directory where output should be placed (if current working directory, press enter)
set /p cwd=Input:
echo:
if /i "%cwd%"=="" goto nocwd
goto cwd

:nocwd
echo in nocwd
echo enter path to directory with files (if target directory should be this directory, press enter)
set /p td=Input:
echo:
if /i "%td%"=="" goto notdnocwd
goto tdnocwd

:notdnocwd
python DataExtraction.py
pause
exit

:tdnocwd
python DataExtraction.py -td "%td%"
pause
exit

:cwd
echo in cwd
echo enter path to directory with files (if target directory should be this directory, press enter)
set /p td=Input:
echo:
if /i "%td%"=="" goto notdcwd
goto tdcwd

:notdcwd
python DataExtraction.py -cwd "%cwd%"
pause
exit

:tdcwd
python DataExtraction.py -td "%td%" -cwd "%cwd%"
pause
exit


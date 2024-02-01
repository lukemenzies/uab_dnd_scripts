@ECHO OFF

REM Batch file to create shortcuts for the DnD Shares on a Windows machine
REM Also checks for Python and if present installs setuptools and modules

SET "dndusername=none"
SET "dndpassword=none"
SET /p "dndusername=Enter the User Name:"
SET /p "dndpassword=Enter the Password:"
MKLINK "%USERPROFILE%\Map to H Drive (historical)" "C:\WINDOWS\System32\net.exe use H: \\138.26.152.9\historical_staging /user:%dndusername% %dndpassword%"

@echo off
setlocal enabledelayedexpansion
:: Batch file to be able to click on posting info on beancount's web interface and
:: automatically open up the source file at the place of that posting.
:: 
:: Ref: https://msdn.microsoft.com/en-us/library/aa767914(v=vs.85).aspx
:: 
:: Instructions:
:: 1) Edit the supplied beancounturi.reg file, and replace the string 'YOURUSERNAME'
::    with your Windows username
:: 2) Save the file to a known location and double click the file to install the
::    registry value
:: 3) In the lines below where indicated, replace 'YOURUSERNAME' with your username, and
::    replace the path if needed (usually not needed)
:: 4) In the last line below, replace the editor with the one of your choice installed
::    on your system, and its arguments as required
:: 5) Copy this .bat file to th C:\Users\YOURUSERNAME\beancountopen.bat (as indicated in
::    the .reg file)
:: 6) Clicking on a beancount:// uri in your browser (or in any other application)
::    should now open the file in your editor at the line name given
:: 
:: Notes: URI example: beancount:///home/YOURUSERNAME/beancount/Credit-Card.bc?lineno=647
:: This is changed to: "C:\Program Files (x86)\Vim\vim74\gvim.exe"  C:/Users/YOURUSERNAME/Documents/beancount/Credit-Card.bc +647
:: 

Set url=%1

:: Strip quotes
set url=%url:~1,-1%

:: Strip '"beanount://'
set url=%url:beancount://=%

:: Extract line number
set "find=*?"
call set lineno=%%url:!find!=%%
set "find=*lineno"
call set lineno=%%lineno:!find!=%%
set lineno=%lineno:~1%
:: echo %lineno%

:: Extract filename
call set file=%%url:!lineno!=%%
set file=%file:~0,-8%

:: REPLACE root directory with custom root (since cygwin paths are different from native
:: Windows paths)
Set "Pattern=/home/YOURUSERNAME"
Set "Replace=C:/Users/YOURUSERNAME/Documents/docs.sync/accounts/beancount"
Set "File=!File:%Pattern%=%Replace%!"

:: DEBUG:
:: echo File: %file%
:: echo Line: %lineno%

:: REPLACE this with the editor of your choice:
"C:\Program Files (x86)\Vim\vim74\gvim.exe" %file%   +%lineno%


@echo off

REM First, delete all previously compiled libraries
cd ../acs
if exist *.o del *.o

REM Now let's go to the source directory
cd ../acs_src
if exist *.o del *.o
if exist error.txt del error.txt

REM Compile all libraries
for %%v in (*.acs) do (
	acc %%v
	if exist acs.err ren acs.err error.txt
	if exist error.txt goto ACS_Error
)

goto ACS_No_Error

:ACS_No_Error

for %%v in (*.o) do (
	copy %%v ..\acs\%%v
)
if exist *.o del *.o
echo ACS compiled successfully.

REM Go to the ACS directory to do some cleaning up
cd ../acs

REM Generate the LOADACS
type NUL > ../loadacs.txt
echo // Generated automatically by build script, do not edit>>../loadacs.txt
for %%v in (*.o) do (
	echo %%~nv>>../loadacs.txt
)

goto ACS_All_Success

:ACS_Error

echo Errors found in compiling ACS libraries. Aborting...
error.txt
exit

:ACS_All_Success
echo All ACS scripts compiled successfully!

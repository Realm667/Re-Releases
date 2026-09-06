@echo off
setlocal
if exist "%~dp0tools\utnt-env.cmd" call "%~dp0tools\utnt-env.cmd"
if defined UTNT_PYTHON goto configured
where py >nul 2>nul
if not errorlevel 1 goto launcher
python "%~dp0tools\build_utnt.py" --root "%~dp0." %*
exit /b %errorlevel%
:launcher
py -3 "%~dp0tools\build_utnt.py" --root "%~dp0." %*
exit /b %errorlevel%
:configured
"%UTNT_PYTHON%" "%~dp0tools\build_utnt.py" --root "%~dp0." %*
exit /b %errorlevel%

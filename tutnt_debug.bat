@echo off
setlocal
if exist "%~dp0tools\utnt-env.cmd" call "%~dp0tools\utnt-env.cmd"
if not defined UTNT_ENGINE (
  echo Set UTNT_ENGINE and UTNT_IWAD in tools\utnt-env.cmd.
  exit /b 1
)
if not exist "%~dp0logs" mkdir "%~dp0logs"
"%UTNT_ENGINE%" -debug 19021 -iwad "%UTNT_IWAD%" -file "%~dp0tutnt" -config "%~dp0logs\debug.ini" -noautoload +vid_fullscreen false %*

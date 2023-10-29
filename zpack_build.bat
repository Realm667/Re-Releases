@echo off
7za a -tzip -x!".git" -xr!"*.dbs" -xr!"*.backup1" -xr!"*.backup2" -xr!"*.backup3" -xr!"*.psd" -xr!"*.otf" -xr!"*.ttf" zpack.pk3 .\zpack\*



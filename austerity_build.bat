@echo off
if exist austerity.pk3 del /q austerity.pk3
7za a -tzip -mx9 -x!".git" -xr!"*.dbs" -xr!"*.backup*" -xr!"*.autosave*" -xr!tools -xr!#PSD -x!.vscode\ -xr!"*.bat" -xr!"*.psd" -xr!"*.otf" -xr!"*.ttf" -xr!"*.rar" -xr!"*.zip" austerity.pk3 .\austerity.released-v31-20220907\*

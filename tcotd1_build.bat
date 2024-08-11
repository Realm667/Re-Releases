@echo off
7za a -tzip -mx0 -x!".git" -xr!"*.dbs" -xr!"*.backup*" -xr!"*.autosave*" -xr!tools -xr!#PSD -x!.vscode\ -xr!"*.bat" -xr!"*.psd" -xr!"*.otf" -xr!"*.ttf" -xr!"*.rar" -xr!"*.zip" tcotd1.pk3 .\tcotd1.released-v21-20220911\*

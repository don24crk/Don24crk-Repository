@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo  Flipper File - PyInstaller Build Kit
echo ==========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  set "PY=python"
)

%PY% --version >nul 2>nul
if errorlevel 1 goto :no_python

echo Installing or updating PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :pyinstaller_failed


echo.
echo Building CopyRAR-cmd...
%PY% -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --onefile ^
  --name "CopyRAR-cmd" ^
  "CopyRAR-cmd.py"

if errorlevel 1 goto :build_failed

echo.
echo ==========================================
echo Build complete.
echo Look in the dist folder for your app.
echo ==========================================
echo.
pause
exit /b 0

:no_python
echo.
echo Python was not found. Install Python for Windows first,
echo then re-run this build file.
pause
exit /b 1

:pyinstaller_failed
echo.
echo PyInstaller could not be installed or updated.
echo Check your internet connection and Python/pip setup.
pause
exit /b 1

:dependency_failed
echo.
echo One or more project dependencies failed to install.
echo Review requirements.txt and correct package names if needed.
pause
exit /b 1

:build_failed
echo.
echo The PyInstaller build failed.
echo Review the error output above and README.txt.
pause
exit /b 1

FLIPPER FILE - PYTHON TO EXE BUILD KIT
======================================

This kit does not contain a pre-built EXE.
It contains the files needed to build your application locally with PyInstaller.

IMPORTANT PLATFORM NOTE
-----------------------
To create a Windows EXE, run this kit on Windows.
PyInstaller is not a cross-compiler.

QUICK START
-----------
1. Install Python for Windows if it is not already installed.
2. Extract this ZIP to a normal writable folder.
3. Review requirements.txt. Dependency detection is heuristic.
4. Double-click build.bat.
5. When the build finishes, open the dist folder.

PROJECT SETTINGS
----------------
Entry script: CopyRAR-cmd.py
Application name: CopyRAR-cmd
Bundle type: One-file EXE
Window type: Console application
Icon: Default PyInstaller icon

LIKELY THIRD-PARTY DEPENDENCIES
--------------------------------
None detected

HIDDEN IMPORTS
--------------
None

COLLECT-ALL PACKAGES
--------------------
None

BUNDLED DATA FILES
------------------
  None

BUILD COMMAND
-------------
python -m PyInstaller --clean --noconfirm --onefile --name "CopyRAR-cmd" "CopyRAR-cmd.py"

TROUBLESHOOTING
---------------
- If a package fails to install, correct its name in requirements.txt and run build.bat again.
- If the EXE reports a missing module, add that module to Hidden imports in the Flipper File tool, regenerate the kit, and rebuild.
- If a package needs extra data/binaries, add it to Collect all or use a custom PyInstaller hook/spec file.
- For GUI applications, choose GUI / no console. For debugging, console mode is usually easier.
- One-file applications unpack themselves to a temporary folder at runtime; bundled data should be accessed using paths relative to __file__ when possible.

FILES IN THIS KIT
-----------------
CopyRAR-cmd.py       Main Python source
requirements.txt      Suggested third-party dependencies
build.bat             Windows build script
CopyRAR-cmd.spec       Advanced PyInstaller spec starter
pyinstaller-command.txt Direct command for manual builds
README.txt            This file



Generated locally by Flipper File.

import sys
import os
from cx_Freeze import setup, Executable

# Automatische Erkennung von zusätzlichen Dateien im aktuellen Verzeichnis
extra_files = []
for file_name in ["CopyRAR-cmd.exe", "7z.exe", "Rar.exe", "about_banner.png"]:
    if os.path.exists(file_name):
        # Kopiert die Datei direkt in das Hauptverzeichnis des Build-Ordners
        extra_files.append((file_name, file_name))

# Definition der Build-Optionen
build_exe_options = {
    # Alle für die Windows-Shell und Tkinter benötigten Module erzwingen
    "includes": ["win32api", "win32con", "tkinter"],
    "packages": ["win32com.shell", "tkinter.filedialog", "tkinter.ttk"],
    "include_files": extra_files,  # Fügt die erkannten Begleitdateien automatisch hinzu
    "excludes": []
}

# Verhindert das Aufpoppen des schwarzen CMD-Konsolenfensters im Hintergrund unter Windows
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name = "CopyRAR_Professional",
    version = "1.0",
    description = "CopyRAR Professional - Freeware Packprogramm von don24crk",
    options = {"build_exe": build_exe_options},
    executables = [
        Executable(
            "CopyRAR_Professional.py", 
            base=base,
            target_name="CopyRAR_Professional.exe"  # Name der fertigen ausführbaren Datei
        )
    ]
)

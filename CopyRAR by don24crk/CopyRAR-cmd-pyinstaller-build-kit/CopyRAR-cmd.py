#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  Copyrar - Universal CLI Archiver & Extractor
  Copyright (c) 02-10-2026 by don24crk
================================================================================
"""

import os
import sys
import argparse
import subprocess
import shutil

# Konstanten
PROGRAM_NAME = "Copyrar"
CODED_BY = "don24crk"
VERSION = "1.0"
COPYRIGHT = "Copyright (c) 2-10-2026 by don24crk"

# Einfache ANSI-Farben für die CLI-Ausgabe
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""{Colors.HEADER}
  ============================================================
    ____                                     
   / ___|___  _ __  _   _ _ __  __ _ _ __    

  | |   / _ \| '_ \| | | | '__|/ _` | '__|   
  | |__| (_) | |_) | |_| | |  | (_| | |      
   \____\___/| .__/ \__, |_|   \__,_|_|      

             |_|    |___/                    
  ============================================================
  Tool       : {PROGRAM_NAME} (Win32 CLI Tool)
  Version    : {VERSION}
  Coded by   : {CODED_BY}
  Legal      : {COPYRIGHT}
  Supports   : 7z, rar, rar5, zip, tar.gz
  ============================================================{Colors.ENDC}"""
    print(banner)

def get_executable(name):
    """Überprüft, ob das Executable im aktuellen Verzeichnis oder PATH existiert."""
    # Zuerst im aktuellen Skript-Verzeichnis suchen
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if os.path.exists(local_path):
        return local_path
    if os.path.exists(name):
        return name
    
    # Im System-PATH suchen
    path_executable = shutil.which(name)
    if path_executable:
        return path_executable
    return None

def check_dependencies():
    """Überprüft die Verfügbarkeit von 7z.exe und rar.exe."""
    seven_zip = get_executable("7z.exe")
    rar = get_executable("rar.exe")
    
    missing = []
    if not seven_zip:
        missing.append("7z.exe")
    if not rar:
        missing.append("rar.exe")
        
    if missing:
        print(f"{Colors.WARNING}[!] Warnung: Die folgenden Abhängigkeiten wurden nicht im Pfad gefunden: {', '.join(missing)}{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Stellen Sie sicher, dass sie sich im selben Ordner oder im System-PATH befinden.{Colors.ENDC}\n")
    
    return seven_zip, rar

def handle_zip(archive_path, source_paths, seven_zip_exe, rar_exe):
    """Erstellt Archive basierend auf der Dateiendung."""
    ext = "".join(os.path.splitext(archive_path.lower())[1:])
    
    # Sonderfall für .tar.gz
    if archive_path.lower().endswith('.tar.gz'):
        ext = '.tar.gz'

    print(f"{Colors.OKBLUE}[*] Packe Dateien in ein {ext.upper()}-Archiv...{Colors.ENDC}")

    # Logik für RAR und RAR5
    if ext == '.rar':
        if not rar_exe:
            print(f"{Colors.FAIL}[-] Fehler: rar.exe wird für dieses Format benötigt!{Colors.ENDC}")
            return False
        cmd = [rar_exe, 'a', '-r', archive_path] + source_paths

    # Logik für 7Z und ZIP
    elif ext in ['.7z', '.zip']:
        if not seven_zip_exe:
            print(f"{Colors.FAIL}[-] Fehler: 7z.exe wird für dieses Format benötigt!{Colors.ENDC}")
            return False
        cmd = [seven_zip_exe, 'a', '-r', archive_path] + source_paths

    # Logik für TAR.GZ
    elif ext == '.tar.gz':
        if not seven_zip_exe:
            print(f"{Colors.FAIL}[-] Fehler: 7z.exe wird für dieses Format benötigt!{Colors.ENDC}")
            return False
        
        # 7z benötigt zwei Schritte für tar.gz
        temp_tar = archive_path[:-3] 
        print(f"{Colors.OKBLUE}[*] Schritt 1: Erstelle temporäres TAR-Archiv...{Colors.ENDC}")
        cmd_tar = [seven_zip_exe, 'a', '-ttar', temp_tar] + source_paths
        
        res = subprocess.run(cmd_tar)
        if res.returncode != 0:
            return False
        
        print(f"{Colors.OKBLUE}[*] Schritt 2: Komprimiere TAR zu GZ...{Colors.ENDC}")
        cmd = [seven_zip_exe, 'a', '-tgzip', archive_path, temp_tar]
        res_gz = subprocess.run(cmd)
        
        # Temporäre TAR-Datei aufräumen
        if os.path.exists(temp_tar):
            os.remove(temp_tar)
            
        return res_gz.returncode == 0

    else:
        print(f"{Colors.FAIL}[-] Fehler: Nicht unterstütztes Ausgabeformat: {ext}{Colors.ENDC}")
        return False

    # Befehl ausführen
    process = subprocess.run(cmd)
    return process.returncode == 0

def handle_extract(archive_path, output_dir, seven_zip_exe, rar_exe):
    """Entpackt Archive basierend auf dem Format."""
    if not os.path.exists(archive_path):
        print(f"{Colors.FAIL}[-] Fehler: Archiv '{archive_path}' existiert nicht.{Colors.ENDC}")
        return False

    ext = os.path.splitext(archive_path.lower())
    if archive_path.lower().endswith('.tar.gz'):
        ext = '.tar.gz'

    print(f"{Colors.OKBLUE}[*] Entpacke Archiv: {archive_path}...{Colors.ENDC}")
    
    if not output_dir:
        output_dir = "."

    # RAR-Archive bevorzugt mit rar.exe (wegen bestem RAR5 Support)
    if ext == '.rar':
        if rar_exe:
            cmd = [rar_exe, 'x', '-y', archive_path, output_dir + "\\"]
        elif seven_zip_exe:
            print(f"{Colors.WARNING}[!] rar.exe fehlt. Versuche über 7z.exe zu entpacken...{Colors.ENDC}")
            cmd = [seven_zip_exe, 'x', f'-o{output_dir}', '-y', archive_path]
        else:
            print(f"{Colors.FAIL}[-] Fehler: Kein Entpacker (rar.exe oder 7z.exe) vorhanden!{Colors.ENDC}")
            return False

    # Alle anderen Formate über 7z.exe handhaben
    elif ext in ['.7z', '.zip', '.tar.gz', '.gz', '.tar']:
        if not seven_zip_exe:
            print(f"{Colors.FAIL}[-] Fehler: 7z.exe wird für dieses Format benötigt!{Colors.ENDC}")
            return False
        cmd = [seven_zip_exe, 'x', f'-o{output_dir}', '-y', archive_path]
    else:
        if seven_zip_exe:
            cmd = [seven_zip_exe, 'x', f'-o{output_dir}', '-y', archive_path]
        else:
            print(f"{Colors.FAIL}[-] Fehler: Unbekanntes Format und 7z.exe fehlt.{Colors.ENDC}")
            return False

    process = subprocess.run(cmd)
    
    # Zusätzlicher Entpackungsschritt falls es eine verschachtelte .tar.gz war
    if ext == '.tar.gz' and process.returncode == 0:
        expected_tar = os.path.join(output_dir, os.path.splitext(os.path.basename(archive_path)))
        if os.path.exists(expected_tar) and expected_tar.lower().endswith('.tar'):
            print(f"{Colors.OKBLUE}[*] Schritt 2: Entpacke extrahierte TAR-Datei...{Colors.ENDC}")
            cmd_tar = [seven_zip_exe, 'x', f'-o{output_dir}', '-y', expected_tar]
            process_tar = subprocess.run(cmd_tar)
            os.remove(expected_tar) 
            return process_tar.returncode == 0

    return process.returncode == 0

def main():
    print_banner()
    seven_zip_exe, rar_exe = check_dependencies()
    
    parser = argparse.ArgumentParser(
        description=f"Copyrar {VERSION} - {COPYRIGHT}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--add', action='store_true', help='Dateien zu einem Archiv hinzufügen (Packen)')
    group.add_argument('-x', '--extract', action='store_true', help='Archiv extrahieren (Entpacken)')
    
    parser.add_argument('-f', '--archive', required=True, help='Pfad zur Archivdatei (z.B. archiv.rar, archiv.7z)')
    parser.add_argument('-o', '--output', help='Ausgabeverzeichnis für Entpacken (Standard: aktueller Ordner)')
    parser.add_argument('files', nargs='*', help='Liste von Dateien oder Ordnern, die gepackt werden sollen')

    args = parser.parse_args()

    # Ausführung: Packen
    if args.add:
        if not args.files:
            print(f"{Colors.FAIL}[-] Fehler: Keine Dateien oder Ordner zum Packen angegeben!{Colors.ENDC}")
            sys.exit(1)
        
        success = handle_zip(args.archive, args.files, seven_zip_exe, rar_exe)
        if success:
            print(f"\n{Colors.OKGREEN}[+] Archiv erfolgreich erstellt: {args.archive}{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}[-] Fehler beim Erstellen des Archivs.{Colors.ENDC}")
            sys.exit(1)

    # Ausführung: Entpacken
    elif args.extract:
        success = handle_extract(args.archive, args.output, seven_zip_exe, rar_exe)
        if success:
            print(f"\n{Colors.OKGREEN}[+] Archiv erfolgreich entpackt!{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}[-] Fehler beim Entpacken des Archivs.{Colors.ENDC}")
            sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        os.system('color')
    main()

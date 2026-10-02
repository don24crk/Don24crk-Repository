import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import win32con
from win32com.shell import shell, shellcon

class CopyRARProfessionalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CopyRAR Professional")
        self.root.geometry("800x600")
        
        # Aktuellen Pfad bestimmen
        self.current_dir = os.path.expanduser("~\\Downloads")
        
        # Pfade zu den Pack-Executables und Assets ermitteln (wichtig für cx_Freeze)
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Zentrale Zuweisung der CopyRAR-cmd.exe und Helfer-Bibliotheken
        self.path_to_copyrar_cmd = os.path.join(self.base_dir, "CopyRAR-cmd.exe")
        self.path_to_7z = os.path.join(self.base_dir, "7z.exe")
        self.path_to_rar = os.path.join(self.base_dir, "Rar.exe")
        self.banner_path = os.path.join(self.base_dir, "about_banner.png")
        
        # 1. Menüleiste & Toolbar
        self.create_toolbar()
        
        # 2. Adresszeile
        self.address_var = tk.StringVar(value=self.current_dir)
        address_bar = tk.Entry(self.root, textvariable=self.address_var, font=("Segoe UI", 10))
        address_bar.pack(fill=tk.X, padx=5, pady=2)
        address_bar.bind("<Return>", self.on_address_enter)

        # 3. Haupt-Dateiliste (TreeView)
        self.tree = ttk.Treeview(self.root, columns=("Größe", "Typ", "Geändert"), show="tree headings")
        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.heading("Größe", text="Größe", anchor=tk.E)
        self.tree.heading("Typ", text="Typ", anchor=tk.W)
        self.tree.heading("Geändert", text="Geändert", anchor=tk.W)
        
        self.tree.column("#0", width=250, anchor=tk.W)
        self.tree.column("Größe", width=100, anchor=tk.E)
        self.tree.column("Typ", width=120, anchor=tk.W)
        self.tree.column("Geändert", width=150, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Events binden
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 4. Kontextmenü erstellen
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Öffnen", command=self.open_selected)
        self.context_menu.add_command(label="Zum Archiv hinzufügen...", command=self.add_to_archive)
        self.context_menu.add_command(label="Hier entpacken", command=self.extract_here)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Eigenschaften", command=self.show_properties)

        self.load_directory(self.current_dir)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        
        btn_add = tk.Button(toolbar, text="Hinzufügen", compound=tk.TOP, command=self.add_to_archive)
        btn_add.pack(side=tk.LEFT, padx=5, pady=2)
        
        btn_extract = tk.Button(toolbar, text="Entp. nach", compound=tk.TOP, command=self.extract_here)
        btn_extract.pack(side=tk.LEFT, padx=5, pady=2)
        
        btn_about = tk.Button(toolbar, text="Info", compound=tk.TOP, command=self.show_about_dialog)
        btn_about.pack(side=tk.LEFT, padx=5, pady=2)
        
        toolbar.pack(fill=tk.X)

    def show_about_dialog(self):
        """Öffnet das Info-Fenster im CopyRAR Professional Stil"""
        about_win = tk.Toplevel(self.root)
        about_win.title("Über CopyRAR Professional")
        about_win.geometry("420x340")
        about_win.resizable(False, False)
        about_win.transient(self.root)
        about_win.grab_set()
        
        # --- 1. Der CopyRAR Banner ---
        banner_frame = tk.Frame(about_win, width=400, height=80, bg="#1a4f8a", bd=1, relief=tk.SUNKEN)
        banner_frame.pack(fill=tk.X, padx=10, pady=10)
        banner_frame.pack_propagate(False)
        
        if os.path.exists(self.banner_path):
            try:
                self.banner_img = tk.PhotoImage(file=self.banner_path)
                lbl_banner = tk.Label(banner_frame, image=self.banner_img, bg="#1a4f8a")
                lbl_banner.pack(fill=tk.BOTH, expand=True)
            except Exception:
                lbl_title = tk.Label(banner_frame, text="★ CopyRAR ★", font=("Segoe UI", 16, "bold"), fg="white", bg="#1a4f8a")
                lbl_title.pack(expand=True)
        else:
            lbl_title = tk.Label(banner_frame, text="★ CopyRAR Banner ★", font=("Segoe UI", 14, "bold"), fg="white", bg="#1a4f8a")
            lbl_title.pack(expand=True)
            
        # --- 2. Informationstexte im Freeware-Stil ---
        info_frame = tk.Frame(about_win)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        lbl_app_name = tk.Label(info_frame, text="CopyRAR Professional v1.00 (64-Bit)", font=("Segoe UI", 11, "bold"))
        lbl_app_name.pack(anchor=tk.W, pady=(5, 2))
        
        lbl_credits = tk.Label(info_frame, text="coded by don24crk", font=("Segoe UI", 10, "italic"), fg="#0066cc")
        lbl_credits.pack(anchor=tk.W, pady=(0, 10))
        
        # Trennlinie
        sep = ttk.Separator(info_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=5)
        
        license_text = (
            "Dieses Programm ist offiziell als Freeware lizenziert. "
            "Es darf sowohl für private als auch für kommerzielle Zwecke "
            "vollkommen kostenlos und zeitlich unbegrenzt genutzt werden.\n\n"
            "Registriert für: don24crk Community-Edition\n"
            "Lizenztyp: Unbegrenzte, freie Vollversion"
        )
        
        text_widget = tk.Text(info_frame, wrap=tk.WORD, font=("Segoe UI", 9), height=6, bg=about_win.cget("bg"), bd=0)
        text_widget.insert(tk.END, license_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.X, pady=5)
        
        # --- 3. OK Schließen-Button ---
        btn_ok = tk.Button(about_win, text="OK", width=12, command=about_win.destroy, font=("Segoe UI", 9))
        btn_ok.pack(side=tk.BOTTOM, pady=10)

    def load_directory(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            return
        self.current_dir = path
        self.address_var.set(path)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.tree.insert("", tk.END, iid="..", text="..", values=("", "Dateiordner", ""))

        try:
            for entry in os.scandir(path):
                stat = entry.stat()
                size = f"{stat.st_size:,} Bytes" if entry.is_file() else ""
                ftype = "Anwendung" if entry.name.endswith(".exe") else ("Dateiordner" if entry.is_dir() else "Datei")
                mtime = "02.10.2026 16:54"
                self.tree.insert("", tk.END, iid=entry.path, text=entry.name, values=(size, ftype, mtime))
        except Exception as e:
            print(f"Fehler: {e}")

    def on_double_click(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        if selected_item == "..":
            self.load_directory(os.path.dirname(self.current_dir))
        elif os.path.isdir(selected_item):
            self.load_directory(selected_item)
        else:
            os.startfile(selected_item)

    def add_to_archive(self):
        """Pack-Logik gesteuert über CopyRAR-cmd.exe in Verbindung mit 7z/Rar"""
        selected_item = self.tree.focus()
        if not selected_item or selected_item == "..":
            messagebox.showwarning("CopyRAR", "Bitte wählen Sie zuerst eine Datei oder einen Ordner aus!")
            return

        archive_path = filedialog.asksaveasfilename(
            initialdir=self.current_dir,
            title="Archivname und Typ auswählen",
            filetypes=[
                ("RAR-Archiv (*.rar)", "*.rar"),
                ("RAR5-Archiv (*.rar)", "*.rar"),
                ("ZIP-Archiv (*.zip)", "*.zip"),
                ("7-Zip Archiv (*.7z)", "*.7z"),
                ("GZipped Tar-Archiv (*.tar.gz)", "*.tar.gz")
            ]
        )
        if not archive_path:
            return

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if not os.path.exists(self.path_to_copyrar_cmd):
            messagebox.showerror("CopyRAR Fehler", "CopyRAR-cmd.exe wurde im Programmverzeichnis nicht gefunden!")
            return

        try:
            if archive_path.endswith(".tar.gz"):
                if not os.path.exists(self.path_to_7z):
                    raise FileNotFoundError("7z.exe fehlt im Programmverzeichnis!")
                base_archive_path = archive_path[:-3]
                # Schritt 1: TAR erzeugen
                cmd_tar = [self.path_to_copyrar_cmd, "7z", "a", "-ttar", base_archive_path, selected_item]
                subprocess.Popen(cmd_tar, startupinfo=startupinfo).communicate()
                # Schritt 2: GZIP komprimieren
                cmd_gz = [self.path_to_copyrar_cmd, "7z", "a", "-tgzip", archive_path, base_archive_path]
                process = subprocess.Popen(cmd_gz, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if os.path.exists(base_archive_path):
                    os.remove(base_archive_path)

            elif archive_path.endswith(".rar"):
                if not os.path.exists(self.path_to_rar):
                    raise FileNotFoundError("Rar.exe fehlt im Programmverzeichnis!")
                # -ma5 erzwingt standardmäßig das RAR5-Format
                cmd = [self.path_to_copyrar_cmd, "rar", "a", "-ma5", archive_path, selected_item]

process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
elif archive_path.endswith((".zip", ".7z")):
if not os.path.exists(self.path_to_7z):
raise FileNotFoundError("7z.exe fehlt im Programmverzeichnis!")
cmd = [self.path_to_copyrar_cmd, "7z", "a", archive_path, selected_item]
process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
else:
return
if process.returncode == 0:
messagebox.showinfo("CopyRAR", "Archiv erfolgreich über CopyRAR-cmd erstellt!")
self.load_directory(self.current_dir)
else:
messagebox.showerror("Fehler beim Packen", stderr.decode('cp1252', errors='ignore'))
except Exception as e:
messagebox.showerror("Systemfehler", str(e))
def extract_here(self):
"""Entpack-Logik gesteuert über CopyRAR-cmd.exe"""
selected_item = self.tree.focus()
if not selected_item or selected_item == "..":
messagebox.showwarning("CopyRAR", "Bitte wählen Sie zuerst ein Archiv aus!")
return
is_tar_gz = selected_item.lower().endswith(".tar.gz")
ext = os.path.splitext(selected_item).lower()
if ext not in [".rar", ".zip", ".7z"] and not is_tar_gz:
messagebox.showwarning("CopyRAR", "Das ausgewählte Element ist kein unterstütztes Archiv!")
return
destination_dir = filedialog.askdirectory(initialdir=self.current_dir, title="Zielordner zum Entpacken auswählen")
if not destination_dir:
return
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
if not os.path.exists(self.path_to_copyrar_cmd):
messagebox.showerror("CopyRAR Fehler", "CopyRAR-cmd.exe fehlt!")
return
try:
if is_tar_gz:
if not os.path.exists(self.path_to_7z):
raise FileNotFoundError("7z.exe fehlt im Programmverzeichnis!")
cmd_gz = [self.path_to_copyrar_cmd, "7z", "x", "-y", f"-o{destination_dir}", selected_item]
subprocess.Popen(cmd_gz, startupinfo=startupinfo).communicate()
extracted_tar_name = os.path.basename(selected_item)[:-3]
extracted_tar_path = os.path.join(destination_dir, extracted_tar_name)
if os.path.exists(extracted_tar_path):
cmd_tar = [self.path_to_copyrar_cmd, "7z", "x", "-y", f"-o{destination_dir}", extracted_tar_path]
process = subprocess.Popen(cmd_tar, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
os.remove(extracted_tar_path)
else:
raise FileNotFoundError("Interner Tar-Entpackungsfehler über CopyRAR-cmd.")
elif ext == ".rar":
if not os.path.exists(self.path_to_rar):
raise FileNotFoundError("Rar.exe fehlt im Programmverzeichnis!")
cmd = [self.path_to_copyrar_cmd, "rar", "x", "-y", selected_item, destination_dir + "/"]
process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
elif ext in [".zip", ".7z"]:
if not os.path.exists(self.path_to_7z):
raise FileNotFoundError("7z.exe fehlt im Programmverzeichnis!")
cmd = [self.path_to_copyrar_cmd, "7z", "x", "-y", f"-o{destination_dir}", selected_item]
process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
# Syntaxfehler behoben: Explizite Prüfung auf den Code 0 (und Code 1 als Warnungs-Erfolg bei 7z)
if process.returncode in:
messagebox.showinfo("CopyRAR", "Archiv erfolgreich entpackt!")
self.load_directory(self.current_dir)
else:
messagebox.showerror("Fehler beim Entpacken", stderr.decode('cp1252', errors='ignore'))
except Exception as e:
messagebox.showerror("Systemfehler", str(e))
def show_context_menu(self, event):
item = self.tree.identify_row(event.y)
if item:
self.tree.selection_set(item)
self.tree.focus(item)
self.context_menu.post(event.x_root, event.y_root)
def show_properties(self):
selected_item = self.tree.focus()
if not selected_item or selected_item == "..":
return
shell.ShellExecuteEx(
lpVerb='properties', lpFile=os.path.abspath(selected_item),
nShow=win32con.SW_SHOW, fMask=shellcon.SEE_MASK_INVOKEIDLIST
)
def open_selected(self): self.on_double_click(None)
def on_address_enter(self, event): self.load_directory(self.address_var.get())
if name == "main":
root = tk.Tk()
app = CopyRARProfessionalApp(root)
root.mainloop()

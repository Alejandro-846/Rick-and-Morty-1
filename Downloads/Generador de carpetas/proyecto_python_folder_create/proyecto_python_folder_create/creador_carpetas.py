from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import zipfile
import os
import threading
from PIL import Image, ImageDraw, ImageTk
import io
import json
import winsound
from datetime import datetime
from dataclasses import dataclass, asdict

# ==================== TEMAS ====================
THEMES = {
    "dark": {
        "bg": "#0f1419",
        "bg_secondary": "#1a2332",
        "accent": "#9b6dd1",
        "accent_dark": "#7a4ba6",
        "text": "#ffffff",
        "text_secondary": "#b0b8c1",
        "success": "#27ae60",
        "error": "#e74c3c",
        "warning": "#f39c12",
        "input_bg": "#0a0e14",
        "button_hover": "#2a3d52",
    },
    "light": {
        "bg": "#f5f5f5",
        "bg_secondary": "#e8e8e8",
        "accent": "#8b5fbf",
        "accent_dark": "#6d4a9f",
        "text": "#1a1a1a",
        "text_secondary": "#5a5a5a",
        "success": "#28a745",
        "error": "#dc3545",
        "warning": "#ffc107",
        "input_bg": "#ffffff",
        "button_hover": "#d0d0d0",
    }
}

CONFIG_FILE = Path(__file__).parent / "config.json"

@dataclass
class Operation:
    """Registro de operación"""
    timestamp: str
    tipo: str
    descripcion: str
    estado: str
    
    def to_dict(self):
        return asdict(self)

class CompressionWorker(threading.Thread):
    """Thread worker para comprimir sin bloquear UI"""
    def __init__(self, inv_dir, zip_path, compression_level, callback, error_callback):
        super().__init__(daemon=True)
        self.inv_dir = inv_dir
        self.zip_path = zip_path
        self.compression_level = compression_level
        self.callback = callback
        self.error_callback = error_callback
    
    def run(self):
        try:
            def _add_empty_dir(zipf, arcdir):
                info = zipfile.ZipInfo(str(arcdir).replace("\\", "/") + "/")
                zipf.writestr(info, b"")
            
            with zipfile.ZipFile(self.zip_path, "w", compression=self.compression_level) as zf:
                total_files = sum([len(files) for _, _, files in os.walk(self.inv_dir)])
                processed = 0
                
                for root, dirs, files in os.walk(self.inv_dir):
                    root_path = Path(root)
                    for d in dirs:
                        dir_path = root_path / d
                        arcdir = dir_path.relative_to(self.inv_dir.parent)
                        _add_empty_dir(zf, arcdir)
                    
                    for f in files:
                        file_path = root_path / f
                        arcname = file_path.relative_to(self.inv_dir.parent)
                        zf.write(file_path, arcname)
                        processed += 1
                        if total_files > 0:
                            progress = (processed / total_files) * 100
                            self.callback(progress, self.inv_dir.name)
            
            self.callback(100, self.inv_dir.name)
        except Exception as e:
            self.error_callback(str(e), self.inv_dir.name)

class StyledButton(tk.Button):
    """Botón con estilo Cathaleia y animaciones"""
    def __init__(self, parent, text, command, primary=False, theme_colors=None, **kwargs):
        self.primary = primary
        self.theme = theme_colors or THEMES["dark"]
        self.normal_bg = self.theme["accent"] if primary else self.theme["bg_secondary"]
        self.hover_bg = self.theme["accent_dark"] if primary else self.theme["button_hover"]
        
        super().__init__(
            parent, text=text, command=command,
            bg=self.normal_bg, fg=self.theme["text"],
            font=('Segoe UI', 11, 'bold' if primary else 'normal'),
            relief='flat', bd=0, padx=25, pady=12,
            cursor='hand2', activebackground=self.hover_bg,
            activeforeground=self.theme["text"], **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.configure(bg=self.normal_bg)
    
    def update_theme(self, theme_colors):
        """Actualizar tema en tiempo real"""
        self.theme = theme_colors
        self.normal_bg = self.theme["accent"] if self.primary else self.theme["bg_secondary"]
        self.hover_bg = self.theme["accent_dark"] if self.primary else self.theme["button_hover"]
        self.configure(bg=self.normal_bg, fg=self.theme["text"])

class ComprensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compresor de Carpetas CT/INV")
        self.root.geometry("1000x900")
        self.root.minsize(700, 600)
        self.root.resizable(True, True)
        
        self.ruta_destino = Path.cwd()
        self.compression_level = zipfile.ZIP_DEFLATED
        self.icon_image = None
        self.current_theme = "dark"
        self.operations_history = []
        self.buttons = []
        
        self._load_config()
        self._load_icon()
        self._center_window()
        self._create_ui()
        self._bind_keyboard_shortcuts()
    
    def _load_config(self):
        """Cargar configuración guardada"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "dark")
                    self.ruta_destino = Path(config.get("last_path", str(Path.cwd())))
                    self.operations_history = [
                        Operation(**op) for op in config.get("history", [])
                    ][-10:]
        except Exception as e:
            print(f"Error cargando config: {e}")
    
    def _save_config(self):
        """Guardar configuración"""
        try:
            config = {
                "theme": self.current_theme,
                "last_path": str(self.ruta_destino),
                "history": [op.to_dict() for op in self.operations_history[-10:]]
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando config: {e}")
    
    def _load_icon(self):
        """Cargar ícono desde cathaleia.png"""
        try:
            icon_path = Path(__file__).parent / "cathaleia.png"
            if icon_path.exists():
                img = Image.open(icon_path)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                self.icon_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error al cargar ícono: {e}")
    
    def _center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 500
        y = (self.root.winfo_screenheight() // 2) - 450
        self.root.geometry(f'+{x}+{y}')
    
    def _bind_keyboard_shortcuts(self):
        """Atajos de teclado para accesibilidad"""
        self.root.bind("<Control-t>", lambda e: self._toggle_theme())
        self.root.bind("<Control-h>", lambda e: self._show_history())
    
    def _toggle_theme(self):
        """Cambiar entre tema oscuro y claro"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        theme = THEMES[self.current_theme]
        
        self.root.configure(bg=theme["bg"])
        self._update_theme_recursive(self.root, theme)
        
        self._play_sound(440, 100)
        self._save_config()
    
    def _update_theme_recursive(self, widget, theme):
        """Actualizar tema recursivamente"""
        try:
            if isinstance(widget, StyledButton):
                widget.update_theme(theme)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg"])
            elif isinstance(widget, tk.Label):
                if widget.cget("bg") in [THEMES["dark"]["bg"], THEMES["light"]["bg"]]:
                    widget.configure(bg=theme["bg"], fg=theme["text"])
                elif widget.cget("bg") in [THEMES["dark"]["bg_secondary"], THEMES["light"]["bg_secondary"]]:
                    widget.configure(bg=theme["bg_secondary"], fg=theme["text"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=theme["input_bg"], fg=theme["text"], insertbackground=theme["accent"])
        except:
            pass
        
        for child in widget.winfo_children():
            self._update_theme_recursive(child, theme)
    
    def _play_sound(self, frequency=800, duration=100):
        """Reproducir sonido de notificación"""
        try:
            winsound.Beep(frequency, duration)
        except:
            pass
    
    def _create_ui(self):
        """Crear interfaz estilo Cathaleia - Layout 2 columnas"""
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["bg"])
        
        main_frame = tk.Frame(self.root, bg=theme["bg"])
        main_frame.pack(fill="both", expand=True)
        
        # === HEADER ===
        header = tk.Frame(main_frame, bg=theme["bg"])
        header.pack(fill="x", pady=(15, 15), padx=20)
        
        header_container = tk.Frame(header, bg=theme["bg"])
        header_container.pack(fill="x", pady=(0, 10))
        
        text_frame = tk.Frame(header_container, bg=theme["bg"])
        text_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(text_frame, text="COMPRESOR DE", font=('Segoe UI', 24, 'bold'),
                bg=theme["bg"], fg=theme["text"]).pack(anchor="w")
        
        title_frame = tk.Frame(text_frame, bg=theme["bg"])
        title_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(title_frame, text="CARPETAS", font=('Segoe UI', 24, 'bold'),
                bg=theme["bg"], fg=theme["text"]).pack(side="left")
        tk.Label(title_frame, text="CT/INV", font=('Segoe UI', 24, 'bold'),
                bg=theme["bg"], fg=theme["accent"]).pack(side="left", padx=(10, 0))
        
        if self.icon_image:
            icon_frame = tk.Frame(header_container, bg=theme["bg"])
            icon_frame.pack(side="right", padx=(20, 0))
            tk.Label(icon_frame, image=self.icon_image, bg=theme["bg"]).pack()
        
        # Controles del tema
        controls_frame = tk.Frame(header, bg=theme["bg"])
        controls_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(controls_frame, text="Tema:", font=('Segoe UI', 9),
                bg=theme["bg"], fg=theme["text_secondary"]).pack(side="left", padx=(0, 5))
        
        theme_btn = tk.Button(controls_frame, text="🌙 Oscuro" if self.current_theme == "dark" else "☀️ Claro",
                             command=self._toggle_theme, bg=theme["accent"], fg=theme["text"],
                             font=('Segoe UI', 9, 'bold'), relief='flat', bd=0, padx=12, pady=6, cursor='hand2')
        theme_btn.pack(side="left")
        
        tk.Label(controls_frame, text=" | Ctrl+T para cambiar | Ctrl+H para historial",
                font=('Segoe UI', 8), bg=theme["bg"], fg=theme["text_secondary"]).pack(side="left", padx=5)
        
        tk.Label(header, text="Organiza y comprime tus carpetas con facilidad",
                font=('Segoe UI', 9), bg=theme["bg"], fg=theme["text_secondary"]).pack(anchor="w")
        
        sep = tk.Frame(main_frame, bg=theme["accent"], height=1)
        sep.pack(fill="x", pady=(0, 15))
        
        # === CONTENEDOR DE 2 COLUMNAS ===
        content_frame = tk.Frame(main_frame, bg=theme["bg"])
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        left_column = tk.Frame(content_frame, bg=theme["bg"])
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self._create_section(left_column, "Crear Carpetas", self._build_create_section, theme)
        
        right_column = tk.Frame(content_frame, bg=theme["bg"])
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self._create_section(right_column, "Comprimir", self._build_compress_section, theme)
        self._create_section(right_column, "Estado", self._build_status_section, theme)
        self._create_section(right_column, "Historial", self._build_history_section, theme)
    
    def _create_section(self, parent, title, builder, theme):
        """Crear sección reutilizable"""
        section = tk.Frame(parent, bg=theme["bg_secondary"], relief="flat")
        section.pack(fill="x", padx=15, pady=8)
        
        title_label = tk.Label(section, text=title, font=('Segoe UI', 12, 'bold'),
                              bg=theme["bg_secondary"], fg=theme["accent"])
        title_label.pack(anchor="w", padx=15, pady=(12, 10))
        
        separator = tk.Frame(section, bg=theme["accent"], height=2)
        separator.pack(fill="x", padx=15, pady=(0, 12))
        
        content = tk.Frame(section, bg=theme["bg_secondary"])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        builder(content, theme)
    
    def _build_create_section(self, parent, theme):
        """Sección: Crear carpetas con validación mejorada"""
        tk.Label(parent, text="Carpeta destino:", font=('Segoe UI', 10, 'bold'),
                bg=theme["bg_secondary"], fg=theme["text"]).pack(anchor="w", pady=(0, 5))
        
        self.lbl_ruta = tk.Label(parent, text=f"{self.ruta_destino}",
                                font=('Segoe UI', 8), bg=theme["bg_secondary"],
                                fg=theme["text_secondary"], wraplength=350, justify="left")
        self.lbl_ruta.pack(anchor="w", pady=(0, 10), fill="x")
        
        StyledButton(parent, "Seleccionar carpeta", self.seleccionar_carpeta, 
                    primary=True, theme_colors=theme).pack(fill="x", pady=(0, 15))
        
        self._create_input_field(parent, "Número CT:", "nombre_ct", theme)
        self._create_input_field(parent, "Número Inversor (1-50):", "num_inv", theme, only_digits=True)
        self._create_input_field(parent, "Cantidad de Strings (1-100):", "entry_subcarpetas", theme, only_digits=True)
        
        tk.Label(parent, text="Tipo de dispositivo:", font=('Segoe UI', 10, 'bold'),
                bg=theme["bg_secondary"], fg=theme["text"]).pack(anchor="w", pady=(10, 8))
        
        self.dispositivo = tk.StringVar(value="PVPM")
        dispo_frame = tk.Frame(parent, bg=theme["bg_secondary"])
        dispo_frame.pack(fill="x", pady=(0, 15))
        
        tk.Radiobutton(dispo_frame, text="PVPM", variable=self.dispositivo, value="PVPM",
                      bg=theme["bg_secondary"], fg=theme["text"], selectcolor=theme["accent"],
                      font=('Segoe UI', 10)).pack(side="left", padx=(0, 20))
        tk.Radiobutton(dispo_frame, text="METREL", variable=self.dispositivo, value="METREL",
                      bg=theme["bg_secondary"], fg=theme["text"], selectcolor=theme["accent"],
                      font=('Segoe UI', 10)).pack(side="left")
        
        StyledButton(parent, "✓ Crear carpetas", self.crear_carpetas, 
                    primary=True, theme_colors=theme).pack(fill="x")
    
    def _build_compress_section(self, parent, theme):
        """Sección: Comprimir"""
        StyledButton(parent, "📦 Comprimir carpeta CT", self.comprimir_carpetas_ct, 
                    primary=True, theme_colors=theme).pack(fill="x")
    
    def _build_status_section(self, parent, theme):
        """Sección: Estado con detalles"""
        self.lbl_detalle = tk.Label(parent, text="Esperando acción...",
                                   font=('Segoe UI', 9), bg=theme["bg_secondary"],
                                   fg=theme["text_secondary"])
        self.lbl_detalle.pack(anchor="w", pady=(0, 8))
        
        self.progress = ttk.Progressbar(parent, mode='determinate', length=500)
        self.progress.pack(fill="x", pady=(0, 12))
        
        self.lbl_progreso = tk.Label(parent, text="Listo para comenzar",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=theme["bg_secondary"], fg=theme["success"])
        self.lbl_progreso.pack(anchor="w")
    
    def _build_history_section(self, parent, theme):
        """Sección: Historial de operaciones"""
        tk.Label(parent, text="Últimas operaciones:", font=('Segoe UI', 9),
                bg=theme["bg_secondary"], fg=theme["text_secondary"]).pack(anchor="w", pady=(0, 8))
        
        hist_frame = tk.Frame(parent, bg=theme["input_bg"], relief="solid", bd=1)
        hist_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(hist_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.history_text = tk.Text(hist_frame, height=6, bg=theme["input_bg"],
                                   fg=theme["text"], font=('Courier New', 8),
                                   yscrollcommand=scrollbar.set, relief="flat", bd=0)
        self.history_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.history_text.yview)
        self.history_text.config(state="disabled")
        
        self._update_history_display()
    
    def _update_history_display(self):
        """Actualizar display del historial"""
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        
        for op in reversed(self.operations_history[-5:]):
            self.history_text.insert(tk.END, f"[{op.timestamp}] {op.tipo}\n")
            self.history_text.insert(tk.END, f"  {op.descripcion}\n")
            self.history_text.insert(tk.END, f"  Estado: {op.estado}\n\n")
        
        self.history_text.config(state="disabled")
    
    def _show_history(self):
        """Mostrar historial completo en ventana"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Historial Completo")
        history_window.geometry("600x400")
        
        theme = THEMES[self.current_theme]
        history_window.configure(bg=theme["bg"])
        
        text_widget = tk.Text(history_window, bg=theme["input_bg"], fg=theme["text"],
                             font=('Courier New', 9), padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        
        for op in reversed(self.operations_history):
            text_widget.insert(tk.END, f"[{op.timestamp}] {op.tipo}\n")
            text_widget.insert(tk.END, f"  {op.descripcion}\n")
            text_widget.insert(tk.END, f"  Estado: {op.estado}\n\n")
        
        text_widget.config(state="disabled")
    
    def _create_input_field(self, parent, label, attr_name, theme, only_digits=False):
        """Crear campo de entrada con validación"""
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'),
                bg=theme["bg_secondary"], fg=theme["text"]).pack(anchor="w", pady=(0, 4))
        
        entry_frame = tk.Frame(parent, bg=theme["bg_secondary"])
        entry_frame.pack(fill="x", pady=(0, 12))
        
        entry = tk.Entry(parent, font=('Segoe UI', 10), 
                        bg=theme["input_bg"], fg=theme["text"],
                        insertbackground=theme["accent"],
                        relief="solid", bd=1, highlightthickness=0)
        entry.pack(fill="x")
        
        def on_change(*args):
            content = entry.get()
            if only_digits and content and not content.isdigit():
                entry.configure(fg=theme["error"])
            else:
                entry.configure(fg=theme["text"])
        
        entry.bind("<KeyRelease>", on_change)
        setattr(self, attr_name, entry)
    
    def seleccionar_carpeta(self):
        """Selecciona carpeta destino"""
        ruta_elegida = filedialog.askdirectory(title="Selecciona la carpeta destino")
        if ruta_elegida:
            self.ruta_destino = Path(ruta_elegida)
            self.lbl_ruta.config(text=str(self.ruta_destino))
            self._save_config()
    
    def _add_operation(self, tipo, descripcion, estado):
        """Agregar operación al historial"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        op = Operation(timestamp=now, tipo=tipo, descripcion=descripcion, estado=estado)
        self.operations_history.append(op)
        if len(self.operations_history) > 50:
            self.operations_history = self.operations_history[-50:]
        
        self._update_history_display()
        self._save_config()
    
    def crear_carpetas(self):
        """Crea estructura de carpetas CT/INV/String con validación mejorada"""
        try:
            nombreCT = self.nombre_ct.get().strip()
            numero_name_inversor = self.num_inv.get().strip()
            nombreDivice = self.dispositivo.get()
            strings = self.entry_subcarpetas.get().strip()
            
            errores = []
            if not nombreCT:
                errores.append("• Número CT no puede estar vacío")
            if not numero_name_inversor:
                errores.append("• Número Inversor no puede estar vacío")
            if not strings:
                errores.append("• Cantidad de Strings no puede estar vacía")
            
            if errores:
                messagebox.showerror("Validación", "\n".join(errores))
                self._add_operation("CREATE", f"CT-{nombreCT}", "ERROR: Validación")
                return
            
            if not numero_name_inversor.isdigit():
                messagebox.showerror("Error", "Inversor debe ser un número")
                return
            if not strings.isdigit():
                messagebox.showerror("Error", "Strings debe ser un número")
                return
            
            numero_inv_int = int(numero_name_inversor)
            strings_int = int(strings)
            
            if numero_inv_int < 1 or numero_inv_int > 50:
                messagebox.showerror("Error", "El inversor debe estar entre 1 y 50")
                return
            if strings_int < 1 or strings_int > 100:
                messagebox.showerror("Error", "Los strings deben estar entre 1 y 100")
                return
            
            theme = THEMES[self.current_theme]
            self.lbl_detalle.config(text=f"Creando: CT-{nombreCT}/INV-{numero_name_inversor}-{nombreDivice}", 
                                   fg=theme["accent"])
            self.lbl_progreso.config(text="Creando carpetas...", fg=theme["accent"])
            self.root.update()
            
            ruta = self.ruta_destino
            for i in range(1, strings_int + 1):
                carpeta_ct = ruta / f"CT-{nombreCT}" / f"INV-{numero_name_inversor}-{nombreDivice}" / f"String-{i}"
                carpeta_ct.mkdir(parents=True, exist_ok=True)
                progress = (i / strings_int) * 100
                self.progress['value'] = progress
                self.root.update()
            
            self.progress['value'] = 100
            self.lbl_progreso.config(text=f"✓ Se crearon {strings_int} carpetas", fg=theme["success"])
            self.lbl_detalle.config(text=f"Completado: {strings_int} carpetas creadas", fg=theme["success"])
            
            self._play_sound(700, 150)
            self._add_operation("CREATE", f"CT-{nombreCT} ({strings_int} strings)", "ÉXITO")
            
            messagebox.showinfo("Éxito", 
                f"Se crearon {strings_int} carpetas en:\n"
                f"{ruta}/CT-{nombreCT}/INV-{numero_name_inversor}-{nombreDivice}")
        except Exception as e:
            theme = THEMES[self.current_theme]
            self.lbl_progreso.config(text="Error al crear carpetas", fg=theme["error"])
            self._add_operation("CREATE", "Error", str(e))
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def comprimir_carpetas_ct(self):
        """Comprime cada INV dentro de CT seleccionada"""
        try:
            carpeta_ct = filedialog.askdirectory(title="Selecciona la carpeta CT")
            if not carpeta_ct:
                return
            
            carpeta_ct_path = Path(carpeta_ct)
            inv_dirs = [d for d in carpeta_ct_path.iterdir() if d.is_dir() and d.name.startswith("INV-")]
            
            if not inv_dirs:
                messagebox.showwarning("Aviso", "No hay carpetas INV-* para comprimir")
                return
            
            theme = THEMES[self.current_theme]
            self.progress['value'] = 0
            self.lbl_progreso.config(text="Comprimiendo...", fg=theme["accent"])
            self.root.update()
            
            creados = []
            
            for idx, inv_dir in enumerate(inv_dirs):
                self.lbl_detalle.config(text=f"Comprimiendo: {inv_dir.name}", fg=theme["accent"])
                self.root.update()
                
                zip_name = f"{inv_dir.name}.zip"
                zip_path = carpeta_ct_path / zip_name
                
                contador = 1
                while zip_path.exists():
                    zip_path = carpeta_ct_path / f"{inv_dir.name}_{contador}.zip"
                    contador += 1
                
                def on_progress(progress, name):
                    self.progress['value'] = progress
                    self.lbl_detalle.config(text=f"Comprimiendo: {name} ({int(progress)}%)", fg=theme["accent"])
                    self.root.update()
                
                def on_error(error, name):
                    pass
                
                worker = CompressionWorker(inv_dir, zip_path, self.compression_level, on_progress, on_error)
                worker.start()
                worker.join()
                
                if zip_path.exists():
                    creados.append(zip_path.name)
                
                progress_val = ((idx + 1) / len(inv_dirs)) * 100
                self.progress['value'] = progress_val
                self.root.update()
            
            self.progress['value'] = 100
            self.lbl_progreso.config(text=f"✓ {len(creados)} archivos comprimidos", fg=theme["success"])
            self.lbl_detalle.config(text=f"Completado: {len(creados)} ZIPs creados", fg=theme["success"])
            
            self._play_sound(700, 200)
            self._add_operation("COMPRESS", f"{len(creados)} archivos ZIP", "ÉXITO")
            
            messagebox.showinfo("Éxito", f"Se comprimieron {len(creados)} componentes.")
        except Exception as e:
            theme = THEMES[self.current_theme]
            self.lbl_progreso.config(text="Error en compresión", fg=theme["error"])
            self._add_operation("COMPRESS", "Error", str(e))
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def __del__(self):
        """Guardar configuración al cerrar"""
        try:
            self._save_config()
        except:
            pass

if __name__ == "__main__":
    ventana = tk.Tk()
    app = ComprensorApp(ventana)
    ventana.mainloop()

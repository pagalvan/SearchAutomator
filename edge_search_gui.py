"""
Interfaz Gráfica para Automatización de Búsquedas en Microsoft Edge
Autor: Asistente de IA
Fecha: Febrero 2026
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
from datetime import datetime
from edge_search_automation import (
    USER_DATA_DIR, 
    PERFILES_EDGE, 
    BUSQUEDAS_POR_PERFIL,
    USAR_PERFILES_ORIGINALES,
    procesar_perfil,
    generar_busquedas_realistas
)
from puntos_dashboard import registrar_puntos, abrir_dashboard

# Archivo para guardar el progreso
PROGRESO_FILE = "progreso_busquedas.json"
CONFIG_FILE = "config_perfiles.json"


class PerfilCard(tk.Frame):
    """Widget que representa una tarjeta de perfil"""
    
    def __init__(self, parent, nombre_perfil, numero, callback=None):
        super().__init__(parent, relief=tk.RAISED, borderwidth=2, bg='white')
        self.nombre_perfil = nombre_perfil
        self.numero = numero
        self.callback = callback
        
        # Variable para checkbox
        self.selected = tk.BooleanVar(value=False)
        
        # Variable para detener este perfil específico
        self.detener_individual = False
        self.ejecutando_ahora = False
        
        # Variables de progreso
        self.busquedas_completadas = tk.IntVar(value=0)
        self.estado = tk.StringVar(value="Pendiente")
        
        self._crear_ui()
        self._cargar_datos()
    
    def _crear_ui(self):
        """Crea la interfaz de la tarjeta"""
        # Frame principal
        main_frame = tk.Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header con checkbox e ícono
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Checkbox
        self.checkbox = tk.Checkbutton(
            header_frame, 
            variable=self.selected,
            bg='white',
            command=self._on_select
        )
        self.checkbox.pack(side=tk.LEFT)
        
        # Ícono (emoji de usuario)
        icon_label = tk.Label(
            header_frame,
            text="👤",
            font=('Segoe UI Emoji', 24),
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=5)
        
        # Nombre del perfil
        name_label = tk.Label(
            header_frame,
            text=f"Perfil #{self.numero}",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        name_label.pack(side=tk.LEFT, padx=5)
        
        # Información del perfil
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=5)
        
        # Nombre técnico del perfil
        tk.Label(
            info_frame,
            text=f"📁 {self.nombre_perfil}",
            font=('Arial', 9),
            bg='white',
            fg='gray'
        ).pack(anchor=tk.W)
        
        # Email (se intentará cargar de las preferencias)
        self.email_label = tk.Label(
            info_frame,
            text="📧 Cargando...",
            font=('Arial', 9),
            bg='white',
            fg='#0066cc'
        )
        self.email_label.pack(anchor=tk.W, pady=2)
        
        # Puntos Rewards
        self.puntos_label = tk.Label(
            info_frame,
            text="💰 Puntos: --",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#f39c12'
        )
        self.puntos_label.pack(anchor=tk.W, pady=2)
        
        # Barra de progreso
        progress_frame = tk.Frame(main_frame, bg='white')
        progress_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            progress_frame,
            text="Progreso:",
            font=('Arial', 9),
            bg='white'
        ).pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=200,
            mode='determinate',
            maximum=BUSQUEDAS_POR_PERFIL
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="0/30",
            font=('Arial', 9),
            bg='white'
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # Estado
        self.estado_label = tk.Label(
            main_frame,
            textvariable=self.estado,
            font=('Arial', 9, 'italic'),
            bg='white',
            fg='gray'
        )
        self.estado_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Botón de detener individual
        self.btn_detener = tk.Button(
            main_frame,
            text="⏹️ Detener este perfil",
            command=self._detener_individual,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 8),
            padx=8,
            pady=2,
            state=tk.DISABLED
        )
        self.btn_detener.pack(anchor=tk.W, pady=(3, 0))
        
        # Última actualización
        self.update_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 8),
            bg='white',
            fg='#666'
        )
        self.update_label.pack(anchor=tk.W)
    
    def _cargar_datos(self):
        """Carga datos guardados del perfil"""
        # Intentar cargar email desde Preferences
        try:
            prefs_path = os.path.join(USER_DATA_DIR, self.nombre_perfil, 'Preferences')
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    # Intentar obtener email de diferentes ubicaciones
                    email = None
                    if 'account_info' in prefs:
                        for account in prefs['account_info']:
                            if 'email' in account:
                                email = account['email']
                                break
                    
                    if not email and 'profile' in prefs:
                        email = prefs['profile'].get('user_name', None)
                    
                    if email:
                        self.email_label.config(text=f"📧 {email}")
                    else:
                        self.email_label.config(text="📧 No disponible")
            else:
                self.email_label.config(text="📧 Perfil no encontrado")
        except Exception as e:
            self.email_label.config(text="📧 Error al cargar")
        
        # Cargar puntos guardados del historial
        self._cargar_puntos_historial()
        
        # Cargar progreso guardado
        self._cargar_progreso()
    
    def _cargar_progreso(self):
        """Carga el progreso guardado del archivo JSON"""
        try:
            if os.path.exists(PROGRESO_FILE):
                with open(PROGRESO_FILE, 'r') as f:
                    data = json.load(f)
                    
                    if self.nombre_perfil in data:
                        perfil_data = data[self.nombre_perfil]
                        completadas = perfil_data.get('completadas', 0)
                        ultima_fecha = perfil_data.get('fecha', '')
                        
                        # Verificar si es del día de hoy
                        hoy = datetime.now().strftime('%Y-%m-%d')
                        if ultima_fecha.startswith(hoy):
                            # Es del mismo día, cargar progreso
                            self.actualizar_progreso(completadas)
                            if completadas >= BUSQUEDAS_POR_PERFIL:
                                self.estado.set("✅ Completado hoy")
                                self.estado_label.config(fg='green')
                            else:
                                self.estado.set(f"🔄 {completadas}/{BUSQUEDAS_POR_PERFIL} hoy")
                                self.estado_label.config(fg='orange')
                            self.update_label.config(text=f"Última actualización: {ultima_fecha}")
                        else:
                            # Es de un día anterior, resetear progreso
                            self.actualizar_progreso(0)
                            self.estado.set("🆕 Nuevo día - Listo para comenzar")
                            self.estado_label.config(fg='blue')
                            if ultima_fecha:
                                self.update_label.config(text=f"Último uso: {ultima_fecha}")
                            # Limpiar el registro antiguo
                            self._resetear_progreso_archivo()
        except Exception as e:
            pass
    
    def _resetear_progreso_archivo(self):
        """Resetea el progreso de este perfil en el archivo JSON"""
        try:
            data = {}
            if os.path.exists(PROGRESO_FILE):
                with open(PROGRESO_FILE, 'r') as f:
                    data = json.load(f)
            
            # Eliminar o resetear el perfil
            if self.nombre_perfil in data:
                del data[self.nombre_perfil]
                
                with open(PROGRESO_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            pass
    
    def _cargar_puntos_historial(self):
        """Carga los últimos puntos guardados del historial"""
        try:
            historial_file = "historial_puntos.json"
            if os.path.exists(historial_file):
                with open(historial_file, 'r', encoding='utf-8') as f:
                    historial = json.load(f)
                    
                    if self.nombre_perfil in historial:
                        registros = historial[self.nombre_perfil].get('registros', [])
                        if registros:
                            # Obtener el último registro
                            ultimo = registros[-1]
                            puntos = ultimo.get('puntos', 0)
                            if puntos:
                                PUNTOS_PARA_CANJEAR = 6550
                                if puntos >= PUNTOS_PARA_CANJEAR:
                                    self.puntos_label.config(
                                        text=f"🎁 ¡{puntos:,} LISTO!",
                                        fg='#27ae60',
                                        font=('Arial', 10, 'bold')
                                    )
                                else:
                                    faltan = PUNTOS_PARA_CANJEAR - puntos
                                    self.puntos_label.config(
                                        text=f"💰 {puntos:,} (faltan {faltan:,})",
                                        fg='#f39c12',
                                        font=('Arial', 9)
                                    )
        except Exception as e:
            pass
    
    def _guardar_progreso(self):
        """Guarda el progreso en el archivo JSON"""
        try:
            data = {}
            if os.path.exists(PROGRESO_FILE):
                with open(PROGRESO_FILE, 'r') as f:
                    data = json.load(f)
            
            data[self.nombre_perfil] = {
                'completadas': self.busquedas_completadas.get(),
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'numero': self.numero
            }
            
            with open(PROGRESO_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass
    
    def _on_select(self):
        """Callback cuando se selecciona/deselecciona"""
        if self.callback:
            self.callback()
    
    def _detener_individual(self):
        """Detiene solo este perfil"""
        self.detener_individual = True
        self.btn_detener.config(state=tk.DISABLED)
        self.set_estado("⏹️ Deteniendo...", "orange")
    
    def iniciar_ejecucion(self):
        """Marca el perfil como en ejecución"""
        self.ejecutando_ahora = True
        self.detener_individual = False
        self.btn_detener.config(state=tk.NORMAL)
        self.set_estado("🔄 Ejecutando...", "blue")
    
    def finalizar_ejecucion(self):
        """Marca el perfil como finalizado"""
        self.ejecutando_ahora = False
        self.btn_detener.config(state=tk.DISABLED)
    
    def actualizar_progreso(self, completadas):
        """Actualiza la barra de progreso"""
        self.busquedas_completadas.set(completadas)
        self.progress_bar['value'] = completadas
        self.progress_label.config(text=f"{completadas}/{BUSQUEDAS_POR_PERFIL}")
        
        if completadas >= BUSQUEDAS_POR_PERFIL:
            self.estado.set("✅ Completado")
            self.estado_label.config(fg='green')
        elif completadas > 0:
            self.estado.set("🔄 En progreso")
            self.estado_label.config(fg='orange')
        
        self._guardar_progreso()
    
    def set_puntos(self, puntos):
        """Actualiza los puntos mostrados"""
        if puntos:
            try:
                puntos_int = int(str(puntos).replace(',', '').replace('.', ''))
                PUNTOS_PARA_CANJEAR = 6550
                
                if puntos_int >= PUNTOS_PARA_CANJEAR:
                    # ¡Tiene suficientes puntos para canjear!
                    self.puntos_label.config(
                        text=f"🎁 ¡{puntos_int:,} LISTO!",
                        fg='#27ae60',
                        font=('Arial', 10, 'bold')
                    )
                else:
                    faltan = PUNTOS_PARA_CANJEAR - puntos_int
                    self.puntos_label.config(
                        text=f"💰 {puntos_int:,} (faltan {faltan:,})",
                        fg='#f39c12',
                        font=('Arial', 9)
                    )
            except:
                self.puntos_label.config(text=f"💰 Puntos: {puntos}")
            
            # Guardar en el historial
            email = self.email_label.cget('text').replace('📧 ', '')
            registrar_puntos(self.nombre_perfil, email, puntos)
    
    def set_estado(self, texto, color='gray'):
        """Establece el estado del perfil"""
        self.estado.set(texto)
        self.estado_label.config(fg=color)
        self.update_label.config(text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")


class EdgeSearchGUI:
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edge Search Automation - Control Panel")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.perfil_cards = []
        self.ejecutando = False
        self.detener_flag = False
        self.threads_activos = []
        
        self._crear_ui()
        self._cargar_perfiles()
    
    def _crear_ui(self):
        """Crea la interfaz principal"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔍 Edge Search Automation",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=10)
        
        tk.Label(
            header,
            text="Selecciona los perfiles y gestiona las búsquedas automáticas",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg='white', relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        # Botones de selección
        tk.Button(
            toolbar,
            text="✅ Seleccionar Todos",
            command=self.seleccionar_todos,
            bg='#3498db',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="❌ Deseleccionar Todos",
            command=self.deseleccionar_todos,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón de resetear progreso
        tk.Button(
            toolbar,
            text="🔄 Resetear Progreso",
            command=self.resetear_progreso_seleccionados,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botón de inicio
        self.btn_iniciar = tk.Button(
            toolbar,
            text="🚀 Iniciar Búsquedas",
            command=self.iniciar_busquedas,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=5
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        # Botón de detener
        self.btn_detener = tk.Button(
            toolbar,
            text="⏹️ Detener",
            command=self.detener_busquedas,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_detener.pack(side=tk.LEFT, padx=5)
        
        # Contador de seleccionados
        self.label_seleccionados = tk.Label(
            toolbar,
            text="0 perfiles seleccionados",
            font=('Arial', 10),
            bg='white'
        )
        self.label_seleccionados.pack(side=tk.RIGHT, padx=10)
        
        # Botón del dashboard
        tk.Button(
            toolbar,
            text="📊 Dashboard",
            command=self.abrir_dashboard,
            bg='#1abc9c',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # Botón de configuración de perfiles
        tk.Button(
            toolbar,
            text="⚙️ Configurar Perfiles",
            command=self.configurar_perfiles,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # Container principal con scroll
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log area
        log_frame = tk.Frame(self.root, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10))
        
        tk.Label(
            log_frame,
            text="📋 Registro de Actividad",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    def _cargar_perfiles(self):
        """Carga las tarjetas de perfiles"""
        # Limpiar progreso de días anteriores al inicio
        self._limpiar_progreso_antiguo()
        
        # Crear grid de 3 columnas
        for i, nombre_perfil in enumerate(PERFILES_EDGE):
            fila = i // 3
            columna = i % 3
            
            card = PerfilCard(
                self.scrollable_frame,
                nombre_perfil,
                i + 1,
                callback=self.actualizar_contador
            )
            card.grid(row=fila, column=columna, padx=10, pady=10, sticky='nsew')
            
            self.perfil_cards.append(card)
        
        # Configurar grid para que las columnas se expandan igual
        for col in range(3):
            self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="col")
        
        fecha_hoy = datetime.now().strftime('%d/%m/%Y')
        self.log(f"Sistema iniciado - {fecha_hoy}. Listo para comenzar.")
    
    def _limpiar_progreso_antiguo(self):
        """Limpia el progreso de días anteriores"""
        try:
            if os.path.exists(PROGRESO_FILE):
                with open(PROGRESO_FILE, 'r') as f:
                    data = json.load(f)
                
                hoy = datetime.now().strftime('%Y-%m-%d')
                perfiles_actualizados = {}
                
                # Filtrar solo los perfiles del día de hoy
                for perfil, info in data.items():
                    fecha = info.get('fecha', '')
                    if fecha.startswith(hoy):
                        perfiles_actualizados[perfil] = info
                
                # Guardar solo los datos del día actual
                if perfiles_actualizados != data:
                    with open(PROGRESO_FILE, 'w') as f:
                        json.dump(perfiles_actualizados, f, indent=2)
        except Exception as e:
            pass
    
    def log(self, mensaje):
        """Añade un mensaje al log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def actualizar_contador(self):
        """Actualiza el contador de perfiles seleccionados"""
        seleccionados = sum(1 for card in self.perfil_cards if card.selected.get())
        self.label_seleccionados.config(
            text=f"{seleccionados} perfil{'es' if seleccionados != 1 else ''} seleccionado{'s' if seleccionados != 1 else ''}"
        )
    
    def seleccionar_todos(self):
        """Selecciona todos los perfiles"""
        for card in self.perfil_cards:
            card.selected.set(True)
        self.actualizar_contador()
        self.log("Todos los perfiles seleccionados")
    
    def deseleccionar_todos(self):
        """Deselecciona todos los perfiles"""
        for card in self.perfil_cards:
            card.selected.set(False)
        self.actualizar_contador()
        self.log("Todos los perfiles deseleccionados")
    
    def resetear_progreso_seleccionados(self):
        """Resetea el progreso de los perfiles seleccionados"""
        perfiles_seleccionados = [
            card for card in self.perfil_cards if card.selected.get()
        ]
        
        if not perfiles_seleccionados:
            messagebox.showwarning(
                "Advertencia",
                "Por favor selecciona al menos un perfil para resetear"
            )
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Reseteo",
            f"¿Resetear el progreso de {len(perfiles_seleccionados)} perfil(es)?\n\n"
            "Esto eliminará el progreso guardado y volverá a 0/30."
        )
        
        if respuesta:
            for card in perfiles_seleccionados:
                card.actualizar_progreso(0)
                card.set_estado("🔄 Reseteado - Listo para comenzar", "blue")
                card._resetear_progreso_archivo()
                self.log(f"🔄 Progreso reseteado: {card.nombre_perfil}")
            
            self.log(f"✅ {len(perfiles_seleccionados)} perfil(es) reseteado(s)")
            messagebox.showinfo(
                "Completado",
                f"Progreso reseteado en {len(perfiles_seleccionados)} perfil(es)"
            )
    
    def configurar_perfiles(self):
        """Abre ventana para configurar perfiles de Edge"""
        # Crear ventana de configuración
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Perfiles de Edge")
        config_window.geometry("700x500")
        config_window.configure(bg='white')
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Header
        header_frame = tk.Frame(config_window, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="⚙️ Configuración de Perfiles",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(config_window, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instrucción
        tk.Label(
            main_frame,
            text="Directorio de User Data de Edge:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para ruta
        path_frame = tk.Frame(main_frame, bg='white')
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        user_data_entry = tk.Entry(
            path_frame,
            font=('Arial', 10),
            width=50
        )
        user_data_entry.insert(0, USER_DATA_DIR)
        user_data_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def seleccionar_user_data():
            carpeta = filedialog.askdirectory(
                title="Selecciona el directorio User Data de Edge",
                initialdir="C:\\Users"
            )
            if carpeta:
                user_data_entry.delete(0, tk.END)
                user_data_entry.insert(0, carpeta)
                # Detectar perfiles automáticamente
                detectar_perfiles(carpeta)
        
        tk.Button(
            path_frame,
            text="📂 Buscar",
            command=seleccionar_user_data,
            bg='#3498db',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Lista de perfiles
        tk.Label(
            main_frame,
            text="Perfiles detectados:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, pady=(10, 5))
        
        # Frame con scroll para perfiles
        perfiles_frame = tk.Frame(main_frame, bg='white')
        perfiles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        perfiles_canvas = tk.Canvas(perfiles_frame, bg='white', highlightthickness=1)
        perfiles_scrollbar = ttk.Scrollbar(perfiles_frame, orient=tk.VERTICAL, command=perfiles_canvas.yview)
        perfiles_list_frame = tk.Frame(perfiles_canvas, bg='white')
        
        perfiles_list_frame.bind(
            "<Configure>",
            lambda e: perfiles_canvas.configure(scrollregion=perfiles_canvas.bbox("all"))
        )
        
        perfiles_canvas.create_window((0, 0), window=perfiles_list_frame, anchor="nw")
        perfiles_canvas.configure(yscrollcommand=perfiles_scrollbar.set)
        
        perfiles_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        perfiles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        perfiles_checks = []
        
        def detectar_perfiles(user_data_path):
            """Detecta automáticamente los perfiles en User Data"""
            # Limpiar lista actual
            for widget in perfiles_list_frame.winfo_children():
                widget.destroy()
            perfiles_checks.clear()
            
            if not os.path.exists(user_data_path):
                tk.Label(
                    perfiles_list_frame,
                    text="⚠️ Directorio no encontrado",
                    font=('Arial', 10),
                    bg='white',
                    fg='red'
                ).pack(pady=20)
                return
            
            # Buscar perfiles
            perfiles_encontrados = []
            
            # Default siempre existe
            if os.path.exists(os.path.join(user_data_path, "Default")):
                perfiles_encontrados.append("Default")
            
            # Buscar Profile X
            for item in os.listdir(user_data_path):
                if item.startswith("Profile ") and os.path.isdir(os.path.join(user_data_path, item)):
                    perfiles_encontrados.append(item)
            
            if not perfiles_encontrados:
                tk.Label(
                    perfiles_list_frame,
                    text="⚠️ No se encontraron perfiles",
                    font=('Arial', 10),
                    bg='white',
                    fg='orange'
                ).pack(pady=20)
                return
            
            # Crear checkboxes para cada perfil
            for perfil in sorted(perfiles_encontrados):
                var = tk.BooleanVar(value=(perfil in PERFILES_EDGE))
                
                frame = tk.Frame(perfiles_list_frame, bg='white')
                frame.pack(fill=tk.X, pady=2)
                
                check = tk.Checkbutton(
                    frame,
                    text=f"👤 {perfil}",
                    variable=var,
                    font=('Arial', 10),
                    bg='white'
                )
                check.pack(side=tk.LEFT, padx=5)
                
                perfiles_checks.append((perfil, var))
        
        # Detectar perfiles iniciales
        detectar_perfiles(USER_DATA_DIR)
        
        # Botones de acción
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        def guardar_configuracion():
            # Obtener nuevas rutas
            nuevo_user_data = user_data_entry.get()
            nuevos_perfiles = [perfil for perfil, var in perfiles_checks if var.get()]
            
            if not nuevos_perfiles:
                messagebox.showwarning(
                    "Advertencia",
                    "Debes seleccionar al menos un perfil"
                )
                return
            
            # Guardar configuración
            config = {
                "user_data_dir": nuevo_user_data,
                "perfiles": nuevos_perfiles
            }
            
            try:
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Actualizar variables globales
                global USER_DATA_DIR, PERFILES_EDGE
                USER_DATA_DIR = nuevo_user_data
                PERFILES_EDGE = nuevos_perfiles
                
                # Actualizar en edge_search_automation
                import edge_search_automation
                edge_search_automation.USER_DATA_DIR = nuevo_user_data
                edge_search_automation.PERFILES_EDGE = nuevos_perfiles
                
                messagebox.showinfo(
                    "Éxito",
                    f"Configuración guardada correctamente.\n\n"
                    f"Perfiles: {len(nuevos_perfiles)}\n\n"
                    f"La aplicación se reiniciará."
                )
                
                config_window.destroy()
                
                # Recargar la aplicación
                self.recargar_aplicacion()
                
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo guardar la configuración:\n{str(e)}"
                )
        
        tk.Button(
            buttons_frame,
            text="✅ Guardar y Aplicar",
            command=guardar_configuracion,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)
        
        tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=config_window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=(0, 10))
    
    def iniciar_busquedas(self):
        """Inicia las búsquedas en los perfiles seleccionados"""
        perfiles_seleccionados = [
            card for card in self.perfil_cards if card.selected.get()
        ]
        
        if not perfiles_seleccionados:
            messagebox.showwarning(
                "Advertencia",
                "Por favor selecciona al menos un perfil"
            )
            return
        
        # Confirmar inicio
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Iniciar búsquedas en {len(perfiles_seleccionados)} perfil(es)?\n\n"
            f"Se realizarán {BUSQUEDAS_POR_PERFIL} búsquedas por perfil."
        )
        
        if not respuesta:
            return
        
        # Cambiar estado de botones y resetear flag de detención
        self.ejecutando = True
        self.detener_flag = False
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_detener.config(state=tk.NORMAL)
        
        self.log(f"\n{'='*60}")
        self.log(f"🚀 Iniciando búsquedas en {len(perfiles_seleccionados)} perfiles")
        self.log(f"{'='*60}\n")
        
        # Iniciar threads
        self.threads_activos = []
        for card in perfiles_seleccionados:
            card.set_estado("⏳ Iniciando...", "orange")
            thread = threading.Thread(
                target=self.ejecutar_perfil,
                args=(card,),
                daemon=True
            )
            thread.start()
            self.threads_activos.append(thread)
            self.log(f"✅ Thread iniciado para {card.nombre_perfil}")
    
    def ejecutar_perfil(self, card):
        """Ejecuta las búsquedas para un perfil específico"""
        try:
            card.iniciar_ejecucion()
            self.log(f"🔍 Procesando {card.nombre_perfil}...")
            
            # Crear callback para actualizar progreso en tiempo real
            def actualizar_progreso(completadas):
                # Usar after para actualizar desde el thread seguro
                self.root.after(0, lambda: card.actualizar_progreso(completadas))
                self.root.after(0, lambda: self.log(f"📊 {card.nombre_perfil}: {completadas}/{BUSQUEDAS_POR_PERFIL} búsquedas"))
                # No necesitamos retornar nada, detener_flag maneja la detención
                return None
            
            # Callback para información extra (puntos)
            def actualizar_info(info):
                if info.get('tipo') == 'puntos':
                    puntos = info.get('valor')
                    self.root.after(0, lambda: card.set_puntos(puntos))
                    self.root.after(0, lambda: self.log(f"💰 {card.nombre_perfil}: {puntos} puntos"))
            
            # Función para verificar detención (global o individual)
            def verificar_detener():
                return self.detener_flag or card.detener_individual
            
            # Obtener progreso actual para continuar desde donde quedó
            progreso_actual = card.busquedas_completadas.get()
            
            # Ejecutar con callback de progreso y flag de detención
            completadas = procesar_perfil(
                card.nombre_perfil, 
                card.numero, 
                callback_progreso=actualizar_progreso, 
                detener_flag=verificar_detener,
                callback_info=actualizar_info,
                busquedas_iniciales=progreso_actual
            )
            
            # Verificar si se detuvo o se completó
            if self.detener_flag:
                self.root.after(0, lambda: card.set_estado("⏹️ Detenido (global)", "orange"))
                self.root.after(0, lambda: card.finalizar_ejecucion())
                self.log(f"⏹️ {card.nombre_perfil} detenido por usuario (completadas: {completadas}/{BUSQUEDAS_POR_PERFIL})")
            elif card.detener_individual:
                self.root.after(0, lambda: card.set_estado("⏹️ Detenido", "orange"))
                self.root.after(0, lambda: card.finalizar_ejecucion())
                self.log(f"⏹️ {card.nombre_perfil} detenido individualmente (completadas: {completadas}/{BUSQUEDAS_POR_PERFIL})")
            elif completadas >= BUSQUEDAS_POR_PERFIL:
                # Solo marcar como completado si realmente terminó todas
                self.root.after(0, lambda: card.set_estado("✅ Completado", "green"))
                self.root.after(0, lambda: card.finalizar_ejecucion())
                self.log(f"✅ {card.nombre_perfil} completado exitosamente")
            else:
                # Terminó con menos búsquedas (error o detención no capturada)
                self.root.after(0, lambda: card.set_estado("⚠️ Incompleto", "orange"))
                self.root.after(0, lambda: card.finalizar_ejecucion())
                self.log(f"⚠️ {card.nombre_perfil} terminó con {completadas}/{BUSQUEDAS_POR_PERFIL} búsquedas")
            
        except Exception as e:
            # Error inesperado durante la ejecución
            self.root.after(0, lambda: card.set_estado(f"❌ Error: {str(e)[:30]}...", "red"))
            self.root.after(0, lambda: card.finalizar_ejecucion())
            self.log(f"❌ Error en {card.nombre_perfil}: {str(e)}")
        
        finally:
            # Verificar si todos terminaron
            if all(not t.is_alive() for t in self.threads_activos):
                self.root.after(0, self.finalizar_ejecucion)
    
    def detener_busquedas(self):
        """Detiene las búsquedas en curso"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Detener todas las búsquedas en curso?\n\nEl progreso actual se guardará."
        )
        
        if respuesta:
            self.log("\n⏹️ Señal de detención enviada...")
            self.detener_flag = True
            self.ejecutando = False
            self.log("⏳ Esperando a que los navegadores se cierren...")
    
    def finalizar_ejecucion(self):
        """Finaliza la ejecución y restaura el estado"""
        self.ejecutando = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)
        self.log("\n" + "="*60)
        self.log("🎉 Proceso finalizado")
        self.log("="*60 + "\n")
    
    def abrir_dashboard(self):
        """Abre la ventana del dashboard de puntos"""
        abrir_dashboard(self.root)
    
    def recargar_aplicacion(self):
        """Recarga la aplicación con la nueva configuración"""
        # Destruir ventana actual
        self.root.destroy()
        
        # Crear nueva instancia
        import sys
        import os
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    # Cargar configuración si existe
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                USER_DATA_DIR = config.get('user_data_dir', USER_DATA_DIR)
                PERFILES_EDGE = config.get('perfiles', PERFILES_EDGE)
                
                # Actualizar en edge_search_automation
                import edge_search_automation
                edge_search_automation.USER_DATA_DIR = USER_DATA_DIR
                edge_search_automation.PERFILES_EDGE = PERFILES_EDGE
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    
    app = EdgeSearchGUI()
    app.run()

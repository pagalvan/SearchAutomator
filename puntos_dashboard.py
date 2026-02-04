"""
Dashboard de Puntos de Microsoft Rewards
Muestra estadísticas, historial y gráficas de los puntos ganados
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Intentar importar matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False
    print("⚠️ matplotlib no está instalado. Ejecuta: pip install matplotlib")

HISTORIAL_FILE = "historial_puntos.json"


def cargar_historial():
    """Carga el historial de puntos desde el archivo JSON"""
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def guardar_historial(historial):
    """Guarda el historial de puntos en el archivo JSON"""
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar historial: {e}")


def registrar_puntos(perfil_nombre, email, puntos):
    """
    Registra los puntos de un perfil en el historial
    
    Args:
        perfil_nombre: Nombre del perfil (ej: 'Profile 2')
        email: Email de la cuenta
        puntos: Puntos actuales (string o int)
    """
    if not puntos:
        return
    
    try:
        puntos_int = int(str(puntos).replace(',', '').replace('.', ''))
    except:
        return
    
    historial = cargar_historial()
    
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    if perfil_nombre not in historial:
        historial[perfil_nombre] = {
            'email': email,
            'registros': []
        }
    
    # Actualizar email por si cambió
    historial[perfil_nombre]['email'] = email
    
    # Añadir registro
    historial[perfil_nombre]['registros'].append({
        'fecha': fecha,
        'hora': fecha_hora,
        'puntos': puntos_int
    })
    
    guardar_historial(historial)


def obtener_estadisticas(perfil_nombre):
    """
    Obtiene estadísticas de un perfil
    
    Returns:
        dict con estadísticas o None
    """
    historial = cargar_historial()
    
    if perfil_nombre not in historial:
        return None
    
    registros = historial[perfil_nombre]['registros']
    if not registros:
        return None
    
    # Ordenar por fecha
    registros_ordenados = sorted(registros, key=lambda x: x['hora'])
    
    # Puntos actuales (último registro)
    puntos_actuales = registros_ordenados[-1]['puntos']
    
    # Primer registro
    primer_registro = registros_ordenados[0]
    
    # Calcular flujos (Ganancias y Gastos) recorriendo todo el historial
    ganancia_neta_total = puntos_actuales - primer_registro['puntos']
    
    # Definir fechas de referencia
    hoy = datetime.now().strftime('%Y-%m-%d')
    mes_actual = datetime.now().strftime('%Y-%m')
    
    ganancia_bruta_hoy = 0
    gasto_hoy = 0
    
    ganancia_bruta_mes = 0
    gasto_mes = 0
    
    gasto_total = 0
    
    # Umbral mínimo para considerar un gasto real (ignorar fluctuaciones de la página)
    # Los canjes mínimos en Rewards suelen ser de 100+ puntos
    UMBRAL_GASTO_MINIMO = 50
    
    # Recorrer historial para detectar cambios
    prev_r = registros_ordenados[0]
    
    for r in registros_ordenados[1:]:
        diff = r['puntos'] - prev_r['puntos']
        
        fecha_r = r['fecha']
        es_hoy = (fecha_r == hoy)
        es_mes = fecha_r.startswith(mes_actual)
        
        if diff > 0:
            # Es una ganancia
            if es_hoy: ganancia_bruta_hoy += diff
            if es_mes: ganancia_bruta_mes += diff
        elif diff < -UMBRAL_GASTO_MINIMO:
            # Es un gasto real (mayor al umbral, no es fluctuación)
            gasto = abs(diff)
            gasto_total += gasto
            if es_hoy: gasto_hoy += gasto
            if es_mes: gasto_mes += gasto
            
        prev_r = r

    # Promedio diario de ganancias (Neto vs Bruto? Mejor Neto para ver crecimiento real)
    hace_7_dias = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    registros_semana = [r for r in registros_ordenados if r['fecha'] >= hace_7_dias]
    
    promedio_diario = 0
    if len(registros_semana) >= 2:
        dias = (datetime.now() - datetime.strptime(registros_semana[0]['fecha'], '%Y-%m-%d')).days
        if dias > 0:
            promedio_diario = (registros_semana[-1]['puntos'] - registros_semana[0]['puntos']) / dias
            if promedio_diario < 0: promedio_diario = 0 # No mostrar promedios negativos si gastó mucho
    
    return {
        'puntos_actuales': puntos_actuales,
        'ganancia_hoy': ganancia_bruta_hoy,
        'gasto_hoy': gasto_hoy,
        'ganancia_mes': ganancia_bruta_mes,
        'gasto_mes': gasto_mes,
        'total_gastado': gasto_total,
        'ganancia_total_neta': ganancia_neta_total,
        'promedio_diario': int(promedio_diario),
        'primer_registro': primer_registro['fecha'],
        'total_registros': len(registros_ordenados)
    }


def obtener_datos_grafica(perfil_nombre, dias=30):
    """
    Obtiene datos para la gráfica de un perfil
    
    Returns:
        tuple (fechas, puntos) o (None, None)
    """
    historial = cargar_historial()
    
    if perfil_nombre not in historial:
        return None, None
    
    registros = historial[perfil_nombre]['registros']
    if not registros:
        return None, None
    
    # Agrupar por día (tomar el último registro de cada día)
    por_dia = {}
    for r in registros:
        fecha = r['fecha']
        por_dia[fecha] = r['puntos']
    
    # Filtrar últimos N días
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    fechas = []
    puntos = []
    for fecha in sorted(por_dia.keys()):
        if fecha >= fecha_limite:
            fechas.append(datetime.strptime(fecha, '%Y-%m-%d'))
            puntos.append(por_dia[fecha])
    
    return fechas, puntos


def obtener_ganancia_diaria(perfil_nombre, dias=30):
    """
    Obtiene la ganancia diaria para un perfil
    
    Returns:
        tuple (fechas, ganancias) o (None, None)
    """
    historial = cargar_historial()
    
    if perfil_nombre not in historial:
        return None, None
    
    registros = historial[perfil_nombre]['registros']
    if len(registros) < 2:
        return None, None
    
    # Agrupar por día
    por_dia = {}
    for r in registros:
        fecha = r['fecha']
        if fecha not in por_dia:
            por_dia[fecha] = {'min': r['puntos'], 'max': r['puntos']}
        else:
            por_dia[fecha]['min'] = min(por_dia[fecha]['min'], r['puntos'])
            por_dia[fecha]['max'] = max(por_dia[fecha]['max'], r['puntos'])
    
    # Calcular ganancia diaria
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    fechas_ordenadas = sorted([f for f in por_dia.keys() if f >= fecha_limite])
    
    fechas = []
    ganancias = []
    
    for i, fecha in enumerate(fechas_ordenadas):
        if i == 0:
            # Primer día: usar diferencia dentro del mismo día
            ganancia = por_dia[fecha]['max'] - por_dia[fecha]['min']
        else:
            # Días siguientes: comparar con el máximo del día anterior
            fecha_anterior = fechas_ordenadas[i-1]
            ganancia = por_dia[fecha]['max'] - por_dia[fecha_anterior]['max']
        
        fechas.append(datetime.strptime(fecha, '%Y-%m-%d'))
        ganancias.append(max(0, ganancia))  # No mostrar ganancias negativas
    
    return fechas, ganancias


class DashboardWindow:
    """Ventana del Dashboard de Puntos"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("📊 Dashboard de Puntos - Microsoft Rewards")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        self.perfil_seleccionado = None
        
        self._crear_ui()
        self._cargar_datos()
    
    def _crear_ui(self):
        """Crea la interfaz del dashboard"""
        # Header
        header = tk.Frame(self.root, bg='#16213e', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Dashboard de Puntos - Microsoft Rewards",
            font=('Arial', 20, 'bold'),
            bg='#16213e',
            fg='white'
        ).pack(pady=20)
        
        # Container principal
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Lista de perfiles
        left_panel = tk.Frame(main_container, bg='#1a1a2e', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        tk.Label(
            left_panel,
            text="👥 Perfiles",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=(0, 10))
        
        # Lista de perfiles
        self.perfiles_listbox = tk.Listbox(
            left_panel,
            font=('Arial', 11),
            bg='#0f3460',
            fg='white',
            selectbackground='#e94560',
            selectforeground='white',
            height=15,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.perfiles_listbox.pack(fill=tk.BOTH, expand=True)
        self.perfiles_listbox.bind('<<ListboxSelect>>', self._on_perfil_select)
        
        # Botón actualizar
        tk.Button(
            left_panel,
            text="🔄 Actualizar",
            command=self._cargar_datos,
            bg='#e94560',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(pady=10, fill=tk.X)
        
        # Botón ver todos
        tk.Button(
            left_panel,
            text="📊 Resumen General",
            command=self._mostrar_resumen_general,
            bg='#0f3460',
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(pady=5, fill=tk.X)
        
        # Panel derecho - Dashboard
        self.right_panel = tk.Frame(main_container, bg='#1a1a2e')
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Placeholder inicial
        self._mostrar_placeholder()
    
    def _mostrar_placeholder(self):
        """Muestra mensaje inicial"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.right_panel,
            text="👈 Selecciona un perfil para ver las estadísticas",
            font=('Arial', 16),
            bg='#1a1a2e',
            fg='#888'
        ).pack(expand=True)
    
    def _cargar_datos(self):
        """Carga los perfiles en la lista"""
        self.perfiles_listbox.delete(0, tk.END)
        
        historial = cargar_historial()
        
        if not historial:
            self.perfiles_listbox.insert(tk.END, "No hay datos aún...")
            return
        
        for perfil, datos in historial.items():
            email = datos.get('email', 'Sin email')
            registros = datos.get('registros', [])
            if registros:
                ultimo_puntos = registros[-1]['puntos']
                self.perfiles_listbox.insert(tk.END, f"💰 {ultimo_puntos:,} - {email}")
            else:
                self.perfiles_listbox.insert(tk.END, f"❓ {email}")
        
        self.perfiles_nombres = list(historial.keys())
    
    def _on_perfil_select(self, event):
        """Maneja la selección de un perfil"""
        selection = self.perfiles_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx < len(self.perfiles_nombres):
            self.perfil_seleccionado = self.perfiles_nombres[idx]
            self._mostrar_dashboard_perfil(self.perfil_seleccionado)
    
    def _crear_stat_card(self, parent, titulo, valor, color='#0f3460', icon='📊'):
        """Crea una tarjeta de estadística"""
        card = tk.Frame(parent, bg=color, padx=15, pady=15)
        
        tk.Label(
            card,
            text=f"{icon} {titulo}",
            font=('Arial', 10),
            bg=color,
            fg='#aaa'
        ).pack(anchor=tk.W)
        
        tk.Label(
            card,
            text=str(valor),
            font=('Arial', 24, 'bold'),
            bg=color,
            fg='white'
        ).pack(anchor=tk.W, pady=(5, 0))
        
        return card
    
    def _mostrar_dashboard_perfil(self, perfil_nombre):
        """Muestra el dashboard de un perfil específico"""
        # Limpiar panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        historial = cargar_historial()
        if perfil_nombre not in historial:
            self._mostrar_placeholder()
            return
        
        email = historial[perfil_nombre].get('email', 'Sin email')
        stats = obtener_estadisticas(perfil_nombre)
        
        if not stats:
            tk.Label(
                self.right_panel,
                text="No hay suficientes datos para mostrar estadísticas",
                font=('Arial', 14),
                bg='#1a1a2e',
                fg='#888'
            ).pack(expand=True)
            return
        
        # Header del perfil
        header_frame = tk.Frame(self.right_panel, bg='#1a1a2e')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text=f"👤 {email}",
            font=('Arial', 18, 'bold'),
            bg='#1a1a2e',
            fg='white'
        ).pack(anchor=tk.W)
        
        tk.Label(
            header_frame,
            text=f"📁 {perfil_nombre} | Registros desde: {stats['primer_registro']}",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#888'
        ).pack(anchor=tk.W)
        
        # Grid de estadísticas
        stats_frame = tk.Frame(self.right_panel, bg='#1a1a2e')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configurar grid (4 columnas, 2 filas)
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1, uniform='stat')
        
        # --- FILA 1: Ganancias ---
        
        # Puntos Actuales (con indicador si tiene 6550+)
        PUNTOS_PARA_CANJEAR = 6550
        puntos_actuales = stats['puntos_actuales']
        
        if puntos_actuales >= PUNTOS_PARA_CANJEAR:
            # Tiene suficientes puntos para canjear
            card1 = self._crear_stat_card(
                stats_frame, "✨ ¡LISTO PARA CANJEAR!", 
                f"{puntos_actuales:,}", '#f39c12', '🎁'
            )
        else:
            # Aún no tiene suficientes
            faltan = PUNTOS_PARA_CANJEAR - puntos_actuales
            card1 = self._crear_stat_card(
                stats_frame, f"Puntos (faltan {faltan:,})", 
                f"{puntos_actuales:,}", '#0f3460', '💰'
            )
        card1.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Ganancia Hoy (Bruta)
        card2 = self._crear_stat_card(
            stats_frame, "Ganado Hoy", 
            f"+{stats['ganancia_hoy']:,}",
            '#27ae60', '📈'
        )
        card2.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        # Ganancia Mes
        card3 = self._crear_stat_card(
            stats_frame, "Ganado Mes", 
            f"+{stats['ganancia_mes']:,}",
            '#8e44ad', '📅'
        )
        card3.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        
        # Promedio Diario
        card4 = self._crear_stat_card(
            stats_frame, "Promedio Diario", 
            f"~{stats['promedio_diario']:,}/día",
            '#2980b9', '📊'
        )
        card4.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')

        # --- FILA 2: Gastos (si hay actividad) ---
        if stats['total_gastado'] > 0:
            # Gasto Hoy
            card5 = self._crear_stat_card(
                stats_frame, "Gastado Hoy", 
                f"-{stats['gasto_hoy']:,}",
                '#c0392b' if stats['gasto_hoy'] > 0 else '#34495e', '💸'
            )
            card5.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
            
            # Gasto Mes
            card6 = self._crear_stat_card(
                stats_frame, "Gastado Mes", 
                f"-{stats['gasto_mes']:,}",
                '#c0392b' if stats['gasto_mes'] > 0 else '#34495e', '📉'
            )
            card6.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
            
            # Gasto Total Histórico
            card7 = self._crear_stat_card(
                stats_frame, "Gasto Total", 
                f"-{stats['total_gastado']:,}",
                '#c0392b', '🏦'
            )
            card7.grid(row=1, column=3, padx=5, pady=5, sticky='nsew')
        
        # Gráficas
        if MATPLOTLIB_DISPONIBLE:
            self._mostrar_graficas(perfil_nombre)
        else:
            tk.Label(
                self.right_panel,
                text="⚠️ Instala matplotlib para ver gráficas: pip install matplotlib",
                font=('Arial', 12),
                bg='#1a1a2e',
                fg='#f39c12'
            ).pack(pady=20)
    
    def _mostrar_graficas(self, perfil_nombre):
        """Muestra las gráficas de puntos"""
        # Frame para gráficas
        graficas_frame = tk.Frame(self.right_panel, bg='#1a1a2e')
        graficas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear figura con 2 subplots
        fig = Figure(figsize=(10, 5), dpi=100, facecolor='#1a1a2e')
        
        # Gráfica 1: Evolución de puntos
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor('#0f3460')
        ax1.set_title('📈 Evolución de Puntos', color='white', fontsize=12, pad=10)
        
        fechas, puntos = obtener_datos_grafica(perfil_nombre, dias=30)
        if fechas and puntos:
            ax1.plot(fechas, puntos, color='#e94560', linewidth=2, marker='o', markersize=4)
            ax1.fill_between(fechas, puntos, alpha=0.3, color='#e94560')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            fig.autofmt_xdate()
        
        ax1.tick_params(colors='white')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['left'].set_color('white')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.yaxis.label.set_color('white')
        ax1.xaxis.label.set_color('white')
        
        # Gráfica 2: Ganancia diaria
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor('#0f3460')
        ax2.set_title('📊 Ganancia Diaria', color='white', fontsize=12, pad=10)
        
        fechas_g, ganancias = obtener_ganancia_diaria(perfil_nombre, dias=14)
        if fechas_g and ganancias:
            colors = ['#27ae60' if g > 0 else '#e74c3c' for g in ganancias]
            ax2.bar(fechas_g, ganancias, color=colors, alpha=0.8)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        
        ax2.tick_params(colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        fig.tight_layout(pad=2.0)
        
        # Añadir canvas
        canvas = FigureCanvasTkAgg(fig, master=graficas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _mostrar_resumen_general(self):
        """Muestra un resumen de todos los perfiles"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        historial = cargar_historial()
        
        if not historial:
            tk.Label(
                self.right_panel,
                text="No hay datos aún...",
                font=('Arial', 14),
                bg='#1a1a2e',
                fg='#888'
            ).pack(expand=True)
            return
        
        # Header
        tk.Label(
            self.right_panel,
            text="📊 Resumen General - Todos los Perfiles",
            font=('Arial', 18, 'bold'),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=(0, 20))
        
        # Tabla de resumen
        tabla_frame = tk.Frame(self.right_panel, bg='#0f3460')
        tabla_frame.pack(fill=tk.X, padx=10)
        
        # Encabezados
        headers = ['Email', 'Puntos', 'Hoy', 'Mes', 'Promedio']
        for i, h in enumerate(headers):
            tk.Label(
                tabla_frame,
                text=h,
                font=('Arial', 11, 'bold'),
                bg='#16213e',
                fg='white',
                padx=15,
                pady=10
            ).grid(row=0, column=i, sticky='nsew')
        
        # Datos
        total_puntos = 0
        total_hoy = 0
        total_mes = 0
        
        for row, (perfil, datos) in enumerate(historial.items(), start=1):
            email = datos.get('email', 'Sin email')
            stats = obtener_estadisticas(perfil)
            
            if stats:
                valores = [
                    email[:25] + '...' if len(email) > 25 else email,
                    f"{stats['puntos_actuales']:,}",
                    f"+{stats['ganancia_hoy']:,}",
                    f"+{stats['ganancia_mes']:,}",
                    f"~{stats['promedio_diario']:,}/día"
                ]
                total_puntos += stats['puntos_actuales']
                total_hoy += stats['ganancia_hoy']
                total_mes += stats['ganancia_mes']
            else:
                valores = [email[:25], '---', '---', '---', '---']
            
            for col, val in enumerate(valores):
                color = '#27ae60' if col in [2, 3] and '+' in str(val) else 'white'
                tk.Label(
                    tabla_frame,
                    text=val,
                    font=('Arial', 10),
                    bg='#0f3460' if row % 2 == 0 else '#1a1a2e',
                    fg=color,
                    padx=15,
                    pady=8
                ).grid(row=row, column=col, sticky='nsew')
        
        # Configurar columnas
        for i in range(5):
            tabla_frame.grid_columnconfigure(i, weight=1)
        
        # Totales
        totales_frame = tk.Frame(self.right_panel, bg='#1a1a2e')
        totales_frame.pack(fill=tk.X, pady=20, padx=10)
        
        # Grid de totales
        for i in range(3):
            totales_frame.grid_columnconfigure(i, weight=1, uniform='total')
        
        card1 = self._crear_stat_card(
            totales_frame, "TOTAL Puntos (todos)", 
            f"{total_puntos:,}", '#2980b9', '💎'
        )
        card1.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        card2 = self._crear_stat_card(
            totales_frame, "TOTAL Ganancia Hoy", 
            f"+{total_hoy:,}", '#27ae60', '📈'
        )
        card2.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        card3 = self._crear_stat_card(
            totales_frame, "TOTAL Ganancia Mes", 
            f"+{total_mes:,}", '#8e44ad', '📅'
        )
        card3.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
    
    def run(self):
        """Inicia la ventana"""
        self.root.mainloop()


# Función para abrir el dashboard desde otra ventana
def abrir_dashboard(parent=None):
    """Abre la ventana del dashboard"""
    dashboard = DashboardWindow(parent)
    if not parent:
        dashboard.run()
    return dashboard


if __name__ == "__main__":
    if not MATPLOTLIB_DISPONIBLE:
        print("⚠️ Para gráficas completas, instala matplotlib:")
        print("   pip install matplotlib")
        print()
    
    app = DashboardWindow()
    app.run()

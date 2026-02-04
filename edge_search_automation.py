"""
Script de Automatización de Búsquedas en Microsoft Edge
Autor: Asistente de IA
Fecha: Febrero 2026

Este script automatiza búsquedas en Bing usando Microsoft Edge con múltiples perfiles
de usuario, simulando comportamiento humano para evitar detección.
"""

import time
import random
import threading
import os
import shutil
import tempfile
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from faker import Faker

# ============================================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================================

# Directorio base de User Data de Edge
USER_DATA_DIR = r"C:\Users\Pablo\AppData\Local\Microsoft\Edge\User Data"

# Lista de nombres de perfiles (subdirectorios dentro de User Data)
# IMPORTANTE: Modifica estos nombres según tus perfiles reales
PERFILES_EDGE = [
    "Default",      # Perfil principal
    "Profile 2",    # Segundo perfil
    "Profile 4",    # Tercer perfil
    "Profile 5",    # Cuarto perfil
    "Profile 6",    # Quinto perfil
    "Profile 7"     # Sexto perfil
    # Añade más perfiles según necesites
]

# Número de búsquedas por perfil
BUSQUEDAS_POR_PERFIL = 30

# Tiempo de espera aleatorio entre búsquedas (en segundos)
TIEMPO_MIN = 25
TIEMPO_MAX = 65

# Modo headless (True = sin ver el navegador, False = ver el navegador)
MODO_HEADLESS = False

# Usar perfiles originales directamente (True) o copiar a temporal (False)
# Por defecto False para ejecución simultánea
USAR_PERFILES_ORIGINALES = False

# Lista de perfiles que DEBEN usar el perfil original (cuentas de trabajo/educativas)
# Estos perfiles NO se ejecutarán simultáneamente pero mantendrán su autenticación
PERFILES_MODO_ORIGINAL = ["Profile 2"]  # Agregar aquí otros perfiles de trabajo si es necesario

# ============================================================================
# GENERACIÓN DE BÚSQUEDAS REALISTAS
# ============================================================================

def generar_busquedas_realistas(cantidad):
    """
    Genera búsquedas realistas usando Faker y combinaciones predefinidas.
    
    Args:
        cantidad (int): Número de búsquedas a generar
        
    Returns:
        list: Lista de frases de búsqueda
    """
    fake = Faker('es_ES')  # Usar español de España
    busquedas = []
    
    # Categorías de búsquedas predefinidas
    categorias = {
        'clima': ['clima en {}', 'pronóstico del tiempo {}', 'temperatura en {}'],
        'recetas': ['receta de {}', 'cómo cocinar {}', 'ingredientes para {}'],
        'lugares': ['historia de {}', 'turismo en {}', 'qué ver en {}'],
        'preguntas': ['cómo {}', 'por qué {}', 'cuándo {}'],
        'compras': ['precio de {}', 'comprar {}', 'ofertas de {}'],
        'noticias': ['noticias de {}', 'últimas noticias {}', 'actualidad {}'],
        'educación': ['curso de {}', 'aprender {}', 'tutorial de {}'],
        'salud': ['síntomas de {}', 'tratamiento para {}', 'causas de {}'],
    }
    
    # Temas para combinar con las categorías
    temas = {
        'clima': [fake.city() for _ in range(10)],
        'recetas': ['pasta', 'pollo', 'pizza', 'ensalada', 'arroz', 'pescado', 'tarta', 'sopa'],
        'lugares': [fake.city() for _ in range(10)],
        'preguntas': ['hacer pan', 'aprender inglés', 'programar en Python', 'meditar', 'ahorrar dinero'],
        'compras': ['laptop', 'teléfono móvil', 'auriculares', 'monitor', 'teclado', 'ratón'],
        'noticias': ['tecnología', 'economía', 'deportes', 'ciencia', 'cultura'],
        'educación': ['Python', 'Excel', 'Photoshop', 'inglés', 'guitarra', 'fotografía'],
        'salud': ['gripe', 'dolor de cabeza', 'insomnio', 'estrés', 'ansiedad'],
    }
    
    # Búsquedas adicionales predefinidas
    busquedas_extra = [
        'mejor portátil calidad precio 2026',
        'restaurantes cerca de mi',
        'películas en cartelera',
        'cómo instalar Windows 11',
        'diferencia entre Python 2 y 3',
        'beneficios del ejercicio diario',
        'mejores destinos turísticos Europa',
        'cuándo es el próximo eclipse solar',
        'historia del arte contemporáneo',
        'recetas veganas fáciles',
    ]
    
    # Generar búsquedas mezclando categorías
    for _ in range(cantidad):
        if random.random() < 0.3:  # 30% de búsquedas predefinidas
            busquedas.append(random.choice(busquedas_extra))
        else:  # 70% de búsquedas generadas
            categoria = random.choice(list(categorias.keys()))
            plantilla = random.choice(categorias[categoria])
            tema = random.choice(temas[categoria])
            busquedas.append(plantilla.format(tema))
    
    return busquedas


def scroll_aleatorio(driver):
    """
    Realiza scroll aleatorio en la página para simular comportamiento humano.
    
    Args:
        driver: Instancia del WebDriver
    """
    # Número aleatorio de scrolls (1-3)
    num_scrolls = random.randint(1, 3)
    
    for _ in range(num_scrolls):
        # Scroll hacia abajo una distancia aleatoria
        scroll_down = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_down});")
        time.sleep(random.uniform(0.5, 1.5))
        
        # 50% de probabilidad de hacer scroll hacia arriba
        if random.random() < 0.5:
            scroll_up = random.randint(100, 400)
            driver.execute_script(f"window.scrollBy(0, -{scroll_up});")
            time.sleep(random.uniform(0.3, 1.0))


def crear_driver_edge(nombre_perfil, headless=False, puerto_debug=None):
    """
    Crea y configura una instancia del driver de Edge.
    
    Args:
        nombre_perfil (str): Nombre del perfil de Edge (ej: 'Default', 'Profile 2')
        headless (bool): Si True, ejecuta el navegador en modo headless
        puerto_debug (int): Puerto único para remote-debugging
        
    Returns:
        webdriver: Instancia configurada del WebDriver
    """
    opciones = Options()
    
    # Configurar directorio base de User Data
    opciones.add_argument(f"user-data-dir={USER_DATA_DIR}")
    
    # Especificar el perfil específico a usar
    opciones.add_argument(f"profile-directory={nombre_perfil}")
    
    # Agregar puerto de debugging único para permitir múltiples instancias
    if puerto_debug:
        opciones.add_argument(f"--remote-debugging-port={puerto_debug}")
    
    # Modo headless
    if headless:
        opciones.add_argument("--headless")
    
    # Opciones adicionales para evitar detección
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    
    # Permitir múltiples procesos y ventanas separadas
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--new-window")  # Forzar nueva ventana
    opciones.add_argument(f"--window-position={puerto_debug * 50},{puerto_debug * 30}")  # Posición única
    
    # Deshabilitar compartir procesos entre ventanas
    opciones.add_argument("--disable-features=RendererCodeIntegrity")
    opciones.add_argument("--process-per-site")
    
    # Configurar User-Agent realista
    opciones.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    # Crear servicio - Intentar usar webdriver_manager, si falla usar el driver del sistema
    try:
        servicio = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=servicio, options=opciones)
    except Exception as e:
        print(f"⚠️  No se pudo descargar el driver automáticamente: {e}")
        print("🔄 Intentando usar el driver del sistema...")
        # Selenium buscará msedgedriver.exe en el PATH del sistema
        driver = webdriver.Edge(options=opciones)
    
    # Ejecutar script para ocultar webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def crear_driver_edge_temp(temp_user_data, nombre_perfil, headless=False, puerto_debug=None):
    """
    Crea un driver de Edge usando un directorio temporal de User Data.
    
    Args:
        temp_user_data (str): Ruta al directorio temporal de User Data
        nombre_perfil (str): Nombre del perfil
        headless (bool): Si True, ejecuta en modo headless
        puerto_debug (int): Puerto único para debugging
        
    Returns:
        webdriver: Instancia configurada del WebDriver
    """
    opciones = Options()
    
    # Usar el directorio temporal como User Data
    opciones.add_argument(f"user-data-dir={temp_user_data}")
    opciones.add_argument(f"profile-directory={nombre_perfil}")
    
    # Agregar puerto de debugging único para permitir múltiples instancias
    if puerto_debug:
        opciones.add_argument(f"--remote-debugging-port={puerto_debug}")
    
    # Modo headless
    if headless:
        opciones.add_argument("--headless")
    
    # Opciones adicionales para evitar detección
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    
    # Permitir múltiples procesos y ventanas separadas
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--new-window")  # Forzar nueva ventana
    opciones.add_argument(f"--window-position={puerto_debug * 50},{puerto_debug * 30}")  # Posición única
    
    # Deshabilitar compartir procesos entre ventanas
    opciones.add_argument("--disable-features=RendererCodeIntegrity")
    opciones.add_argument("--process-per-site")
    
    # Configurar User-Agent realista
    opciones.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    # Crear servicio - Intentar usar webdriver_manager, si falla usar el driver del sistema
    try:
        servicio = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=servicio, options=opciones)
    except Exception as e:
        print(f"⚠️  No se pudo descargar el driver automáticamente: {e}")
        print("🔄 Intentando usar el driver del sistema...")
        # Selenium buscará msedgedriver.exe en el PATH del sistema
        driver = webdriver.Edge(options=opciones)
    
    # Ejecutar script para ocultar webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def realizar_busqueda(driver, texto_busqueda):
    """
    Realiza una búsqueda en Bing.
    
    Args:
        driver: Instancia del WebDriver
        texto_busqueda (str): Texto a buscar
        
    Returns:
        bool: True si la búsqueda fue exitosa, False en caso contrario
    """
    try:
        # Verificar si el driver aún está activo
        try:
            driver.current_url
        except Exception:
            print("❌ Error: Sesión del navegador inválida")
            return False
        
        # Ir a Bing
        driver.get("https://www.bing.com")
        
        # Esperar a que la caja de búsqueda esté disponible
        wait = WebDriverWait(driver, 10)
        caja_busqueda = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # Limpiar caja de búsqueda
        caja_busqueda.clear()
        
        # Escribir el texto de búsqueda con pequeñas pausas (simular tipeo humano)
        for caracter in texto_busqueda:
            caja_busqueda.send_keys(caracter)
            time.sleep(random.uniform(0.05, 0.15))
        
        # Presionar Enter
        caja_busqueda.send_keys(Keys.RETURN)
        
        # Esperar a que carguen los resultados
        time.sleep(random.uniform(2, 4))
        
        # Realizar scroll aleatorio
        scroll_aleatorio(driver)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al realizar búsqueda: {e}")
        return False



def obtener_puntos_recompensa(driver, timeout=2):
    """
    Intenta obtener los puntos de Microsoft Rewards.
    
    Args:
        driver: Instancia del WebDriver
        timeout: Tiempo máximo de espera en segundos
        
    Returns:
        str: Puntos encontrados o None
    """
    try:
        # Método 1: ID directo 'id_rc' (el más común en Bing)
        try:
            # Usar find_elements primero para no esperar si no existe
            if driver.find_elements(By.ID, "id_rc"):
                elem = driver.find_element(By.ID, "id_rc")
                if elem.is_displayed():
                    texto = elem.text
                    # A veces devuelve vacío si está cargando
                    if texto and any(c.isdigit() for c in texto):
                        return texto
        except:
            pass

        # Método 2: Selectores CSS alternativos
        try:
            selectores = [
                "#id_rc", 
                "span[id='id_rc']", 
                ".points-container", 
                "a#id_rh div", # Contenedor dentro del enlace de rewards
                "div[id='id_rc']"
            ]
            
            for selector in selectores:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elementos:
                    if elem.is_displayed():
                        texto = elem.text
                        if texto and any(c.isdigit() for c in texto):
                            return texto
        except:
            pass
            
        return None
    except Exception:
        return None


def procesar_perfil(nombre_perfil, numero_perfil, callback_progreso=None, detener_flag=None, callback_info=None, busquedas_iniciales=0):
    """
    Procesa un perfil de Edge realizando las búsquedas programadas.
    
    Args:
        nombre_perfil (str): Nombre del perfil (ej: 'Default', 'Profile 2')
        numero_perfil (int): Número del perfil (para logging)
        callback_progreso (callable): Función a llamar después de cada búsqueda con el número completado
        detener_flag (callable): Función que retorna True si se debe detener
        callback_info (callable): Función para reportar información extra (ej. puntos)
        busquedas_iniciales (int): Número de búsquedas ya completadas (para continuar progreso)
    """
    print(f"\n{'='*70}")
    print(f"🚀 INICIANDO PERFIL #{numero_perfil}: {nombre_perfil}")
    print(f"{'='*70}\n")
    
    driver = None
    temp_user_data = None
    
    try:
        # Determinar si este perfil específico requiere modo original
        usar_original = USAR_PERFILES_ORIGINALES or (nombre_perfil in PERFILES_MODO_ORIGINAL)
        
        if usar_original:
            # ========== MODO ORIGINAL: Usar perfil directamente ==========
            print("🔧 Usando perfil original directamente (modo trabajo/educativo)")
            print("⚠️  NOTA: Este perfil mantiene autenticación completa")
            print("⚠️  IMPORTANTE: Asegúrate de que Edge NO esté abierto con este perfil")
            print(f"📁 Perfil: {os.path.join(USER_DATA_DIR, nombre_perfil)}\n")
            
            # Crear driver con el perfil original
            print("🔧 Configurando driver de Edge...")
            puerto_debug = 9222 + numero_perfil
            try:
                driver = crear_driver_edge(nombre_perfil, headless=MODO_HEADLESS, puerto_debug=puerto_debug)
                print("✅ Driver creado correctamente\n")
            except Exception as e:
                error_msg = str(e)
                if "session not created" in error_msg or "Chrome instance exited" in error_msg:
                    print(f"\n❌ ERROR: No se pudo iniciar Edge con el perfil '{nombre_perfil}'")
                    print("   Posibles causas:")
                    print("   1. Edge ya está abierto con este perfil - CIÉRRALO primero")
                    print("   2. Otro proceso está usando el perfil")
                    print("   3. El perfil está corrupto")
                    print("\n   💡 SOLUCIÓN: Cierra todas las ventanas de Edge y vuelve a intentar")
                    if callback_info:
                        callback_info({'tipo': 'error', 'valor': 'Edge abierto con este perfil. Ciérralo primero.'})
                raise
            
        else:
            # ========== MODO TEMPORAL: Copiar perfil a directorio temporal ==========
            print("🔧 Usando copia temporal del perfil (modo simultáneo)")
            
            # Crear directorio temporal para User Data de este perfil
            temp_user_data = tempfile.mkdtemp(prefix=f"edge_user_data_{numero_perfil}_")
            print(f"📂 Directorio temporal: {temp_user_data}")
            
            # Ruta del perfil original
            perfil_original = os.path.join(USER_DATA_DIR, nombre_perfil)
            perfil_temporal = os.path.join(temp_user_data, nombre_perfil)
            
            # Copiar el perfil completo al directorio temporal
            print(f"📋 Copiando perfil '{nombre_perfil}' (esto puede tardar unos segundos)...")
            
            if os.path.exists(perfil_original):
                # Copiar solo los archivos esenciales para velocidad
                os.makedirs(perfil_temporal, exist_ok=True)
                
                # Archivos esenciales para autenticación y sesión
                archivos_esenciales = [
                    'Cookies', 'Cookies-journal',
                    'Login Data', 'Login Data-journal', 
                    'Web Data', 'Web Data-journal',
                    'Preferences', 'Secure Preferences',
                    'Network', 'Local State',
                    'History', 'History-journal',
                    'Favicons', 'Favicons-journal',
                    'Shortcuts', 'Shortcuts-journal',
                    'Top Sites', 'Top Sites-journal',
                ]
                
                for archivo in archivos_esenciales:
                    origen = os.path.join(perfil_original, archivo)
                    if os.path.exists(origen):
                        destino = os.path.join(perfil_temporal, archivo)
                        try:
                            if os.path.isfile(origen):
                                shutil.copy2(origen, destino)
                            elif os.path.isdir(origen):
                                shutil.copytree(origen, destino, ignore_errors=True)
                        except Exception as e:
                            pass  # Ignorar archivos bloqueados
                
                # Copiar archivos críticos del User Data raíz
                archivos_raiz = ['Local State', 'First Run', 'Last Version']
                for archivo in archivos_raiz:
                    origen = os.path.join(USER_DATA_DIR, archivo)
                    if os.path.exists(origen):
                        try:
                            shutil.copy2(origen, os.path.join(temp_user_data, archivo))
                        except Exception:
                            pass
            
                print("✅ Perfil copiado\n")
                
                # Crear driver con el directorio temporal
                print("🔧 Configurando driver de Edge...")
                puerto_debug = 9222 + numero_perfil  # Puerto único por perfil
                driver = crear_driver_edge_temp(temp_user_data, nombre_perfil, headless=MODO_HEADLESS, puerto_debug=puerto_debug)
                print("✅ Driver creado correctamente\n")
            else:
                print(f"❌ ERROR: No se encontró el perfil '{nombre_perfil}' en {USER_DATA_DIR}")
                return
        
        # Verificar si hay sesión activa intentando ir a una página de Microsoft
        try:
            driver.get("https://www.bing.com")
            time.sleep(2)
            # Intentar verificar si está logueado
            print("🔍 Verificando estado de sesión...")
            time.sleep(1)
            
            # Intentar obtener puntos
            puntos = obtener_puntos_recompensa(driver)
            if puntos:
                print(f"💰 Puntos encontrados: {puntos}")
                if callback_info:
                    callback_info({'tipo': 'puntos', 'valor': puntos})
        except Exception:
            pass
        
        # Calcular cuántas búsquedas faltan
        busquedas_restantes = BUSQUEDAS_POR_PERFIL - busquedas_iniciales
        
        if busquedas_restantes <= 0:
            print(f"✅ Este perfil ya completó las {BUSQUEDAS_POR_PERFIL} búsquedas hoy")
            return BUSQUEDAS_POR_PERFIL
        
        # Generar búsquedas
        print(f"📝 Generando {busquedas_restantes} búsquedas realistas (continuando desde {busquedas_iniciales})...")
        busquedas = generar_busquedas_realistas(busquedas_restantes)
        print("✅ Búsquedas generadas\n")
        
        # Realizar búsquedas
        busquedas_completadas = busquedas_iniciales
        puntos_detectados = False # Flag para saber si ya tenemos puntos
        
        for i, busqueda in enumerate(busquedas, 1):
            # Número real de búsqueda (considerando las ya hechas)
            num_busqueda_real = busquedas_iniciales + i
            # Verificar si se debe detener
            if detener_flag and detener_flag():
                print(f"\n⏹️ Búsquedas detenidas por usuario en {busquedas_completadas}/{BUSQUEDAS_POR_PERFIL}")
                break
            
            print(f"🔍 Búsqueda {num_busqueda_real}/{BUSQUEDAS_POR_PERFIL}: '{busqueda}'")
            
            # Realizar la búsqueda
            exito = realizar_busqueda(driver, busqueda)
            
            if exito:
                print(f"✅ Búsqueda completada")
                busquedas_completadas = num_busqueda_real
                
                # Intentar leer puntos si aún no se han detectado o actualizar cada 5 búsquedas
                if not puntos_detectados or num_busqueda_real % 5 == 0:
                    try:
                        pts = obtener_puntos_recompensa(driver, timeout=1)
                        if pts:
                            puntos_detectados = True
                            if callback_info:
                                callback_info({'tipo': 'puntos', 'valor': pts})
                    except:
                        pass
            else:
                print(f"⚠️  Búsqueda con errores")
                busquedas_completadas = num_busqueda_real  # Contar aunque tenga errores
            
            # Llamar al callback de progreso si existe
            if callback_progreso:
                continuar = callback_progreso(num_busqueda_real)
                # Si el callback retorna False, detener
                if continuar is False:
                    print(f"\n⏹️ Detenido por callback en {num_busqueda_real}/{BUSQUEDAS_POR_PERFIL}")
                    break
            
            # Espera aleatoria antes de la siguiente búsqueda (excepto en la última)
            if num_busqueda_real < BUSQUEDAS_POR_PERFIL:
                tiempo_espera = random.randint(TIEMPO_MIN, TIEMPO_MAX)
                print(f"⏳ Esperando {tiempo_espera} segundos antes de la siguiente búsqueda...")
                time.sleep(tiempo_espera)
                print()
        
        if busquedas_completadas >= BUSQUEDAS_POR_PERFIL:
            print(f"\n✅ PERFIL #{numero_perfil} COMPLETADO - {BUSQUEDAS_POR_PERFIL} búsquedas realizadas")
        else:
            print(f"\n⏹️ PERFIL #{numero_perfil} DETENIDO - {busquedas_completadas}/{BUSQUEDAS_POR_PERFIL} búsquedas realizadas")
        
        return busquedas_completadas
        
    except Exception as e:
        print(f"\n❌ ERROR EN PERFIL #{numero_perfil} ({nombre_perfil}): {e}")
        return 0
        
    finally:
        # Cerrar el navegador
        if driver:
            print(f"🔒 Cerrando navegador del perfil #{numero_perfil}...")
            try:
                driver.quit()
            except Exception:
                pass
            print(f"✅ Navegador cerrado")
        
        # Limpiar directorio temporal
        if temp_user_data and os.path.exists(temp_user_data):
            print(f"🧹 Limpiando archivos temporales...")
            try:
                time.sleep(1)  # Esperar a que Edge libere los archivos
                shutil.rmtree(temp_user_data, ignore_errors=True)
            except Exception:
                pass
            print(f"✅ Limpieza completada\n")


def main():
    """
    Función principal que ejecuta el script.
    """
    print("\n" + "="*70)
    print(" 🤖 SCRIPT DE AUTOMATIZACIÓN DE BÚSQUEDAS EN MICROSOFT EDGE")
    print("="*70)
    print(f"\n📊 Configuración:")
    print(f"   • Perfiles a procesar: {len(PERFILES_EDGE)}")
    print(f"   • Búsquedas por perfil: {BUSQUEDAS_POR_PERFIL}")
    print(f"   • Tiempo entre búsquedas: {TIEMPO_MIN}-{TIEMPO_MAX} segundos")
    print(f"   • Modo headless: {'Activado' if MODO_HEADLESS else 'Desactivado'}")
    print(f"   • Ejecución: SIMULTÁNEA (todos los perfiles a la vez)")
    print(f"\n⚠️  IMPORTANTE: Asegúrate de que las rutas de los perfiles sean correctas")
    print(f"   y que Edge esté cerrado antes de ejecutar el script.")
    print(f"\n⚠️  NOTA: Se abrirán {len(PERFILES_EDGE)} navegadores simultáneamente.")
    print(f"   Asegúrate de tener suficiente RAM y CPU.\n")
    
    input("Presiona Enter para continuar...")
    
    print("\n" + "="*70)
    print(" 🚀 INICIANDO TODOS LOS PERFILES SIMULTÁNEAMENTE")
    print("="*70 + "\n")
    
    # Crear un thread para cada perfil
    threads = []
    for i, perfil in enumerate(PERFILES_EDGE, 1):
        thread = threading.Thread(
            target=procesar_perfil,
            args=(perfil, i),
            name=f"Perfil-{i}"
        )
        threads.append(thread)
        thread.start()
        print(f"✅ Thread iniciado para Perfil #{i}")
        
        # Pequeña pausa para evitar que todos arranquen al mismo tiempo
        time.sleep(2)
    
    print(f"\n⏳ Esperando a que todos los perfiles terminen...\n")
    
    # Esperar a que todos los threads terminen
    for thread in threads:
        thread.join()
    
    print("\n" + "="*70)
    print(" 🎉 TODOS LOS PERFILES HAN SIDO PROCESADOS")
    print("="*70)
    print(f"\n📈 Resumen:")
    print(f"   • Total de perfiles procesados: {len(PERFILES_EDGE)}")
    print(f"   • Total de búsquedas realizadas: {len(PERFILES_EDGE) * BUSQUEDAS_POR_PERFIL}")
    print(f"\n✅ Script finalizado exitosamente.\n")


if __name__ == "__main__":
    main()

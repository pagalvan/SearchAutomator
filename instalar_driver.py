"""
Script auxiliar para instalar el driver de Edge manualmente
"""

import os
import sys
import zipfile
import urllib.request
import subprocess

def obtener_version_edge():
    """Obtiene la versión de Microsoft Edge instalada"""
    try:
        # Ruta del ejecutable de Edge
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        
        # Ejecutar comando para obtener la versión
        result = subprocess.run(
            ['powershell', '-Command', f'(Get-Item "{edge_path}").VersionInfo.ProductVersion'],
            capture_output=True,
            text=True
        )
        
        version = result.stdout.strip()
        return version
    except Exception as e:
        print(f"❌ Error al obtener la versión de Edge: {e}")
        return None

def descargar_driver(version):
    """Descarga el driver de Edge para la versión especificada"""
    try:
        # Extraer versión mayor
        version_mayor = version.split('.')[0]
        
        # URL de descarga del driver
        url = f"https://msedgedriver.azureedge.net/{version}/edgedriver_win64.zip"
        
        print(f"📥 Descargando driver desde: {url}")
        
        # Descargar archivo
        urllib.request.urlretrieve(url, "edgedriver.zip")
        
        print("✅ Driver descargado correctamente")
        
        # Extraer zip
        with zipfile.ZipFile("edgedriver.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        
        print("✅ Driver extraído correctamente")
        
        # Eliminar zip
        os.remove("edgedriver.zip")
        
        print(f"\n✅ ¡Instalación completada!")
        print(f"📁 El archivo msedgedriver.exe está en: {os.getcwd()}")
        print(f"\n💡 Ahora puedes ejecutar el script principal.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al descargar el driver: {e}")
        print("\n🔧 Descarga manual:")
        print("1. Ve a: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print(f"2. Descarga el driver para la versión {version}")
        print("3. Extrae msedgedriver.exe en esta carpeta")
        return False

def main():
    print("="*70)
    print(" 🔧 INSTALADOR DE DRIVER DE MICROSOFT EDGE")
    print("="*70)
    print()
    
    # Obtener versión de Edge
    print("🔍 Detectando versión de Microsoft Edge...")
    version = obtener_version_edge()
    
    if not version:
        print("\n⚠️  No se pudo detectar la versión de Edge automáticamente.")
        print("\nIngresa la versión manualmente (ej: 120.0.2210.121):")
        version = input("Versión: ").strip()
    else:
        print(f"✅ Versión detectada: {version}")
    
    print()
    
    # Descargar driver
    descargar_driver(version)

if __name__ == "__main__":
    main()

"""
Script para crear acceso directo del programa con icono personalizado
"""

import os
import sys

def crear_acceso_directo():
    """Crea un acceso directo en el escritorio"""
    
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("❌ Necesitas instalar pywin32 y winshell:")
        print("   pip install pywin32 winshell")
        return False
    
    # Rutas
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    script_principal = os.path.join(directorio_actual, "edge_search_gui.py")
    
    # Ruta del acceso directo en el escritorio
    escritorio = winshell.desktop()
    acceso_directo_path = os.path.join(escritorio, "Edge Search Automation.lnk")
    
    # Crear acceso directo
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(acceso_directo_path)
    
    # Configurar el acceso directo
    shortcut.Targetpath = sys.executable  # Python
    shortcut.Arguments = f'"{script_principal}"'
    shortcut.WorkingDirectory = directorio_actual
    shortcut.Description = "Automatización de búsquedas en Edge para Microsoft Rewards"
    
    # Icono - usar el de Edge o uno personalizado si existe
    icono_personalizado = os.path.join(directorio_actual, "icono.ico")
    if os.path.exists(icono_personalizado):
        shortcut.IconLocation = icono_personalizado
    else:
        # Usar icono de Microsoft Edge
        edge_icon = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(edge_icon):
            shortcut.IconLocation = edge_icon
    
    shortcut.save()
    
    print("✅ Acceso directo creado en el escritorio!")
    print(f"   📁 {acceso_directo_path}")
    print("\n💡 Para anclarlo a la barra de tareas:")
    print("   1. Ve al escritorio y busca 'Edge Search Automation'")
    print("   2. Clic derecho → 'Anclar a la barra de tareas'")
    
    return True


if __name__ == "__main__":
    crear_acceso_directo()

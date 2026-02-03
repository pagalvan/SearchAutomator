# 🤖 Edge Search Automation

Script de automatización de búsquedas en Microsoft Edge con comportamiento humano simulado.

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar perfiles
Edita `edge_search_automation.py` y actualiza la lista `PERFILES_EDGE` con las rutas de tus perfiles de Edge.

### 3. Ejecutar
```bash
python edge_search_automation.py
```

## 📋 Características

✅ **Múltiples perfiles**: Itera automáticamente sobre varios perfiles de Edge  
✅ **Búsquedas realistas**: Usa Faker para generar frases naturales  
✅ **Comportamiento humano**: Tipeo simulado, scrolls aleatorios, pausas variables  
✅ **Anti-detección**: Tiempos de espera de 25-65 segundos entre búsquedas  
✅ **Modo headless**: Opción para ejecutar sin interfaz gráfica  
✅ **Logging completo**: Progreso detallado en consola  

## 📖 Documentación

Lee [INSTRUCCIONES.md](INSTRUCCIONES.md) para una guía completa de instalación, configuración y uso.

## ⚠️ Advertencia

Este script es para fines educativos y de prueba. Úsalo responsablemente y de acuerdo con los términos de servicio de Microsoft/Bing.

## 🛠️ Requisitos

- Python 3.7+
- Microsoft Edge instalado
- Conexión a internet

## 📦 Dependencias

- `selenium` - Automatización web
- `webdriver-manager` - Gestión de drivers
- `faker` - Generación de datos realistas

# 📘 Instrucciones de Uso - Script de Automatización Edge

## 🔧 Instalación de Dependencias

### Paso 1: Instalar Python
Asegúrate de tener Python 3.7 o superior instalado. Verifica con:
```bash
python --version
```

### Paso 2: Instalar las librerías necesarias
Abre una terminal (PowerShell o CMD) en la carpeta del proyecto y ejecuta:

```bash
pip install selenium webdriver-manager faker
```

O instala desde el archivo de requisitos (ver abajo).

### Detalle de las librerías:
- **selenium**: Framework para automatización de navegadores web
- **webdriver-manager**: Gestiona automáticamente los drivers de navegadores
- **faker**: Genera datos realistas (nombres, ciudades, etc.)

---

## 📝 Configuración Inicial

### 1. Localizar las rutas de tus perfiles de Edge

Las rutas de los perfiles de Edge suelen estar en:
```
C:\Users\TU_USUARIO\AppData\Local\Microsoft\Edge\User Data\
```

Dentro de esta carpeta encontrarás:
- `Default` (perfil principal)
- `Profile 1`, `Profile 2`, etc. (perfiles adicionales)

### 2. Editar el script

Abre `edge_search_automation.py` y modifica la lista `PERFILES_EDGE` con tus rutas:

```python
PERFILES_EDGE = [
    r"C:\Users\Pablo\AppData\Local\Microsoft\Edge\User Data\Default",
    r"C:\Users\Pablo\AppData\Local\Microsoft\Edge\User Data\Profile 1",
    r"C:\Users\Pablo\AppData\Local\Microsoft\Edge\User Data\Profile 2",
]
```

**Notas importantes:**
- Usa la `r` antes de las comillas para rutas en Windows
- Cada perfil debe estar en una línea separada
- Puedes agregar o quitar perfiles según necesites

### 3. Ajustar configuración (opcional)

En el script puedes modificar:

```python
BUSQUEDAS_POR_PERFIL = 35  # Número de búsquedas por perfil
TIEMPO_MIN = 25             # Tiempo mínimo entre búsquedas (segundos)
TIEMPO_MAX = 65             # Tiempo máximo entre búsquedas (segundos)
MODO_HEADLESS = False       # True = sin ver el navegador, False = ver el navegador
```

---

## ▶️ Ejecutar el Script

### Antes de ejecutar:
1. **CIERRA Microsoft Edge completamente** (incluyendo procesos en segundo plano)
2. Asegúrate de estar logueado en las cuentas de cada perfil

### Ejecutar:
```bash
python edge_search_automation.py
```

El script:
1. Mostrará la configuración
2. Pedirá confirmación para continuar
3. Procesará cada perfil secuencialmente
4. Mostrará el progreso en tiempo real

---

## 📊 Cómo Funciona

### Por cada perfil:
1. ✅ Abre Edge con el perfil especificado
2. ✅ Genera 35 búsquedas realistas usando Faker
3. ✅ Realiza cada búsqueda en Bing con:
   - Tipeo simulado (letra por letra con pausas)
   - Scroll aleatorio en resultados
   - Espera aleatoria de 25-65 segundos entre búsquedas
4. ✅ Cierra el navegador y pasa al siguiente perfil

### Tipos de búsquedas generadas:
- Clima en ciudades
- Recetas de cocina
- Información turística
- Preguntas educativas
- Búsquedas de compras
- Noticias y actualidad
- Tutoriales y cursos
- Temas de salud

---

## ⚠️ Advertencias y Consideraciones

### Detección de Spam
- Los tiempos de espera (25-65 segundos) están diseñados para evitar detección
- El script simula comportamiento humano (tipeo, scrolls, pausas)
- **NO** reduzcas los tiempos de espera o podrías activar protecciones anti-bot

### Recursos del Sistema
- Con `MODO_HEADLESS = False`, verás las ventanas del navegador
- Cada perfil consume recursos (RAM, CPU)
- El script puede tardar varias horas en completarse (35 búsquedas × ~45 seg promedio × número de perfiles)

### Privacidad
- El script usa tus perfiles reales de Edge con sesiones activas
- Las búsquedas se registrarán en tu historial de Bing/Microsoft
- Usa bajo tu propia responsabilidad

---

## 🐛 Solución de Problemas

### Error: "EdgeDriver not found"
```bash
pip install --upgrade webdriver-manager
```

### Error: "Cannot find Edge binary"
Verifica que Microsoft Edge esté instalado en la ruta estándar.

### El navegador no se abre
- Asegúrate de que Edge esté completamente cerrado
- Verifica que las rutas de los perfiles sean correctas
- Ejecuta el script como administrador si es necesario

### Las búsquedas no funcionan
- Verifica tu conexión a internet
- Asegúrate de que Bing.com sea accesible
- Revisa si hay captchas (indica detección de bot)

---

## 📦 Archivo requirements.txt

Si prefieres usar un archivo de requisitos, crea `requirements.txt`:

```
selenium>=4.15.0
webdriver-manager>=4.0.0
Faker>=20.0.0
```

E instala con:
```bash
pip install -r requirements.txt
```

---

## 🎯 Uso Avanzado

### Modo Headless (Sin ver el navegador)
```python
MODO_HEADLESS = True
```
Útil para ejecutar en segundo plano o en servidores.

### Personalizar búsquedas
Edita la función `generar_busquedas_realistas()` para agregar tus propias categorías y temas.

### Logging
Para guardar un registro, redirige la salida:
```bash
python edge_search_automation.py > log.txt 2>&1
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa que todas las dependencias estén instaladas
2. Verifica las rutas de los perfiles
3. Asegúrate de que Edge esté cerrado
4. Ejecuta con permisos de administrador si es necesario

---

## ⚖️ Disclaimer

Este script es para fines educativos y de prueba. El usuario es responsable del uso que le dé y de cumplir con los términos de servicio de Microsoft/Bing.

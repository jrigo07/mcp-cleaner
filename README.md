# ☁️ MCP Google Cloud Cleaner

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Security](https://img.shields.io/badge/Security-OAuth2_Local-red)

## 📖 Introducción

**MCP Cloud Cleaner** es una herramienta de código abierto que actúa como un "puente seguro" entre **Claude (Inteligencia Artificial)** y tus archivos de Google.

Le permite a la IA analizar qué está ocupando espacio, descargar copias de seguridad a tu disco duro local y limpiar la nube automáticamente. Todo esto se ejecuta 100% en tu computadora, garantizando que tus datos y credenciales nunca salgan de tu red local.

---

## 🛡️ Características de Seguridad

1. **Ejecución Local:** Tus credenciales (`credentials.json`) nunca se comparten con terceros.  
2. **Integridad SHA-256:** Verifica que la copia local coincide matemáticamente con el archivo en la nube antes de borrarlo.  
3. **Transaccionalidad:** Si la descarga falla, el archivo original NO se elimina.  
4. **Hardware Aware:** Revisa el espacio en disco (`psutil`) antes de descargar cualquier archivo.

---

## 🏗️ Estructura del Proyecto

```
mcp-cleaner/
│
├── config/                 # 🔐 Carpeta de seguridad (Ignorada por Git)
│   ├── credentials.json    # Credenciales de Google Cloud Console
│   └── token_combined.json # Token de sesión (Generado automáticamente)
│
├── server_mcp.py           # 🧠 CONTROLADOR: Recibe órdenes de Claude (JSON-RPC)
├── google_auth.py          # 🛡️ SEGURIDAD: Maneja OAuth2 y refresco de tokens
├── backup_manager.py       # 📦 MOTOR: Descarga y verifica integridad (SHA-256)
├── cleanup.py              # 🧹 LIMPIEZA: Ejecuta el borrado condicional
│
├── drive_tool.py           # ☁️ Sensor: Busca archivos en Drive
├── gmail_tool.py           # 📧 Sensor: Busca correos en Gmail
├── storage_detector.py     # 💾 Sensor: Lee tus discos duros locales
├── space_manager.py        # 📐 Calculadora: Decide qué archivos caben
│
├── setup_final.py          # ⚙️ Script de configuración (se corre 1 sola vez)
└── requirements.txt        # 📋 Dependencias del proyecto
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```
git clone https://github.com/TU_USUARIO/mcp-cleaner.git
cd mcp-cleaner
```

### 2. Instalar dependencias

```
pip install -r requirements.txt
```

### 3. Configurar Google Cloud (OAuth 2.0)

1. Ve a **Google Cloud Console**  
2. Crea un proyecto y habilita:  
   - Google Drive API  
   - Gmail API  
3. Ve a **Credenciales → Crear credenciales → ID de cliente OAuth**  
4. Tipo: **Aplicación de escritorio**  
5. Descarga el JSON y nómbralo:

```
credentials.json
```

6. Crear carpeta:

```
config/
```

7. Colocar dentro el JSON.

✔ La carpeta `config/` está en `.gitignore`.

---

## 4. Generar Tokens de Acceso

Ejecuta:

```
python setup_final.py
```

Autoriza en el navegador.

Esto generará:

```
config/token_combined.json
```

---

# 🔌 Conectar con Claude Desktop

Editar:

**macOS:**  
`~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:**  
`%APPDATA%/Claude/claude_desktop_config.json`

Insertar:

```json
{
  "mcpServers": {
    "google-cleaner": {
      "command": "python",
      "args": [
        "/RUTA/ABSOLUTA/HACIA/TU/PROYECTO/mcp-cleaner/server_mcp.py"
      ]
    }
  }
}
```

⚠️ Usa la **ruta absoluta completa**.

---

# 🧪 Ejemplo de Uso

- “Claude, analiza mi Google Drive y busca archivos mayores a 100MB que pueda borrar.”  
- “Haz un respaldo de los correos pesados de Gmail en D:/Backup y luego bórralos de la nube.”  

---

# ⚠️ Disclaimer

Este software puede borrar archivos.  
Aunque incluye múltiples verificaciones de seguridad (SHA-256), siempre haz respaldos críticos.  
El autor NO se hace responsable por pérdida de datos involuntaria.

## 🔧 Solución de Problemas (Troubleshooting)

Aquí están los errores más comunes que hemos encontrado y cómo solucionarlos:

### 1. Error: "Google hasn't verified this app" (Google no ha verificado esta aplicación)
**Síntoma:** Al ejecutar `setup_final.py`, el navegador muestra una advertencia roja de seguridad.
- **Causa:** Estás usando una aplicación OAuth propia que no ha pasado por la auditoría comercial de Google (lo cual es normal para proyectos personales).
- **Solución:**
  1. Haz clic en **"Advanced"** (Avanzado).
  2. Haz clic en **"Go to [Nombre de tu Proyecto] (unsafe)"** (Ir a ... no seguro).
  3. Escribe "Continue" si te lo pide y otorga los permisos.

### 2. Error: Claude muestra "Connection Failed" o el icono del enchufe en rojo 🔌❌
**Síntoma:** Claude Desktop no reconoce las herramientas.
- **Causa:** La ruta hacia `server_mcp.py` en el archivo de configuración no es absoluta o está mal escrita.
- **Solución:**
  - Abre el archivo de configuración de Claude.
  - Asegúrate de que la ruta empiece desde la raíz del disco.
  - **Mal:** `Code/mcp-cleaner/server_mcp.py`
  - **Bien (Windows):** `C:\\Users\\TuUsuario\\Code\\mcp-cleaner\\server_mcp.py`
  - *Nota:* En Windows, usa doble barra invertida `\\`.

### 3. Error: `FileNotFoundError: [Errno 2] No such file or directory: 'config/credentials.json'`
**Síntoma:** El script `setup_final.py` se cierra inmediatamente.
- **Causa:** No has descargado las credenciales de Google Cloud o no creaste la carpeta `config`.
- **Solución:**
  1. Crea una carpeta llamada `config` en la raíz del proyecto.
  2. Descarga el JSON de credenciales desde Google Cloud Console.
  3. Renómbralo obligatoriamente a `credentials.json` y mételo en esa carpeta.

### 4. Error: `RefreshError: ('invalid_grant', 'Bad Request')`
**Síntoma:** El servidor funcionaba bien, pero de repente falla la autenticación.
- **Causa:** El token de refresco ha caducado, fue revocado, o cambiaste los permisos (Scopes) en el código.
- **Solución:**
  1. Ve a la carpeta `config`.
  2. Borra el archivo `token_combined.json`.
  3. Ejecuta de nuevo `python setup_final.py` para generar un token limpio.

### 5. Error: API 403 Forbidden ("Access Not Configured")
**Síntoma:** El script falla al intentar listar archivos.
- **Causa:** Creaste el proyecto en Google Cloud pero olvidaste habilitar las APIs específicas.
- **Solución:**
  - Ve a la consola de Google Cloud -> "APIs & Services" -> "Library".
  - Busca y habilita: **Google Drive API** y **Gmail API**.

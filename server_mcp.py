import sys
import json
import os
import shutil
from datetime import datetime

# Importamos módulos
from storage_detector import list_local_drives
from drive_tool import get_drive_files, delete_drive_file
from gmail_tool import get_gmail_files, delete_gmail_message
from backup_manager import backup_file

def send(msg):
    sys.stdout.write(json.dumps(msg, default=str) + "\n")
    sys.stdout.flush()

# --- FUNCIONES LÓGICAS ---

def get_cloud_stats(criteria="size"):
    """Paso 1: Solo mirar qué hay, sin tocar nada."""
    print(f"Buscando archivos por criterio: {criteria}...", file=sys.stderr)
    d_files = get_drive_files(criteria, limit_count=50)
    g_files = get_gmail_files(criteria, limit_count=50)
    
    total_size = sum(f['size'] for f in d_files) + sum(f['size'] for f in g_files)
    
    return {
        "summary": f"Encontré {len(d_files)} archivos en Drive y {len(g_files)} correos grandes.",
        "total_size_gb": round(total_size / (1024**3), 2),
        "files_preview": (d_files[:3] + g_files[:3]), # Mostrar solo unos pocos de muestra
        "all_files_cache": d_files + g_files # Devolvemos todo para que Claude sepa qué tiene
    }

def execute_backup_plan(destination_path, size_limit_gb, file_list):
    """Paso 2: Ejecutar el backup con los límites confirmados."""
    
    if not os.path.exists(destination_path):
        try:
            os.makedirs(destination_path, exist_ok=True)
        except Exception as e:
            return {"error": f"No pude crear la carpeta {destination_path}. Error: {e}"}

    limit_bytes = float(size_limit_gb) * 1024 * 1024 * 1024
    current_bytes = 0
    backed_up = []
    
    folder_name = f"BACKUP_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
    final_dest = os.path.join(destination_path, folder_name)
    
    print("Iniciando respaldo...", file=sys.stderr)
    
    for f in file_list:
        if current_bytes + f['size'] > limit_bytes:
            break # Límite alcanzado
            
        res = backup_file(f, final_dest)
        if res['success']:
            backed_up.append(f)
            current_bytes += f['size']
            
    return {
        "status": "Respaldo terminado",
        "location": final_dest,
        "total_backed_up_gb": round(current_bytes / (1024**3), 2),
        "files_count": len(backed_up),
        "files_ready_to_delete": backed_up # Lista verificada para borrar
    }

def delete_confirmed_files(file_list):
    """Paso 3: Borrar SOLO lo que ya se respaldó."""
    deleted_count = 0
    errors = []
    
    for f in file_list:
        success = False
        if f['source'] == 'drive':
            success = delete_drive_file(f['id'])
        elif f['source'] == 'gmail':
            success = delete_gmail_message(f['id'])
        
        if success:
            deleted_count += 1
        else:
            errors.append(f['name'])
            
    return {"status": "Limpieza completada", "deleted": deleted_count, "errors": errors}

# --- DEFINICIÓN DE HERRAMIENTAS (LO QUE VE CLAUDE) ---

TOOLS = [
    {
        "name": "list_local_drives",
        "description": "Paso 1: Listar discos locales o USBs para ver espacio disponible y decidir dónde guardar.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "scan_cloud_files",
        "description": "Paso 2: Escanear Drive y Gmail. Permite elegir criterio (peso o fecha).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sort_criteria": {
                    "type": "string", 
                    "enum": ["size", "date"], 
                    "description": "'size' para los más pesados, 'date' para los más viejos."
                }
            },
            "required": ["sort_criteria"]
        }
    },
    {
        "name": "perform_backup",
        "description": "Paso 3: Realizar el respaldo físico de los archivos detectados, respetando un límite de GB.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "destination_path": {"type": "string", "description": "Ruta elegida por el usuario (ej: E:\\Backups)"},
                "limit_gb": {"type": "number", "description": "Límite máximo de GB a usar en el disco destino"},
                "files_to_backup": {
                    "type": "array", 
                    "description": "La lista de archivos obtenida en el paso de escaneo (se pasa tal cual)",
                    "items": {"type": "object"}
                }
            },
            "required": ["destination_path", "limit_gb", "files_to_backup"]
        }
    },
    {
        "name": "delete_cloud_files",
        "description": "Paso 4: (PELIGROSO) Borrar de la nube SOLO los archivos que se respaldaron exitosamente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "files_to_delete": {
                    "type": "array",
                    "description": "Lista de archivos confirmados del resultado de perform_backup",
                    "items": {"type": "object"}
                }
            },
            "required": ["files_to_delete"]
        }
    }
]

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
            if "method" not in req: continue
            
            method = req["method"]
            req_id = req.get("id")
            
            if method == "initialize":
                send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "smart-google-cleaner", "version": "2.0"}
                    }
                })
            
            elif method == "tools/list":
                send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
                
            elif method == "tools/call":
                name = req["params"]["name"]
                args = req["params"].get("arguments", {})
                res = {}

                if name == "list_local_drives":
                    res = list_local_drives()
                    
                elif name == "scan_cloud_files":
                    res = get_cloud_stats(args.get("sort_criteria", "size"))
                    
                elif name == "perform_backup":
                    res = execute_backup_plan(
                        args["destination_path"], 
                        args["limit_gb"], 
                        args["files_to_backup"]
                    )
                    
                elif name == "delete_cloud_files":
                    res = delete_confirmed_files(args["files_to_delete"])
                
                else:
                    res = {"error": "Herramienta no encontrada"}
                
                send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, default=str)}]}
                })
        except:
            continue

if __name__ == "__main__":
    main()
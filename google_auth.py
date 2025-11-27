import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --- RUTAS A PRUEBA DE BALAS ---
# Esto obtiene la ruta exacta donde está ESTE archivo .py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# Aseguramos que la carpeta config exista
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token_combined.json")

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

def get_service(service_name, version):
    creds = None
    
    # 1. Intentar cargar token existente
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception:
            # Si el archivo está corrupto, lo borramos
            print("Token corrupto, borrando...")
            os.remove(TOKEN_PATH)
            creds = None

    # 2. Si no hay credenciales válidas, iniciar sesión (ESTO ES LO QUE FALLA EN SEGUNDO PLANO)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                print("No se pudo refrescar el token.")
                creds = None
        
        # Si seguimos sin credenciales, hay que pedir login manual
        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"CRÍTICO: No encuentro '{CREDENTIALS_PATH}'. \n"
                    f"Asegúrate de poner el archivo credentials.json en la carpeta config."
                )
            
            print("Iniciando flujo de autenticación manual...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 3. Guardar el token para que la próxima vez sea automático
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            print(f"Token guardado exitosamente en: {TOKEN_PATH}")

    return build(service_name, version, credentials=creds, static_discovery=False)
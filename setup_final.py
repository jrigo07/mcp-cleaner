from google_auth import get_service

print("--- INICIANDO CONFIGURACIÓN DE ACCESO ---")
print("Se abrirá una ventana de navegador. Por favor, inicia sesión y acepta TODO.")
print("Si te dice 'App no segura', dale a 'Avanzado' -> 'Ir a Cleaner (inseguro)'.")

# Esto forzará la creación del token
try:
    # Probamos Drive
    print("\n1. Conectando a Drive...")
    srv_drive = get_service('drive', 'v3')
    print("   ✅ Drive conectado.")

    # Probamos Gmail
    print("\n2. Conectando a Gmail...")
    srv_gmail = get_service('gmail', 'v1')
    print("   ✅ Gmail conectado.")
    
    print("\n---------------------------------------------------")
    print("¡LISTO! La llave maestra (token) ha sido guardada.")
    print("Ahora Claude podrá entrar sin pedirte permiso.")
    print("---------------------------------------------------")

except Exception as e:
    print(f"\n❌ ERROR FATAL: {e}")

input("Presiona Enter para cerrar...")
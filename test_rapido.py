from drive_tool import get_drive_files
from gmail_tool import get_gmail_files

print("--- PRUEBA DE DRIVE ---")
print("Buscando archivos...")
files = get_drive_files(limit_count=5) # Solo 5 para probar
print(f"¡ÉXITO! Encontré {len(files)} archivos en Drive.")

print("\n--- PRUEBA DE GMAIL ---")
print("Buscando correos...")
mails = get_gmail_files(limit_count=5) # Solo 5 para probar
print(f"¡ÉXITO! Encontré {len(mails)} correos en Gmail.")

print("\n--- TODO LISTO ---")
input("Presiona Enter para salir...")
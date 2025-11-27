from google_auth import get_service

def get_drive_files(criteria="size", limit_count=20):
    service = get_service('drive', 'v3')
    files = []
    
    order_by = "quotaBytesUsed desc" if criteria == "size" else "modifiedTime"
    query = "trashed = false and mimeType != 'application/vnd.google-apps.folder'"
    
    try:
        results = service.files().list(
            q=query,
            pageSize=limit_count,
            fields="files(id, name, size, modifiedTime)", # Pedimos MENOS datos para ir rápido
            orderBy=order_by
        ).execute()
        
        items = results.get('files', [])
        for item in items:
            if 'size' in item:
                files.append({
                    'id': item['id'],
                    'name': item['name'],
                    'size': int(item['size']),
                    'date': item.get('modifiedTime'),
                    'source': 'drive'
                })
    except Exception as e:
        # Si falla Drive, imprimimos error pero retornamos lista vacía para no colgar
        print(f"Error Drive API: {e}")
            
    return files

def delete_drive_file(file_id):
    service = get_service('drive', 'v3')
    try:
        service.files().update(fileId=file_id, body={'trashed': True}).execute()
        return True
    except:
        return False
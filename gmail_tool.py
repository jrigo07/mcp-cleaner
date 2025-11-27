from google_auth import get_service

def get_gmail_files(criteria="size", limit_count=15):
    """
    Versión optimizada: Trae menos correos (15) para evitar desconexión por timeout.
    """
    service = get_service('gmail', 'v1')
    messages_list = []
    
    # Buscamos solo correos con adjuntos
    query = "has:attachment"
    
    try:
        # Pedimos solo los IDs para ir rápido
        response = service.users().messages().list(userId='me', q=query, maxResults=limit_count).execute()
        messages = response.get('messages', [])
        
        # Procesamos uno por uno (esto es lo que tarda, por eso bajamos el límite)
        for msg in messages:
            try:
                # 'format=minimal' es mucho más rápido que 'full'
                meta = service.users().messages().get(userId='me', id=msg['id'], format='minimal').execute()
                size = int(meta.get('sizeEstimate', 0))
                date = int(meta.get('internalDate', 0))
                
                # Solo guardar si pesa más de 500KB (ignoramos firmas e iconos pequeños)
                if size > 500000:
                    messages_list.append({
                        'id': msg['id'],
                        'name': f"Email_{msg['id']}.eml",
                        'size': size,
                        'timestamp': date, 
                        'source': 'gmail'
                    })
            except:
                continue
                
    except Exception as e:
        print(f"Error Gmail: {e}")
        return [] # Retornar lista vacía en vez de romper
    
    # Ordenar
    if criteria == "date":
        messages_list.sort(key=lambda x: x['timestamp'])
    else:
        messages_list.sort(key=lambda x: x['size'], reverse=True)
        
    return messages_list

def delete_gmail_message(msg_id):
    service = get_service('gmail', 'v1')
    try:
        service.users().messages().trash(userId='me', id=msg_id).execute()
        return True
    except:
        return False
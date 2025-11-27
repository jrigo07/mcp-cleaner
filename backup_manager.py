import os
import hashlib
import requests
import base64
from googleapiclient.http import MediaIoBaseDownload
from google_auth import get_service

def compute_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def backup_file(file_info, base_path):
    try:
        source = file_info['source']
        dest_folder = os.path.join(base_path, source.upper())
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, file_info['name'])
        
        if source == 'drive':
            service = get_service('drive', 'v3')
            request = service.files().get_media(fileId=file_info['id'])
            with open(dest_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done: _, done = downloader.next_chunk()
                    
        elif source == 'gmail':
            service = get_service('gmail', 'v1')
            msg = service.users().messages().get(userId='me', id=file_info['id'], format='raw').execute()
            with open(dest_path + ".eml", "wb") as f:
                f.write(base64.urlsafe_b64decode(msg['raw'].encode('ASCII')))
            dest_path += ".eml"

        elif source == 'photos':
            r = requests.get(file_info['url_download'], stream=True)
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        
        return {"success": True, "path": dest_path, "hash": compute_sha256(dest_path), "file_info": file_info}
    except Exception as e:
        return {"success": False, "error": str(e)}
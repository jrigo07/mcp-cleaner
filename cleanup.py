from drive_tool import delete_drive_file
from gmail_tool import delete_gmail_message

def process_deletion(backup_results):
    deleted_count = 0
    space_freed = 0
    failed = []
    
    for item in backup_results:
        if item['success']:
            info = item['file_info']
            # Aquí podrías comparar hashes si tuvieras el remoto
            res = False
            if info['source'] == 'drive': res = delete_drive_file(info['id'])
            elif info['source'] == 'gmail': res = delete_gmail_message(info['id'])
            
            if res:
                deleted_count += 1
                space_freed += info.get('size', 0)
            else:
                failed.append(info['name'])
                
    return {"deleted": deleted_count, "freed_mb": round(space_freed/(1024*1024),2), "failed": failed}
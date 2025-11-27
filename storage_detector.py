import psutil
import shutil

def list_local_drives():
    drives = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        try:
            usage = shutil.disk_usage(p.mountpoint)
            drives.append({
                'device': p.device,
                'mountpoint': p.mountpoint,
                'total_gb': round(usage.total / (1024**3), 2),
                'free_gb': round(usage.free / (1024**3), 2),
                'free_bytes': usage.free
            })
        except: continue
    return drives
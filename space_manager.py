def select_files_to_fit(available_bytes, all_files):
    # Ordenar por tamaño (los más grandes primero)
    sorted_files = sorted(all_files, key=lambda x: x.get('size', 0), reverse=True)
    selected = []
    current_size = 0
    # Dejamos 100MB de margen de seguridad
    limit = available_bytes - (100 * 1024 * 1024)
    
    for f in sorted_files:
        f_size = f.get('size', 0)
        if f_size == 0: f_size = 50 * 1024 * 1024 # Estimar 50MB si es desconocido
        
        if current_size + f_size <= limit:
            selected.append(f)
            current_size += f_size
            
    return {'files': selected, 'total_size_gb': round(current_size/(1024**3), 2)}
import os
from datetime import datetime
import zipfile
import shutil

def comprimir_carpeta(carpeta_origen, archivo_zip):
    """Comprime todos los archivos de una carpeta en un ZIP"""
    
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Recorrer todos los archivos en la carpeta
        for archivo in os.listdir(carpeta_origen):
            ruta_completa = os.path.join(carpeta_origen, archivo)
            # Solo comprimir archivos, no subcarpetas
            if os.path.isfile(ruta_completa):
                zipf.write(ruta_completa, arcname=archivo)

    shutil.move(archivo_zip, carpeta_origen)  # Mover el archivo ZIP a la carpeta original


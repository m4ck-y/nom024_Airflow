import requests
from pathlib import Path
from urllib.parse import urlparse


def download_file_from_url(url: str, download_directory: Path, filename: str = None) -> Path:
    """
    Descarga un archivo desde una URL al directorio especificado.
    
    Args:
        url: URL del archivo a descargar
        download_directory: Directorio donde guardar el archivo
        filename: Nombre personalizado para el archivo (opcional)
        
    Returns:
        Path: Ruta completa del archivo descargado
        
    Raises:
        requests.RequestException: Si hay un error en la descarga
        OSError: Si hay un error al escribir el archivo
    """
    # Crear directorio si no existe
    download_directory.mkdir(parents=True, exist_ok=True)
    
    # Determinar nombre del archivo
    if filename is None:
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name or "downloaded_file"
    
    local_file_path = download_directory / filename
    
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(local_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                
    return local_file_path

from pathlib import Path
from tmp.spreadsheet.pipeline import process_web_page_to_database

BASE_URL = "http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html"
DOWNLOAD_DIR = Path("tmp")


def process_nationalities_data(url: str = BASE_URL, download_directory: Path = DOWNLOAD_DIR) -> None:
    """
    Procesa datos de nacionalidades desde una página web específica.
    
    Descarga y procesa archivos Excel con información de nacionalidades
    desde el sitio web del gobierno mexicano.
    
    Args:
        url: URL de la página web a procesar
        download_directory: Directorio donde descargar los archivos temporales
    """
    print("Iniciando descarga y carga de nacionalidades...")
    process_web_page_to_database(url, download_directory)

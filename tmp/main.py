import logging
from pathlib import Path
from tmp.spreadsheet.pipeline import process_web_page_to_database
from tmp.nacionalidades import process_nationalities_data

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

DOWNLOAD_DIR = Path("tmp")
URLS = [
    "http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html",
    # Agrega más URLs si lo deseas
]


def run_batch_pipeline(urls: list[str], download_directory: Path) -> None:
    """
    Ejecuta el pipeline de procesamiento para múltiples URLs.
    
    Args:
        urls: Lista de URLs a procesar
        download_directory: Directorio donde descargar los archivos
    """
    for url in urls:
        logging.info(f"Procesando URL: {url}")
        result = process_web_page_to_database(url, download_directory)
        if result:
            logging.info(f"✔ Procesado: {result}")
        else:
            logging.warning("⚠ No se procesó ningún archivo.")


if __name__ == "__main__":
    process_nationalities_data()
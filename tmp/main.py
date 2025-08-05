import logging
from tmp.spreadsheet.pipeline import process_page_and_load_to_db

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DOWNLOAD_DIR = "tmp/"
URLS = [
    "http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html",
    # Agrega más URLs si lo deseas
]


from tmp.nacionalidades import download_and_load_nationalities

if __name__ == "__main__":
    download_and_load_nationalities()


def run_pipeline_batch():
    for url in URLS:
        logging.info(f"Procesando URL: {url}")
        result = process_page_and_load_to_db(url, DOWNLOAD_DIR)
        if result:
            logging.info(f"✔ Procesado: {result}")
        else:
            logging.warning("⚠ No se procesó ningún archivo.")
from tmp.spreadsheet.pipeline import process_page_and_load_to_db

BASE_URL = "http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html"
DOWNLOAD_DIR = "tmp/"


def download_and_load_nationalities():
    print("Iniciando descarga y carga de nacionalidades...")
    process_page_and_load_to_db(BASE_URL, DOWNLOAD_DIR)

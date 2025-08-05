import os
import logging
from typing import Optional
from urllib.parse import urlparse

from tmp.html import get_html_elements, get_element_attribute
from tmp.downloader import download_file_from_url
from tmp.zip import extract_first_spreadsheet
from tmp.url import resolve_url
from tmp.spreadsheet.transform import (
    read_excel_to_dataframe,
    #transform_and_load_nationalities
)

logger = logging.getLogger(__name__)
ZIP_EXTENSIONS = (".zip",)
EXCEL_EXTENSIONS = (".xls", ".xlsx")


def has_extension(url: str, extensions: tuple[str]) -> bool:
    return urlparse(url).path.lower().endswith(extensions)


def process_page_and_load_to_db(page_url: str, download_dir: str) -> Optional[str]:
    for anchor in get_html_elements(page_url, "a"):
        href_relative = get_element_attribute(anchor, "href")
        if not href_relative:
            continue

        file_url = resolve_url(page_url, href_relative)
        if not file_url:
            continue

        logger.info(f"Enlace encontrado: {file_url}")

        if has_extension(file_url, ZIP_EXTENSIONS):
            zip_path = download_file_from_url(file_url, download_dir)
            extracted_excel = extract_first_spreadsheet(zip_path, download_dir)
            os.remove(zip_path)
            if extracted_excel:
                return process_excel_and_load(extracted_excel)

        elif has_extension(file_url, EXCEL_EXTENSIONS):
            excel_path = download_file_from_url(file_url, download_dir)
            if excel_path:
                return process_excel_and_load(excel_path)

    logger.warning("No se encontró ningún archivo válido.")
    return None


def process_excel_and_load(file_path: str) -> Optional[str]:
    try:
        df = read_excel_to_dataframe(file_path)
        #transform_and_load_nationalities(df)
        logger.info(f"Archivo cargado correctamente: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error al cargar {file_path}: {e}")
        return None

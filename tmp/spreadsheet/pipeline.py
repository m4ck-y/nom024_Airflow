import os
import logging
from typing import Optional, Dict, Callable
from urllib.parse import urlparse
import pandas as pd

from tmp.html import extract_html_elements_by_tag, get_element_attribute_value
from tmp.downloader import download_file_from_url
from tmp.zip import extract_spreadsheet_from_zip
from tmp.url import resolve_relative_url
from tmp.spreadsheet.transform import load_excel_file_to_dataframe
from tmp.database_loader import save_dataframe_to_sqlite

logger = logging.getLogger(__name__)
ZIP_EXTENSIONS = (".zip",)
EXCEL_EXTENSIONS = (".xls", ".xlsx")


def has_extension(url: str, extensions: tuple[str]) -> bool:
    """Verifica si una URL tiene alguna de las extensiones especificadas."""
    return urlparse(url).path.lower().endswith(extensions)


def find_spreadsheet_links(page_url: str) -> list[str]:
    """Encuentra todos los enlaces a archivos Excel o ZIP en una página."""
    spreadsheet_links = []
    
    for anchor in extract_html_elements_by_tag(page_url, "a"):
        href_relative = get_element_attribute_value(anchor, "href")
        if not href_relative:
            continue

        file_url = resolve_relative_url(page_url, href_relative)
        if not file_url:
            continue

        if has_extension(file_url, ZIP_EXTENSIONS + EXCEL_EXTENSIONS):
            spreadsheet_links.append(file_url)
            logger.info(f"Enlace encontrado: {file_url}")
    
    return spreadsheet_links


def download_and_extract_spreadsheet(file_url: str, download_dir: str) -> Optional[str]:
    """Descarga y extrae un archivo de hoja de cálculo."""
    from pathlib import Path
    
    download_path = Path(download_dir)
    
    if has_extension(file_url, ZIP_EXTENSIONS):
        zip_path = download_file_from_url(file_url, download_path)
        extracted_excel = extract_spreadsheet_from_zip(zip_path, download_path)
        if zip_path.exists():
            zip_path.unlink()  # Limpiar archivo ZIP
        return str(extracted_excel) if extracted_excel else None
    
    elif has_extension(file_url, EXCEL_EXTENSIONS):
        excel_path = download_file_from_url(file_url, download_path)
        return str(excel_path)
    
    return None


def process_spreadsheet_and_save_to_database(
    page_url: str, 
    download_dir: str,
    transform_data: Callable[[pd.DataFrame], pd.DataFrame],
    column_mapping: Dict[str, str] = None,
    table_name: str = "datos",
    db_path: str = "tmp/data.db"
) -> bool:
    """
    Pipeline general para procesar hojas de cálculo desde una página web.
    
    Args:
        page_url: URL de la página que contiene enlaces a archivos
        download_dir: Directorio donde descargar archivos
        transform_data: Función para transformar el DataFrame
        column_mapping: Mapeo de nombres de columnas
        table_name: Nombre de la tabla en la base de datos
        db_path: Ruta de la base de datos SQLite
    
    Returns:
        True si el proceso fue exitoso, False en caso contrario
    """
    try:
        # Encontrar enlaces a hojas de cálculo
        spreadsheet_links = find_spreadsheet_links(page_url)
        if not spreadsheet_links:
            logger.warning("No se encontraron enlaces a archivos de hoja de cálculo.")
            return False
        
        # Procesar el primer archivo encontrado
        file_url = spreadsheet_links[0]
        logger.info(f"Procesando archivo: {file_url}")
        
        # Descargar y extraer archivo
        excel_path = download_and_extract_spreadsheet(file_url, download_dir)
        if not excel_path:
            logger.error("No se pudo descargar o extraer el archivo.")
            return False
        
        # Leer archivo Excel
        df = load_excel_file_to_dataframe(excel_path)
        logger.info(f"Archivo leído: {len(df)} filas encontradas")
        
        # Aplicar mapeo de columnas si se proporciona
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Transformar datos
        df_transformed = transform_data(df)
        
        # Cargar a base de datos
        from pathlib import Path
        save_dataframe_to_sqlite(df_transformed, Path(db_path), table_name)
        logger.info(f"Datos cargados exitosamente en la tabla '{table_name}'")
        
        # Limpiar archivo descargado
        if os.path.exists(excel_path):
            os.remove(excel_path)
        
        return True
        
    except Exception as e:
        logger.error(f"Error en el pipeline: {e}")
        return False
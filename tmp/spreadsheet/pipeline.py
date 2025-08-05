import logging
from pathlib import Path
from typing import Optional, Tuple, List
from urllib.parse import urlparse

from tmp.html import extract_html_elements_by_tag, get_element_attribute_value
from tmp.downloader import download_file_from_url
from tmp.zip import extract_spreadsheet_from_zip
from tmp.url import resolve_relative_url
from tmp.spreadsheet.transform import (
    load_excel_file_to_dataframe,
    transform_nationalities_data,
    prepare_data_for_database
)
from tmp.database_loader import save_dataframe_to_sqlite

logger = logging.getLogger(__name__)

# Constantes para extensiones de archivo
ZIP_EXTENSIONS = (".zip",)
EXCEL_EXTENSIONS = (".xls", ".xlsx")


def check_url_has_extension(url: str, extensions: Tuple[str, ...]) -> bool:
    """
    Verifica si una URL tiene alguna de las extensiones especificadas.
    
    Args:
        url: URL a verificar
        extensions: Tupla de extensiones a buscar
        
    Returns:
        bool: True si la URL tiene alguna de las extensiones
    """
    return urlparse(url).path.lower().endswith(extensions)


def find_downloadable_files_in_page(page_url: str) -> List[str]:
    """
    Encuentra todos los archivos descargables (ZIP y Excel) en una página web.
    
    Args:
        page_url: URL de la página web a analizar
        
    Returns:
        List[str]: Lista de URLs de archivos descargables
    """
    downloadable_files = []
    
    try:
        anchor_elements = extract_html_elements_by_tag(page_url, "a")
        
        for anchor in anchor_elements:
            href_relative = get_element_attribute_value(anchor, "href")
            if not href_relative:
                continue

            file_url = resolve_relative_url(page_url, href_relative)
            if not file_url:
                continue

            # Verificar si es un archivo descargable
            if (check_url_has_extension(file_url, ZIP_EXTENSIONS) or 
                check_url_has_extension(file_url, EXCEL_EXTENSIONS)):
                downloadable_files.append(file_url)
                logger.info(f"Archivo descargable encontrado: {file_url}")
                
    except Exception as e:
        logger.error(f"Error al buscar archivos en la página {page_url}: {e}")
    
    return downloadable_files


def process_zip_file(zip_url: str, download_directory: Path) -> Optional[Path]:
    """
    Descarga y procesa un archivo ZIP, extrayendo hojas de cálculo.
    
    Args:
        zip_url: URL del archivo ZIP
        download_directory: Directorio donde descargar y extraer
        
    Returns:
        Optional[Path]: Ruta del archivo Excel extraído o None si no se encontró
    """
    try:
        # Descargar archivo ZIP
        zip_path = download_file_from_url(zip_url, download_directory)
        logger.info(f"ZIP descargado: {zip_path}")
        
        # Extraer hoja de cálculo
        extracted_excel = extract_spreadsheet_from_zip(zip_path, download_directory)
        
        # Limpiar archivo ZIP temporal
        zip_path.unlink(missing_ok=True)
        
        if extracted_excel:
            logger.info(f"Excel extraído: {extracted_excel}")
            return extracted_excel
        else:
            logger.warning(f"No se encontró ninguna hoja de cálculo en {zip_path}")
            
    except Exception as e:
        logger.error(f"Error al procesar archivo ZIP {zip_url}: {e}")
    
    return None


def process_excel_file(excel_url: str, download_directory: Path) -> Optional[Path]:
    """
    Descarga un archivo Excel directamente.
    
    Args:
        excel_url: URL del archivo Excel
        download_directory: Directorio donde descargar
        
    Returns:
        Optional[Path]: Ruta del archivo Excel descargado o None si hubo error
    """
    try:
        excel_path = download_file_from_url(excel_url, download_directory)
        logger.info(f"Excel descargado: {excel_path}")
        return excel_path
    except Exception as e:
        logger.error(f"Error al descargar archivo Excel {excel_url}: {e}")
        return None


def process_spreadsheet_and_save_to_database(file_path: Path, 
                                           database_path: Path = None,
                                           table_name: str = "nacionalidades") -> bool:
    """
    Procesa una hoja de cálculo y guarda los datos en la base de datos.
    
    Args:
        file_path: Ruta del archivo Excel a procesar
        database_path: Ruta de la base de datos (opcional)
        table_name: Nombre de la tabla donde guardar los datos
        
    Returns:
        bool: True si el procesamiento fue exitoso
    """
    try:
        # Cargar datos desde Excel
        logger.info(f"Cargando datos desde {file_path}")
        dataframe = load_excel_file_to_dataframe(file_path)
        logger.info(f"Datos cargados desde {file_path}: {len(dataframe)} filas")
        
        # Transformar datos
        transformed_data = transform_nationalities_data(dataframe)
        logger.info(f"Datos transformados: {len(transformed_data)} filas")
        
        # Preparar para base de datos
        final_data = prepare_data_for_database(transformed_data)
        
        # Guardar en base de datos
        if database_path is None:
            database_path = file_path.parent / "data.db"
            
        save_dataframe_to_sqlite(final_data, database_path, table_name, if_exists="replace")
        logger.info(f"Datos guardados en base de datos: {database_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al procesar {file_path}: {e}")
        return False


def process_web_page_to_database(page_url: str, download_directory: Path) -> Optional[Path]:
    """
    Procesa una página web completa: busca archivos, los descarga y procesa.
    
    Args:
        page_url: URL de la página web a procesar
        download_directory: Directorio donde descargar archivos temporales
        
    Returns:
        Optional[Path]: Ruta del último archivo procesado exitosamente o None
    """
    logger.info(f"Iniciando procesamiento de página: {page_url}")
    
    # Crear directorio de descarga si no existe
    download_directory.mkdir(parents=True, exist_ok=True)
    
    # Buscar archivos descargables
    downloadable_files = find_downloadable_files_in_page(page_url)
    
    if not downloadable_files:
        logger.warning("No se encontraron archivos descargables en la página.")
        return None
    
    processed_file = None
    
    # Procesar cada archivo encontrado
    for file_url in downloadable_files:
        try:
            if check_url_has_extension(file_url, ZIP_EXTENSIONS):
                excel_file = process_zip_file(file_url, download_directory)
            elif check_url_has_extension(file_url, EXCEL_EXTENSIONS):
                excel_file = process_excel_file(file_url, download_directory)
            else:
                continue
            
            if excel_file and excel_file.exists():
                success = process_spreadsheet_and_save_to_database(excel_file)
                if success:
                    processed_file = excel_file
                    logger.info(f"✔ Procesamiento exitoso: {excel_file}")
                else:
                    logger.warning(f"⚠ Error en el procesamiento: {excel_file}")
                    
        except Exception as e:
            logger.error(f"Error al procesar archivo {file_url}: {e}")
    
    if processed_file is None:
        logger.warning("No se pudo procesar ningún archivo correctamente.")
    
    return processed_file

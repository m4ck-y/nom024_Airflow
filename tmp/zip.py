import zipfile
from pathlib import Path
from typing import Optional, List


def extract_spreadsheet_from_zip(zip_file_path: Path, extraction_directory: Path, 
                                 extract_first_only: bool = True) -> Optional[Path]:
    """
    Extrae archivos de hoja de cálculo (.xls, .xlsx) de un archivo ZIP.
    
    Args:
        zip_file_path: Ruta al archivo ZIP
        extraction_directory: Directorio donde extraer los archivos
        extract_first_only: Si True, extrae solo el primer archivo encontrado
        
    Returns:
        Optional[Path]: Ruta del archivo extraído o None si no se encontró ninguno
        
    Raises:
        zipfile.BadZipFile: Si el archivo ZIP está corrupto
        FileNotFoundError: Si el archivo ZIP no existe
    """
    if not zip_file_path.exists():
        raise FileNotFoundError(f"El archivo ZIP no existe: {zip_file_path}")
    
    # Crear directorio de extracción si no existe
    extraction_directory.mkdir(parents=True, exist_ok=True)
    
    spreadsheet_extensions = ('.xlsx', '.xls')
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith(spreadsheet_extensions):
                zip_ref.extract(file_name, extraction_directory)
                extracted_path = extraction_directory / file_name
                
                if extract_first_only:
                    return extracted_path
                    
    return None


def list_spreadsheet_files_in_zip(zip_file_path: Path) -> List[str]:
    """
    Lista todos los archivos de hoja de cálculo dentro de un ZIP.
    
    Args:
        zip_file_path: Ruta al archivo ZIP
        
    Returns:
        List[str]: Lista de nombres de archivos de hoja de cálculo
        
    Raises:
        zipfile.BadZipFile: Si el archivo ZIP está corrupto
        FileNotFoundError: Si el archivo ZIP no existe
    """
    if not zip_file_path.exists():
        raise FileNotFoundError(f"El archivo ZIP no existe: {zip_file_path}")
    
    spreadsheet_extensions = ('.xlsx', '.xls')
    spreadsheet_files = []
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith(spreadsheet_extensions):
                spreadsheet_files.append(file_name)
                
    return spreadsheet_files


def extract_all_files_from_zip(zip_file_path: Path, extraction_directory: Path) -> List[Path]:
    """
    Extrae todos los archivos de un ZIP.
    
    Args:
        zip_file_path: Ruta al archivo ZIP
        extraction_directory: Directorio donde extraer los archivos
        
    Returns:
        List[Path]: Lista de rutas de archivos extraídos
        
    Raises:
        zipfile.BadZipFile: Si el archivo ZIP está corrupto
        FileNotFoundError: Si el archivo ZIP no existe
    """
    if not zip_file_path.exists():
        raise FileNotFoundError(f"El archivo ZIP no existe: {zip_file_path}")
    
    # Crear directorio de extracción si no existe
    extraction_directory.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extraction_directory)
        for file_name in zip_ref.namelist():
            extracted_files.append(extraction_directory / file_name)
            
    return extracted_files

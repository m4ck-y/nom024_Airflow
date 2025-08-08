import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_excel_file_to_dataframe(file_path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """
    Carga un archivo Excel y lo convierte en un DataFrame.
    
    Args:
        file_path: Ruta del archivo Excel
        sheet_name: Nombre o índice de la hoja a leer (por defecto la primera)
        
    Returns:
        pd.DataFrame: Datos del archivo Excel
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si hay error al leer el archivo
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo Excel no existe: {file_path}")
    
    logger.info(f"Cargando archivo Excel: {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"Archivo cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
        return df
    except Exception as e:
        logger.error(f"Error al cargar archivo Excel {file_path}: {e}")
        raise ValueError(f"No se pudo leer el archivo Excel: {e}")


def clean_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los nombres de las columnas del DataFrame.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        pd.DataFrame: DataFrame con columnas limpias
    """
    df_cleaned = df.copy()
    
    # Limpiar nombres de columnas
    df_cleaned.columns = (
        df_cleaned.columns
        .str.strip()  # Eliminar espacios al inicio y final
        .str.lower()  # Convertir a minúsculas
        .str.replace(' ', '_')  # Reemplazar espacios con guiones bajos
        .str.replace('[^a-zA-Z0-9_]', '', regex=True)  # Eliminar caracteres especiales
    )
    
    logger.info(f"Columnas limpiadas: {list(df_cleaned.columns)}")
    return df_cleaned


def remove_empty_rows_and_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas y columnas completamente vacías.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        pd.DataFrame: DataFrame sin filas/columnas vacías
    """
    original_shape = df.shape
    
    # Eliminar filas completamente vacías
    df_cleaned = df.dropna(how='all')
    
    # Eliminar columnas completamente vacías
    df_cleaned = df_cleaned.dropna(axis=1, how='all')
    
    logger.info(f"Filas/columnas vacías eliminadas: {original_shape} -> {df_cleaned.shape}")
    return df_cleaned


def standardize_text_columns(df: pd.DataFrame, text_columns: list[str] = None) -> pd.DataFrame:
    """
    Estandariza las columnas de texto (elimina espacios, convierte a string).
    
    Args:
        df: DataFrame a procesar
        text_columns: Lista de columnas de texto a estandarizar (si None, detecta automáticamente)
        
    Returns:
        pd.DataFrame: DataFrame con columnas de texto estandarizadas
    """
    df_standardized = df.copy()
    
    if text_columns is None:
        # Detectar columnas de texto automáticamente
        text_columns = df_standardized.select_dtypes(include=['object']).columns.tolist()
    
    for col in text_columns:
        if col in df_standardized.columns:
            df_standardized[col] = (
                df_standardized[col]
                .astype(str)
                .str.strip()
                .replace('nan', '')
                .replace('None', '')
            )
    
    logger.info(f"Columnas de texto estandarizadas: {text_columns}")
    return df_standardized


def apply_column_mapping(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Aplica un mapeo de nombres de columnas.
    
    Args:
        df: DataFrame a procesar
        column_mapping: Diccionario con mapeo {nombre_original: nombre_nuevo}
        
    Returns:
        pd.DataFrame: DataFrame con columnas renombradas
    """
    df_mapped = df.copy()
    
    # Filtrar solo las columnas que existen en el DataFrame
    existing_mapping = {old: new for old, new in column_mapping.items() if old in df_mapped.columns}
    
    if existing_mapping:
        df_mapped = df_mapped.rename(columns=existing_mapping)
        logger.info(f"Columnas renombradas: {existing_mapping}")
    else:
        logger.warning("Ninguna columna del mapeo existe en el DataFrame")
    
    return df_mapped


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> pd.DataFrame:
    """
    Valida que el DataFrame tenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas requeridas
        
    Returns:
        pd.DataFrame: DataFrame validado
        
    Raises:
        ValueError: Si faltan columnas requeridas
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
    
    logger.info(f"Validación exitosa: todas las columnas requeridas están presentes")
    return df


def add_metadata_columns(df: pd.DataFrame, metadata: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Agrega columnas de metadatos al DataFrame.
    
    Args:
        df: DataFrame al cual agregar metadatos
        metadata: Diccionario con metadatos a agregar
        
    Returns:
        pd.DataFrame: DataFrame con metadatos agregados
    """
    df_with_metadata = df.copy()
    
    if metadata:
        for key, value in metadata.items():
            df_with_metadata[key] = value
    
    # Agregar timestamp por defecto
    if 'fecha_procesamiento' not in df_with_metadata.columns:
        df_with_metadata['fecha_procesamiento'] = pd.Timestamp.now().isoformat()
    
    logger.info(f"Metadatos agregados: {list(metadata.keys()) if metadata else ['fecha_procesamiento']}")
    return df_with_metadata


# Mantener compatibilidad con nombres anteriores
read_excel_to_dataframe = load_excel_file_to_dataframe
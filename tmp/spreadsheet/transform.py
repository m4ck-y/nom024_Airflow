import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List


def load_excel_file_to_dataframe(file_path: Path, sheet_name: Optional[str] = None, 
                                 **kwargs) -> pd.DataFrame:
    """
    Carga un archivo Excel en un DataFrame de pandas.
    
    Args:
        file_path: Ruta al archivo Excel
        sheet_name: Nombre de la hoja a leer (None para la primera hoja)
        **kwargs: Argumentos adicionales para pd.read_excel
        
    Returns:
        pd.DataFrame: DataFrame con los datos del archivo Excel
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si hay un error al leer el archivo Excel
    """
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo Excel no existe: {file_path}")
    
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
    except Exception as e:
        raise ValueError(f"Error al leer el archivo Excel {file_path}: {e}")


def clean_dataframe_columns(dataframe: pd.DataFrame, 
                           column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Limpia y normaliza las columnas de un DataFrame.
    
    Args:
        dataframe: DataFrame a limpiar
        column_mapping: Diccionario para renombrar columnas {old_name: new_name}
        
    Returns:
        pd.DataFrame: DataFrame con columnas limpias
    """
    df_cleaned = dataframe.copy()
    
    # Limpiar nombres de columnas
    df_cleaned.columns = df_cleaned.columns.str.strip().str.lower()
    
    # Renombrar columnas si se proporciona mapeo
    if column_mapping:
        df_cleaned = df_cleaned.rename(columns=column_mapping)
    
    # Eliminar filas completamente vacías
    df_cleaned = df_cleaned.dropna(how='all')
    
    return df_cleaned


def validate_required_columns(dataframe: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Valida que el DataFrame contenga las columnas requeridas.
    
    Args:
        dataframe: DataFrame a validar
        required_columns: Lista de nombres de columnas requeridas
        
    Returns:
        bool: True si todas las columnas están presentes
        
    Raises:
        ValueError: Si faltan columnas requeridas
    """
    missing_columns = set(required_columns) - set(dataframe.columns)
    
    if missing_columns:
        raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_columns}")
    
    return True


def transform_nationalities_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los datos de nacionalidades aplicando limpieza y normalización.
    
    Args:
        dataframe: DataFrame con datos de nacionalidades
        
    Returns:
        pd.DataFrame: DataFrame transformado
    """
    # Mapeo de columnas esperadas
    column_mapping = {
        'codigo pais': 'codigo_pais',
        'pais': 'pais',
        'clave nacionalidad': 'clave_nacionalidad'
    }
    
    # Limpiar DataFrame
    df_transformed = clean_dataframe_columns(dataframe, column_mapping)
    
    # Validar columnas requeridas
    required_columns = ['codigo_pais', 'pais', 'clave_nacionalidad']
    validate_required_columns(df_transformed, required_columns)
    
    # Limpiar datos específicos
    df_transformed['codigo_pais'] = df_transformed['codigo_pais'].astype(str).str.strip()
    df_transformed['pais'] = df_transformed['pais'].astype(str).str.strip().str.title()
    df_transformed['clave_nacionalidad'] = df_transformed['clave_nacionalidad'].astype(str).str.strip()
    
    # Eliminar duplicados
    df_transformed = df_transformed.drop_duplicates()
    
    return df_transformed


def prepare_data_for_database(dataframe: pd.DataFrame, add_id_column: bool = True) -> pd.DataFrame:
    """
    Prepara los datos para ser insertados en la base de datos.
    
    Args:
        dataframe: DataFrame a preparar
        add_id_column: Si True, agrega una columna de ID autoincremental
        
    Returns:
        pd.DataFrame: DataFrame preparado para la base de datos
    """
    df_prepared = dataframe.copy()
    
    if add_id_column:
        df_prepared.insert(0, 'id', range(1, len(df_prepared) + 1))
    
    return df_prepared
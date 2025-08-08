"""
EJEMPLO: Pipeline específico para procesar datos de ejemplo.

Este archivo muestra cómo crear un nuevo pipeline siguiendo el patrón establecido.
Copia este archivo y modifícalo según tus necesidades.

URL base: https://ejemplo.com/datos
"""

import logging
import pandas as pd
from datetime import datetime

from tmp.spreadsheet.pipeline import process_spreadsheet_and_save_to_database

logger = logging.getLogger(__name__)

# Configuración específica para este pipeline
EXAMPLE_BASE_URL = "https://ejemplo.com/datos"  # Cambiar por tu URL
DOWNLOAD_DIRECTORY = "tmp/"
DATABASE_PATH = "tmp/ejemplo.db"  # Cambiar por tu base de datos
TABLE_NAME = "ejemplo_datos"  # Cambiar por tu tabla

# Mapeo de columnas del archivo Excel a nombres estándar
COLUMN_MAPPING = {
    "Columna Original 1": "columna_1",
    "Columna Original 2": "columna_2", 
    "Fecha": "fecha",
    "Valor": "valor"
}


def clean_example_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y valida los datos específicos de este pipeline.
    
    Args:
        df: DataFrame con datos crudos
        
    Returns:
        DataFrame con datos limpios y validados
    """
    logger.info("Iniciando limpieza de datos de ejemplo")
    
    # Crear copia para no modificar el original
    cleaned_df = df.copy()
    
    # Eliminar filas completamente vacías
    cleaned_df = cleaned_df.dropna(how='all')
    
    # Limpiar espacios en blanco en columnas de texto
    text_columns = ['columna_1', 'columna_2']
    for col in text_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
    
    # Convertir fechas si existe la columna
    if 'fecha' in cleaned_df.columns:
        cleaned_df['fecha'] = pd.to_datetime(cleaned_df['fecha'], errors='coerce')
    
    # Convertir valores numéricos
    if 'valor' in cleaned_df.columns:
        cleaned_df['valor'] = pd.to_numeric(cleaned_df['valor'], errors='coerce')
    
    # Eliminar filas donde falten datos críticos
    critical_columns = ['columna_1']  # Definir columnas críticas
    cleaned_df = cleaned_df.dropna(subset=critical_columns)
    
    logger.info(f"Limpieza completada: {len(cleaned_df)} registros válidos")
    return cleaned_df


def validate_example_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida que los datos cumplan con los requisitos específicos.
    
    Args:
        df: DataFrame con datos a validar
        
    Returns:
        DataFrame validado
    """
    logger.info("Validando datos de ejemplo")
    
    # Verificar que existan las columnas requeridas
    required_columns = ['columna_1']  # Definir columnas requeridas
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
    
    # Verificar duplicados si es necesario
    if df.duplicated().any():
        logger.warning(f"Se encontraron {df.duplicated().sum()} registros duplicados")
        df = df.drop_duplicates()
    
    # Validaciones específicas del negocio
    if 'valor' in df.columns:
        invalid_values = df[df['valor'] < 0]  # Ejemplo: valores no pueden ser negativos
        if not invalid_values.empty:
            logger.warning(f"Se encontraron {len(invalid_values)} valores negativos")
    
    logger.info(f"Validación completada: {len(df)} registros válidos")
    return df


def add_business_logic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica lógica de negocio específica a los datos.
    
    Args:
        df: DataFrame con datos validados
        
    Returns:
        DataFrame con lógica de negocio aplicada
    """
    logger.info("Aplicando lógica de negocio")
    
    df_processed = df.copy()
    
    # Ejemplo: Categorizar valores
    if 'valor' in df_processed.columns:
        df_processed['categoria'] = pd.cut(
            df_processed['valor'], 
            bins=[0, 100, 500, float('inf')], 
            labels=['Bajo', 'Medio', 'Alto']
        )
    
    # Ejemplo: Calcular campos derivados
    if 'fecha' in df_processed.columns:
        df_processed['año'] = df_processed['fecha'].dt.year
        df_processed['mes'] = df_processed['fecha'].dt.month
    
    logger.info("Lógica de negocio aplicada")
    return df_processed


def transform_example_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas las transformaciones necesarias a los datos de ejemplo.
    
    Args:
        df: DataFrame crudo con datos
        
    Returns:
        DataFrame transformado y listo para cargar a la base de datos
    """
    logger.info("Transformando datos de ejemplo")
    
    # Aplicar limpieza
    df_cleaned = clean_example_data(df)
    
    # Aplicar validaciones
    df_validated = validate_example_data(df_cleaned)
    
    # Aplicar lógica de negocio
    df_processed = add_business_logic(df_validated)
    
    # Agregar metadatos
    df_processed['fecha_procesamiento'] = datetime.now().isoformat()
    df_processed['fuente'] = EXAMPLE_BASE_URL
    
    # Ordenar datos
    if 'columna_1' in df_processed.columns:
        df_final = df_processed.sort_values('columna_1').reset_index(drop=True)
    else:
        df_final = df_processed.reset_index(drop=True)
    
    logger.info(f"Transformación completada: {len(df_final)} registros finales")
    return df_final


def process_example_data() -> bool:
    """
    Ejecuta el pipeline completo para procesar datos de ejemplo.
    
    Este es el punto de entrada principal que:
    1. Descarga archivos desde la URL base
    2. Extrae y lee los datos
    3. Aplica transformaciones específicas
    4. Carga los datos a la base de datos
    
    Returns:
        bool: True si el proceso fue exitoso, False en caso contrario
    """
    logger.info("=== Iniciando procesamiento de datos de ejemplo ===")
    logger.info(f"URL fuente: {EXAMPLE_BASE_URL}")
    logger.info(f"Base de datos: {DATABASE_PATH}")
    logger.info(f"Tabla: {TABLE_NAME}")
    
    try:
        success = process_spreadsheet_and_save_to_database(
            page_url=EXAMPLE_BASE_URL,
            download_dir=DOWNLOAD_DIRECTORY,
            transform_data=transform_example_data,
            column_mapping=COLUMN_MAPPING,
            table_name=TABLE_NAME,
            db_path=DATABASE_PATH
        )
        
        if success:
            logger.info("=== Procesamiento de ejemplo completado exitosamente ===")
        else:
            logger.error("=== Error en el procesamiento de ejemplo ===")
            
        return success
        
    except Exception as e:
        logger.error(f"Error crítico en el procesamiento de ejemplo: {e}")
        return False


if __name__ == "__main__":
    # Configurar logging para ejecución directa
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Ejecutar pipeline
    success = process_example_data()
    exit(0 if success else 1)
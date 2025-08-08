"""
Pipeline específico para procesar datos de nacionalidades del gobierno mexicano.

Este módulo define el proceso completo para:
1. Obtener datos de nacionalidades desde la página web oficial
2. Descargar y extraer archivos
3. Transformar los datos según el formato requerido
4. Cargar los datos a la base de datos

URL base: http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html
"""

import logging
import pandas as pd
from datetime import datetime

from tmp.spreadsheet.pipeline import process_spreadsheet_and_save_to_database

logger = logging.getLogger(__name__)

# Configuración específica para nacionalidades
NATIONALITIES_BASE_URL = "http://www.dgis.salud.gob.mx/contenidos/intercambio/nacionalidades_gobmx.html"
DOWNLOAD_DIRECTORY = "tmp/"
DATABASE_PATH = "tmp/nacionalidades.db"
TABLE_NAME = "nacionalidades"

# Mapeo de columnas del archivo Excel a nombres estándar
COLUMN_MAPPING = {
    "codigo pais": "codigo_pais",
    "pais": "pais", 
    "clave nacionalidad": "clave_nacionalidad"
}


def clean_nationality_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y valida los datos de nacionalidades.
    
    Args:
        df: DataFrame con datos crudos de nacionalidades
        
    Returns:
        DataFrame con datos limpios y validados
    """
    logger.info("Iniciando limpieza de datos de nacionalidades")
    
    # Crear copia para no modificar el original
    cleaned_df = df.copy()
    
    # Eliminar filas completamente vacías
    cleaned_df = cleaned_df.dropna(how='all')
    
    # Limpiar espacios en blanco en columnas de texto
    text_columns = ['codigo_pais', 'pais', 'clave_nacionalidad']
    for col in text_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
    
    # Convertir código de país a string y rellenar con ceros si es necesario
    if 'codigo_pais' in cleaned_df.columns:
        cleaned_df['codigo_pais'] = cleaned_df['codigo_pais'].astype(str).str.zfill(3)
    
    # Eliminar filas donde falten datos críticos
    critical_columns = ['codigo_pais', 'pais']
    cleaned_df = cleaned_df.dropna(subset=critical_columns)
    
    # Agregar metadatos
    cleaned_df['fecha_procesamiento'] = datetime.now().isoformat()
    cleaned_df['fuente'] = NATIONALITIES_BASE_URL
    
    logger.info(f"Limpieza completada: {len(cleaned_df)} registros válidos")
    return cleaned_df


def validate_nationality_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida que los datos de nacionalidades cumplan con los requisitos.
    
    Args:
        df: DataFrame con datos de nacionalidades
        
    Returns:
        DataFrame validado
    """
    logger.info("Validando datos de nacionalidades")
    
    # Verificar que existan las columnas requeridas
    required_columns = ['codigo_pais', 'pais']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
    
    # Verificar que no haya códigos de país duplicados
    duplicated_codes = df[df['codigo_pais'].duplicated()]
    if not duplicated_codes.empty:
        logger.warning(f"Se encontraron {len(duplicated_codes)} códigos de país duplicados")
        # Mantener solo la primera ocurrencia
        df = df.drop_duplicates(subset=['codigo_pais'], keep='first')
    
    # Verificar rangos válidos para código de país (asumiendo códigos ISO)
    invalid_codes = df[~df['codigo_pais'].str.match(r'^\d{3}$')]
    if not invalid_codes.empty:
        logger.warning(f"Se encontraron {len(invalid_codes)} códigos de país inválidos")
    
    logger.info(f"Validación completada: {len(df)} registros válidos")
    return df


def transform_nationalities_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas las transformaciones necesarias a los datos de nacionalidades.
    
    Args:
        df: DataFrame crudo con datos de nacionalidades
        
    Returns:
        DataFrame transformado y listo para cargar a la base de datos
    """
    logger.info("Transformando datos de nacionalidades")
    
    # Aplicar limpieza
    df_cleaned = clean_nationality_data(df)
    
    # Aplicar validaciones
    df_validated = validate_nationality_data(df_cleaned)
    
    # Ordenar por código de país
    df_final = df_validated.sort_values('codigo_pais').reset_index(drop=True)
    
    logger.info(f"Transformación completada: {len(df_final)} registros finales")
    return df_final


def process_nationalities_data() -> bool:
    """
    Ejecuta el pipeline completo para procesar datos de nacionalidades.
    
    Este es el punto de entrada principal que:
    1. Descarga archivos desde la URL base
    2. Extrae y lee los datos
    3. Aplica transformaciones específicas
    4. Carga los datos a la base de datos
    
    Returns:
        bool: True si el proceso fue exitoso, False en caso contrario
    """
    logger.info("=== Iniciando procesamiento de datos de nacionalidades ===")
    logger.info(f"URL fuente: {NATIONALITIES_BASE_URL}")
    logger.info(f"Base de datos: {DATABASE_PATH}")
    logger.info(f"Tabla: {TABLE_NAME}")
    
    try:
        success = process_spreadsheet_and_save_to_database(
            page_url=NATIONALITIES_BASE_URL,
            download_dir=DOWNLOAD_DIRECTORY,
            transform_data=transform_nationalities_data,
            column_mapping=COLUMN_MAPPING,
            table_name=TABLE_NAME,
            db_path=DATABASE_PATH
        )
        
        if success:
            logger.info("=== Procesamiento de nacionalidades completado exitosamente ===")
        else:
            logger.error("=== Error en el procesamiento de nacionalidades ===")
            
        return success
        
    except Exception as e:
        logger.error(f"Error crítico en el procesamiento de nacionalidades: {e}")
        return False


if __name__ == "__main__":
    # Configurar logging para ejecución directa
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Ejecutar pipeline
    success = process_nationalities_data()
    exit(0 if success else 1)
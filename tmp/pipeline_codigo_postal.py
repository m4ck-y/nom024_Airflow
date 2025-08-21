import pandas as pd
import logging

# ---------------------------
# Configuración de logging
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------
# Configuraciones
# ---------------------------
EXCEL_PATH = "CODIGO_POSTAL_20250814.xls"              # Ruta del archivo Excel fuente
OUTPUT_PARQUET_PATH = "codigos_postales_mx.parquet"    # Ruta de salida del archivo .parquet
SKIP_SHEETS = 1                                         # Número de hojas a omitir desde el inicio (p. ej. hoja "Notas")
EXPECTED_COLUMNS = None                                 # Se definirá con las columnas de la primera hoja válida

# Definición de longitudes esperadas por campo (clave para limpieza/padding)
COLUMN_LENGTHS = {
    "d_codigo": 5,
    "d_cp": 5,
    "c_tipo_asenta": 2,
    "c_estado": 2,
    "c_oficina": 5,
    "c_mnpio": 3,
    "id_asenta_cpcons": 4,
    "c_cve_ciudad": 2,
    "c_cp": 5,
}


# ---------------------------
# Función para cargar hojas de Excel
# ---------------------------
def load_excel_sheets(file_path: str) -> tuple[pd.ExcelFile, list]:
    logger.info(f"Leyendo archivo: {file_path}")
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        logger.error(f"No se pudo leer el archivo Excel: {e}")
        raise

    sheet_names = xls.sheet_names
    logger.info(f"Se encontraron {len(sheet_names)} hojas:")
    for i, sheet in enumerate(sheet_names):
        logger.info(f"{i + 1}. {sheet}")
    return xls, sheet_names


# ---------------------------
# Función para procesar y combinar hojas válidas
# ---------------------------
def process_sheets(xls: pd.ExcelFile, sheet_names: list, skip: int = 1) -> pd.DataFrame:
    global EXPECTED_COLUMNS
    dataframes = []

    for i, sheet_name in enumerate(sheet_names):
        if i < skip:
            # Saltar hojas iniciales no relevantes (como "Notas")
            logger.info(f"Omitiendo hoja '{sheet_name}'")
            continue

        logger.info(f"Procesando hoja: {sheet_name}")
        df = xls.parse(sheet_name)

        # Eliminar filas totalmente vacías
        df = df.dropna(how='all')

        # Mostrar columnas presentes en esta hoja
        logger.info(f"Columnas en hoja '{sheet_name}': {list(df.columns)}")

        # Verificación de consistencia en columnas
        if EXPECTED_COLUMNS is None:
            EXPECTED_COLUMNS = list(df.columns)  # Definir columnas base
            logger.info(f"Columnas esperadas definidas a partir de '{sheet_name}': {EXPECTED_COLUMNS}")
        elif list(df.columns) != EXPECTED_COLUMNS:
            raise ValueError(f"Las columnas de la hoja '{sheet_name}' no coinciden con las esperadas.")

        logger.info(f"{len(df)} registros encontrados en hoja '{sheet_name}'")
        dataframes.append(df)

    # Concatenar todas las hojas en un solo DataFrame
    full_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Total de registros combinados: {len(full_df)}")
    return full_df


# ---------------------------
# Función para validar y rellenar ceros en columnas numéricas
# ---------------------------
def validate_and_pad_column(df: pd.DataFrame, col_name: str, length: int) -> pd.DataFrame:
    if col_name not in df.columns:
        logger.warning(f"Columna '{col_name}' no encontrada en DataFrame.")
        return df

    not_null_mask = df[col_name].notna()
    df[col_name] = df[col_name].astype(object)  # Convertir a tipo genérico

    # Rellenar con ceros a la izquierda según longitud esperada
    df.loc[not_null_mask, col_name] = (
        df.loc[not_null_mask, col_name].astype(str).str.strip().str.zfill(length)
    )

    # Detectar valores que exceden la longitud esperada
    mask_exceed = df.loc[not_null_mask, col_name].str.len() > length
    if mask_exceed.any():
        count_exceed = mask_exceed.sum()
        logger.warning(
            f"La columna '{col_name}' tiene {count_exceed} registros que exceden la longitud esperada de {length} caracteres."
        )
        logger.warning(f"Ejemplos: {df.loc[not_null_mask, col_name][mask_exceed].head().tolist()}")

    return df


# ---------------------------
# Función de limpieza y normalización
# ---------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando limpieza de datos...")

    logger.info("Tipos de datos originales:")
    logger.info(df.dtypes)

    # Limpiar espacios en columnas de texto
    for col in df.select_dtypes(include='object').columns:
        not_null_mask = df[col].notna()
        df.loc[not_null_mask, col] = df.loc[not_null_mask, col].astype(str).str.strip()

    # Normalizar nombres de columnas (snake_case)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Conversión específica: 'c_cve_ciudad' a string con zfill(2)
    if 'c_cve_ciudad' in df.columns:
        logger.info("Convirtiendo 'c_cve_ciudad' de float a string con zfill(2)...")
        not_null_mask = df['c_cve_ciudad'].notna()

        # Primero convierte la columna completa a tipo objeto (más flexible)
        df['c_cve_ciudad'] = df['c_cve_ciudad'].astype('object')

        # Luego convierte solo los no nulos a entero y string con relleno
        df.loc[not_null_mask, 'c_cve_ciudad'] = (
            df.loc[not_null_mask, 'c_cve_ciudad']
            .astype('Int64')
            .astype(str)
            .str.zfill(2)
        )
        
        # Finalmente, si quieres que la columna tenga dtype "string" de pandas:
        df['c_cve_ciudad'] = df['c_cve_ciudad'].astype('string')
        logger.info(f"Ejemplos después de conversión: {df['c_cve_ciudad'].dropna().unique()[:5].tolist()}")

    # Validar y aplicar relleno a columnas definidas
    for col, length in COLUMN_LENGTHS.items():
        df = validate_and_pad_column(df, col, length)

    # Eliminar duplicados
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info(f"Duplicados eliminados: {before - after}")

    logger.info("Tipos de datos después de limpieza:")
    logger.info(df.dtypes)

    return df


# ---------------------------
# Guardar DataFrame limpio a archivo .parquet
# ---------------------------
def save_to_parquet(df: pd.DataFrame, output_path: str):
    logger.info(f"Guardando DataFrame en formato .parquet: {output_path}")
    df.to_parquet(output_path, index=False)
    logger.info("Archivo guardado exitosamente.")


# ---------------------------
# Leer y mostrar inspección básica del archivo .parquet
# ---------------------------
def read_and_inspect_parquet(parquet_path: str):
    logger.info(f"Lectura del archivo parquet: {parquet_path}")
    df = pd.read_parquet(parquet_path)

    logger.info("Tipos de datos cargados desde el parquet:")
    logger.info(df.dtypes)

    # Revisar si hay valores nulos
    cols_with_nulls = df.columns[df.isnull().any()].tolist()
    if cols_with_nulls:
        logger.info(f"Columnas con valores nulos: {cols_with_nulls}")
    else:
        logger.info("No se detectaron valores nulos en ninguna columna.")

    # Mostrar ejemplos
    logger.info("Primeros 5 registros:")
    logger.info(df.head(5).to_string(index=False))

    logger.info("Últimos 5 registros:")
    logger.info(df.tail(5).to_string(index=False))


# ---------------------------
# Ejecución completa del pipeline
# ---------------------------
def run_pipeline():
    xls, sheet_names = load_excel_sheets(EXCEL_PATH)          # Leer hojas del Excel
    combined_df = process_sheets(xls, sheet_names, skip=SKIP_SHEETS)  # Unir hojas válidas
    cleaned_df = clean_data(combined_df)                      # Limpiar y preparar datos
    save_to_parquet(cleaned_df, OUTPUT_PARQUET_PATH)          # Guardar como parquet
    read_and_inspect_parquet(OUTPUT_PARQUET_PATH)             # Verificar archivo resultante


# ---------------------------
# Punto de entrada principal
# ---------------------------
if __name__ == "__main__":
    run_pipeline()

# Pipeline Architecture - Filosofía y Diseño

## 🎯 Filosofía del Sistema

Este sistema implementa **pipelines declarativos modulares** para procesamiento de datos web. La filosofía central es:

> **"Cada pipeline específico debe ser autocontenido y declarativo - al leer el código, debe ser obvio QUÉ hace, no CÓMO lo hace"**

### Principios de Diseño

1. **Declarativo sobre Imperativo**: Los nombres de funciones describen la intención, no la implementación
2. **Separación de Responsabilidades**: Pipeline general vs. lógica específica de dominio
3. **Composición sobre Herencia**: Funciones pequeñas que se combinan para crear flujos complejos
4. **Configuración Explícita**: Cada pipeline define claramente sus parámetros y transformaciones

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE ESPECÍFICO                      │
│  (nacionalidades.py, otro_pipeline.py, etc.)               │
│                                                             │
│  • URL base específica                                      │
│  • Transformaciones de dominio                              │
│  • Mapeo de columnas                                        │
│  • Validaciones de negocio                                  │
│  • Configuración de BD                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 PIPELINE GENERAL                            │
│              (spreadsheet/pipeline.py)                     │
│                                                             │
│  • Flujo estándar reutilizable                             │
│  • Orquestación de pasos                                   │
│  • Manejo de errores                                       │
│  • Limpieza de recursos                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                MÓDULOS UTILITARIOS                          │
│   (html.py, downloader.py, zip.py, etc.)                  │
│                                                             │
│  • Funciones atómicas reutilizables                        │
│  • Sin lógica de negocio                                   │
│  • Enfoque en una sola responsabilidad                     │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Flujo de Ejecución

### 1. Pipeline Específico (ej: nacionalidades.py)

```python
def process_nationalities_data() -> bool:
    """Punto de entrada principal - orquesta todo el proceso"""
    
    return process_spreadsheet_and_save_to_database(
        page_url=NATIONALITIES_BASE_URL,
        download_dir=DOWNLOAD_DIRECTORY,
        transform_data=transform_nationalities_data,  # ← Lógica específica
        column_mapping=COLUMN_MAPPING,               # ← Configuración específica
        table_name=TABLE_NAME,
        db_path=DATABASE_PATH
    )
```

**Responsabilidades del Pipeline Específico:**
- Definir configuración del dominio
- Implementar transformaciones específicas
- Establecer reglas de validación
- Configurar destino de datos

### 2. Pipeline General (spreadsheet/pipeline.py)

```python
def process_spreadsheet_and_save_to_database(...) -> bool:
    """Flujo estándar reutilizable para cualquier fuente de datos"""
    
    # 1. Descubrimiento
    spreadsheet_links = find_spreadsheet_links(page_url)
    if not spreadsheet_links:
        return False
    
    # 2. Adquisición
    excel_path = download_and_extract_spreadsheet(file_url, download_dir)
    if not excel_path:
        return False
    
    # 3. Ingesta
    df = load_excel_file_to_dataframe(excel_path)
    
    # 4. Mapeo
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # 5. Transformación (específica del dominio)
    df_transformed = transform_data(df)  # ← Función inyectada
    
    # 6. Persistencia
    save_dataframe_to_sqlite(df_transformed, db_path, table_name)
    
    # 7. Limpieza
    cleanup_temporary_files(excel_path)
    
    return True
```

**Responsabilidades del Pipeline General:**
- Orquestar el flujo estándar
- Manejar errores y logging
- Gestionar recursos temporales
- Proporcionar puntos de extensión

### 3. Transformaciones Específicas

```python
def transform_nationalities_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas las transformaciones del dominio"""
    
    # Limpieza específica del dominio
    df_cleaned = clean_nationality_data(df)
    
    # Validaciones de negocio
    df_validated = validate_nationality_data(df_cleaned)
    
    # Enriquecimiento
    df_final = add_metadata_and_sort(df_validated)
    
    return df_final
```

## 🔧 Módulos Utilitarios

Cada módulo tiene una **responsabilidad única** y **nombres declarativos**:

### html.py - Extracción Web
```python
extract_html_elements_by_tag(url, tag)     # Extrae elementos HTML
get_element_attribute_value(element, attr)  # Obtiene valores de atributos
```

### downloader.py - Adquisición de Archivos
```python
download_file_from_url(url, directory)     # Descarga archivos
```

### zip.py - Manejo de Archivos Comprimidos
```python
extract_spreadsheet_from_zip(zip_path, extract_to)  # Extrae hojas de cálculo
```

### database_loader.py - Persistencia
```python
save_dataframe_to_sqlite(df, db_path, table_name)   # Guarda en SQLite
```

### transform.py - Transformaciones Genéricas
```python
load_excel_file_to_dataframe(file_path)    # Carga Excel a DataFrame
clean_dataframe_columns(df)                # Limpia nombres de columnas
validate_required_columns(df, columns)     # Valida columnas requeridas
```

## 🎨 Patrones de Diseño Implementados

### 1. Template Method Pattern
El pipeline general define el esqueleto del algoritmo, los pipelines específicos implementan los pasos variables.

### 2. Strategy Pattern
Las transformaciones específicas se inyectan como estrategias al pipeline general.

### 3. Builder Pattern
Cada pipeline específico construye su configuración paso a paso.

### 4. Single Responsibility Principle
Cada función tiene una sola razón para cambiar.

## 📝 Convenciones de Nomenclatura

### Funciones Principales (Verbos de Acción)
- `process_*_data()` - Ejecuta pipeline completo
- `transform_*_data()` - Aplica transformaciones específicas
- `clean_*_data()` - Limpia datos específicos
- `validate_*_data()` - Valida datos específicos

### Funciones Utilitarias (Verbos Descriptivos)
- `find_*()` - Busca y retorna elementos
- `extract_*()` - Extrae información
- `download_*()` - Descarga recursos
- `save_*()` - Persiste datos
- `load_*()` - Carga datos

### Configuración (Sustantivos en Mayúsculas)
- `*_BASE_URL` - URL fuente de datos
- `*_DIRECTORY` - Directorios de trabajo
- `COLUMN_MAPPING` - Mapeo de columnas
- `TABLE_NAME` - Nombre de tabla destino

## 🚀 Cómo Crear un Nuevo Pipeline

### Paso 1: Definir Configuración
```python
# Configuración específica del dominio
MY_DATA_BASE_URL = "https://source.com/data"
DOWNLOAD_DIRECTORY = "tmp/"
DATABASE_PATH = "tmp/my_data.db"
TABLE_NAME = "my_table"

COLUMN_MAPPING = {
    "Original Column": "standard_column"
}
```

### Paso 2: Implementar Transformaciones
```python
def transform_my_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transformaciones específicas del dominio"""
    
    df_cleaned = clean_my_specific_data(df)
    df_validated = validate_my_business_rules(df_cleaned)
    df_enriched = add_my_metadata(df_validated)
    
    return df_enriched
```

### Paso 3: Crear Función Principal
```python
def process_my_data() -> bool:
    """Punto de entrada del pipeline"""
    
    return process_spreadsheet_and_save_to_database(
        page_url=MY_DATA_BASE_URL,
        download_dir=DOWNLOAD_DIRECTORY,
        transform_data=transform_my_data,
        column_mapping=COLUMN_MAPPING,
        table_name=TABLE_NAME,
        db_path=DATABASE_PATH
    )
```

## 🎯 Beneficios de esta Arquitectura

### Para Desarrolladores
- **Legibilidad**: El código se lee como documentación
- **Mantenibilidad**: Cambios localizados en módulos específicos
- **Testabilidad**: Funciones pequeñas y enfocadas
- **Reutilización**: Pipeline general sirve múltiples casos de uso

### Para el Sistema
- **Escalabilidad**: Fácil agregar nuevos pipelines
- **Robustez**: Manejo centralizado de errores
- **Eficiencia**: Reutilización de componentes comunes
- **Observabilidad**: Logging consistente en todos los niveles

### Para IAs/Otros Desarrolladores
- **Comprensión Rápida**: Estructura predecible y consistente
- **Extensión Sencilla**: Patrones claros para seguir
- **Documentación Implícita**: El código es autodocumentado
- **Separación Clara**: Responsabilidades bien definidas

## 🔍 Ejemplo de Lectura de Código

Al ver `nacionalidades.py`, un desarrollador entiende inmediatamente:

1. **QUÉ hace**: `process_nationalities_data()` - procesa datos de nacionalidades
2. **DE DÓNDE**: `NATIONALITIES_BASE_URL` - fuente específica
3. **CÓMO transforma**: `transform_nationalities_data()` - lógica específica
4. **DÓNDE guarda**: `DATABASE_PATH` y `TABLE_NAME` - destino específico

Sin necesidad de leer implementaciones internas, el flujo y propósito son evidentes.

---

> **Filosofía clave**: "Un pipeline bien diseñado cuenta su historia a través de sus nombres de funciones y estructura, no a través de comentarios o documentación externa."
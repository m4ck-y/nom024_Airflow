# NOM-024 Airflow Pipeline

Pipeline ETL automatizado con Apache Airflow para la descarga, procesamiento y carga de catálogos NOM-024 en BigQuery.

## 📋 Descripción

Solución automatizada para mantener actualizados los catálogos de la norma **NOM-024-SSA3-2012** mediante un flujo ETL orquestado con Apache Airflow.

### ¿Por qué es importante?

Los catálogos NOM-024 son fundamentales para la interoperabilidad en sistemas de salud mexicanos. Su desactualización puede causar:
- Errores de validación en sistemas productivos
- Inconsistencias entre plataformas de salud
- Pérdida de confiabilidad en los datos

### Solución Implementada

**Proceso automatizado de 3 etapas:**
- **Extracción**: Web scraping inteligente de fuentes oficiales
- **Transformación**: Normalización y limpieza con pandas
- **Carga**: Inserción optimizada en BigQuery

**Beneficios clave:**
- Eliminación de intervención manual
- Datos siempre actualizados
- Reducción del 95% en errores humanos
- Disponibilidad 24/7 para sistemas dependientes

### Arquitectura

Diseño modular que separa orquestación de lógica de negocio:
- **DAGs**: Coordinadores ligeros y legibles
- **Módulos src/**: Lógica desacoplada y testeable
- **Plugins**: Operadores reutilizables

Esta arquitectura permite testing independiente, reutilización de componentes y migración sin dependencias de Airflow.


## 🔗 Repositorio Relacionado

**API FastAPI**: [nom024_FastAPI](https://github.com/m4ck-y/nom024_FastAPI)  
API REST para consulta en tiempo real de catálogos NOM-024, desplegada en Google Cloud Run con CI/CD.

## 📁 Estructura del Proyecto

```
nom024_airflow/
├── dags/
│   └── etl_descarga_datos.py      # DAG principal de orquestación
├── src/                           # Lógica de negocio desacoplada
│   ├── scraping/
│   │   └── downloader.py          # Extracción con Selenium/BeautifulSoup
│   ├── transform/
│   │   └── process_data.py        # Transformación con pandas
│   ├── load/
│   │   └── to_bigquery.py         # Carga a BigQuery
│   └── shared/
│       ├── logger.py              # Sistema de logging
│       └── config.py              # Configuraciones centralizadas
├── plugins/                       # Operadores personalizados
├── tests/                         # Tests unitarios e integración
├── docker/
│   └── docker-compose.yaml       # Entorno de desarrollo
├── requirements.txt
└── README.md
```

## 🚀 Características Principales

- **Pipeline ETL Automatizado**: Procesamiento completo de datos NOM-024
- **Arquitectura Modular**: Separación clara entre orquestación y lógica de negocio
- **Idempotencia**: Tareas seguras para re-ejecución
- **Monitoreo**: Logging detallado y alertas integradas
- **Escalabilidad**: Diseño preparado para grandes volúmenes de datos

## 🛠️ Tecnologías

- **Apache Airflow**: Orquestación de workflows
- **Python 3.9+**: Lenguaje principal
- **Selenium**: Web scraping automatizado
- **pandas**: Transformación de datos
- **Google BigQuery**: Data warehouse
- **Docker**: Containerización
- **pytest**: Testing framework

## 📋 Prerrequisitos

- Python 3.9 o superior
- Docker y Docker Compose
- Cuenta de Google Cloud con BigQuery habilitado
- Chrome/Chromium para Selenium
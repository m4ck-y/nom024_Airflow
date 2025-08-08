"""
Punto de entrada principal para ejecutar diferentes pipelines de datos.

Este archivo orquesta la ejecución de diferentes pipelines específicos,
cada uno definido en su propio módulo.
"""

import logging
from tmp.nacionalidades import process_nationalities_data

# Configurar logging global
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_all_pipelines():
    """Ejecuta todos los pipelines disponibles."""
    logger.info("=== Iniciando ejecución de todos los pipelines ===")
    
    pipelines = [
        ("Nacionalidades", process_nationalities_data),
        # Aquí se pueden agregar más pipelines en el futuro
        # ("Otro Pipeline", process_other_data),
    ]
    
    results = {}
    
    for pipeline_name, pipeline_function in pipelines:
        logger.info(f"Ejecutando pipeline: {pipeline_name}")
        try:
            success = pipeline_function()
            results[pipeline_name] = success
            status = "✓ EXITOSO" if success else "✗ FALLÓ"
            logger.info(f"Pipeline {pipeline_name}: {status}")
        except Exception as e:
            results[pipeline_name] = False
            logger.error(f"Error en pipeline {pipeline_name}: {e}")
    
    # Resumen final
    logger.info("=== Resumen de ejecución ===")
    for pipeline_name, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"{status} {pipeline_name}")
    
    successful_pipelines = sum(results.values())
    total_pipelines = len(results)
    logger.info(f"Pipelines exitosos: {successful_pipelines}/{total_pipelines}")
    
    return all(results.values())


if __name__ == "__main__":
    # Ejecutar solo el pipeline de nacionalidades por defecto
    logger.info("Ejecutando pipeline de nacionalidades...")
    success = process_nationalities_data()
    
    if success:
        logger.info("Pipeline ejecutado exitosamente")
    else:
        logger.error("Error en la ejecución del pipeline")
    
    exit(0 if success else 1)
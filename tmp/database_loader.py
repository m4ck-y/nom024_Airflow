import pandas as pd
import sqlite3
from pathlib import Path
from typing import Literal


def save_dataframe_to_sqlite(
    dataframe: pd.DataFrame, 
    database_path: Path = Path("tmp/data.db"), 
    table_name: str = "datos",
    if_exists: Literal["fail", "replace", "append"] = "append"
) -> None:
    """
    Guarda un DataFrame en una base de datos SQLite.
    
    Args:
        dataframe: DataFrame de pandas a guardar
        database_path: Ruta al archivo de base de datos SQLite
        table_name: Nombre de la tabla donde guardar los datos
        if_exists: Comportamiento si la tabla ya existe ('fail', 'replace', 'append')
        
    Raises:
        sqlite3.Error: Si hay un error al conectar o escribir a la base de datos
        ValueError: Si el DataFrame está vacío
    """
    if dataframe.empty:
        raise ValueError("El DataFrame está vacío, no se puede guardar")
    
    # Crear directorio padre si no existe
    database_path.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(database_path) as conn:
        dataframe.to_sql(table_name, conn, if_exists=if_exists, index=False)

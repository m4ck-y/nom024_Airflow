import pandas as pd
import sqlite3

def load_dataframe_to_db(df: pd.DataFrame, db_path: str = "tmp/data.db", table_name: str = "datos"):
    """
    Carga un DataFrame a una base de datos SQLite.
    """
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="append", index=False)

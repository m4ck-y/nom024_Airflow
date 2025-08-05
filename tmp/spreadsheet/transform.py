import pandas as pd

def read_excel_to_dataframe(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)


def transform_and_load_nationalities(df: pd.DataFrame):
    pass
    """ with Session() as db:
        db.query(Table).delete()
        for index, row in df.iterrows():
            nationality = E(
                id=index + 1,
                codigo_pais=str(row["codigo pais"]),
                pais=row["pais"],
                clave_nacionalidad=row["clave nacionalidad"]
            )
            db.add(Table(**nationality.model_dump()))
        db.commit() """
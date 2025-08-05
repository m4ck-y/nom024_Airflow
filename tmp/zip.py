import zipfile
import os
from typing import Optional

def extract_first_spreadsheet(zip_path: str, extract_to: str) -> Optional[str]:
    """
    Extrae el primer archivo .xls o .xlsx de un archivo ZIP.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.endswith('.xlsx') or name.endswith('.xls'):
                zip_ref.extract(name, extract_to)
                return os.path.join(extract_to, name)
    return None

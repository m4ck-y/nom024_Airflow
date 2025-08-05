from urllib.parse import urljoin

def resolve_url(base_url: str, relative_url: str) -> str:
    """
    Resuelve una URL relativa a una absoluta.
    """
    return urljoin(base_url, relative_url)

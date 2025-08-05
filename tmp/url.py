from urllib.parse import urljoin, urlparse
from typing import Optional


def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """
    Resuelve una URL relativa convirtiéndola en una URL absoluta.
    
    Args:
        base_url: URL base para resolver la URL relativa
        relative_url: URL relativa a resolver
        
    Returns:
        str: URL absoluta resultante
        
    Example:
        >>> resolve_relative_url("https://example.com/page", "../file.pdf")
        "https://example.com/file.pdf"
    """
    return urljoin(base_url, relative_url)


def is_valid_url(url: str) -> bool:
    """
    Verifica si una URL tiene un formato válido.
    
    Args:
        url: URL a validar
        
    Returns:
        bool: True si la URL es válida, False en caso contrario
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_filename_from_url(url: str) -> Optional[str]:
    """
    Extrae el nombre del archivo de una URL.
    
    Args:
        url: URL de la cual extraer el nombre del archivo
        
    Returns:
        Optional[str]: Nombre del archivo o None si no se puede determinar
        
    Example:
        >>> extract_filename_from_url("https://example.com/files/document.pdf")
        "document.pdf"
    """
    try:
        parsed_url = urlparse(url)
        filename = parsed_url.path.split('/')[-1]
        return filename if filename else None
    except Exception:
        return None

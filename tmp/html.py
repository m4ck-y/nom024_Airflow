import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Union


def extract_html_elements_by_tag(url: str, tag: str, **kwargs) -> List[BeautifulSoup]:
    """
    Extrae elementos HTML con la etiqueta especificada desde una URL.
    
    Args:
        url: URL de la página web a analizar
        tag: Etiqueta HTML a buscar (ej: 'a', 'div', 'span')
        **kwargs: Argumentos adicionales para find_all (class_, id, etc.)
        
    Returns:
        List[BeautifulSoup]: Lista de elementos HTML encontrados
        
    Raises:
        requests.RequestException: Si hay un error al acceder a la URL
        Exception: Si hay un error al parsear el HTML
    """
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all(tag, **kwargs)


def get_element_attribute_value(element: BeautifulSoup, attribute: str) -> Optional[str]:
    """
    Obtiene el valor de un atributo específico de un elemento HTML.
    
    Args:
        element: Elemento HTML de BeautifulSoup
        attribute: Nombre del atributo a obtener
        
    Returns:
        Optional[str]: Valor del atributo o None si no existe
    """
    return element.get(attribute)


def extract_links_from_page(url: str, filter_extension: Optional[str] = None) -> List[str]:
    """
    Extrae todos los enlaces de una página web.
    
    Args:
        url: URL de la página web
        filter_extension: Filtrar enlaces por extensión (ej: '.pdf', '.xlsx')
        
    Returns:
        List[str]: Lista de URLs encontradas
    """
    links = []
    anchor_elements = extract_html_elements_by_tag(url, "a")
    
    for anchor in anchor_elements:
        href = get_element_attribute_value(anchor, "href")
        if href:
            if filter_extension is None or href.lower().endswith(filter_extension.lower()):
                links.append(href)
    
    return links

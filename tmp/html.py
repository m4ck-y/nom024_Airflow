import requests
from bs4 import BeautifulSoup

def get_html_elements(url: str, tag: str):
    """
    Devuelve una lista de elementos HTML con la etiqueta especificada desde una URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all(tag)

def get_element_attribute(element, attribute: str):
    return element.get(attribute)

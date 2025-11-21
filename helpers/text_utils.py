"""
Utilidades para procesamiento de texto y generación de snippets.
"""
import re
from typing import List, Dict, Optional


def generar_snippet(texto: str, query: str, max_length: int = 200) -> str:
    """
    Genera un snippet del texto mostrando el contexto donde aparece la query.
    
    Args:
        texto: Texto completo del documento
        query: Palabra o frase buscada
        max_length: Longitud máxima del snippet
        
    Returns:
        Snippet con contexto alrededor de la palabra buscada
    """
    if not texto or not query:
        return ""
    
    # Buscar la primera ocurrencia (case insensitive)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(texto)
    
    if not match:
        # Si no encuentra, retornar inicio del texto
        return texto[:max_length] + "..." if len(texto) > max_length else texto
    
    # Posición donde aparece la palabra
    start_pos = match.start()
    end_pos = match.end()
    
    # Calcular contexto antes y después
    context_before = max_length // 2
    context_after = max_length // 2
    
    # Ajustar inicio del snippet
    snippet_start = max(0, start_pos - context_before)
    snippet_end = min(len(texto), end_pos + context_after)
    
    # Extraer snippet
    snippet = texto[snippet_start:snippet_end]
    
    # Agregar "..." si no empieza/termina en el inicio/fin del texto
    if snippet_start > 0:
        snippet = "..." + snippet
    if snippet_end < len(texto):
        snippet = snippet + "..."
    
    return snippet.strip()


def resaltar_texto(texto: str, query: str) -> str:
    """
    Resalta todas las ocurrencias de la query en el texto con marcadores HTML.
    
    Args:
        texto: Texto donde resaltar
        query: Palabra a resaltar
        
    Returns:
        Texto con marcadores <mark> alrededor de las coincidencias
    """
    if not texto or not query:
        return texto
    
    # Reemplazar todas las ocurrencias (case insensitive) con marcadores
    pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
    return pattern.sub(r'<mark>\1</mark>', texto)


def generar_snippets_multiples(texto: str, query: str, max_snippets: int = 3, max_length: int = 150) -> List[str]:
    """
    Genera múltiples snippets si la palabra aparece varias veces en el texto.
    
    Args:
        texto: Texto completo
        query: Palabra buscada
        max_snippets: Número máximo de snippets a generar
        max_length: Longitud de cada snippet
        
    Returns:
        Lista de snippets con contexto
    """
    if not texto or not query:
        return []
    
    snippets = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    matches = list(pattern.finditer(texto))
    
    if not matches:
        # Si no hay coincidencias, retornar inicio del texto
        preview = texto[:max_length] + "..." if len(texto) > max_length else texto
        return [preview]
    
    # Tomar las primeras N ocurrencias
    for match in matches[:max_snippets]:
        start_pos = match.start()
        end_pos = match.end()
        
        context = max_length // 2
        snippet_start = max(0, start_pos - context)
        snippet_end = min(len(texto), end_pos + context)
        
        snippet = texto[snippet_start:snippet_end]
        
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(texto):
            snippet = snippet + "..."
        
        snippets.append(snippet.strip())
    
    return snippets


def limpiar_texto(texto: str) -> str:
    """
    Limpia el texto eliminando caracteres especiales y espacios múltiples.
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    if not texto:
        return ""
    
    # Eliminar saltos de línea múltiples
    texto = re.sub(r'\n+', ' ', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()


def truncar_texto(texto: str, max_length: int = 500, sufijo: str = "...") -> str:
    """
    Trunca el texto a una longitud máxima.
    
    Args:
        texto: Texto a truncar
        max_length: Longitud máxima
        sufijo: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if not texto or len(texto) <= max_length:
        return texto
    
    return texto[:max_length].rsplit(' ', 1)[0] + sufijo

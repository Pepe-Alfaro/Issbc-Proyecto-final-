import requests
import re

class WebSearchService:
    def buscar_info_web(self, query):
        """
        Realiza una búsqueda básica en la web usando DuckDuckGo (HTML)
        para obtener un poco más de contexto sobre un repositorio o tecnología.
        """
        print(f"🌐 Buscando en la web: {query}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            
            # Extraer los snippets usando una expresión regular
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.IGNORECASE | re.DOTALL)
            
            # Limpiar tags HTML (como <b>, </b>, etc)
            clean_snippets = []
            for s in snippets:
                # Reemplazar tags con espacio y quitar espacios extra
                texto_limpio = re.sub(r'<[^>]+>', '', s).strip()
                if texto_limpio:
                    clean_snippets.append(texto_limpio)
            
            if clean_snippets:
                return "\n".join(f"- {s}" for s in clean_snippets[:3])
            return "No se encontraron resultados o el repositorio es muy específico."
            
        except Exception as e:
            print(f"Error en WebSearchService: {e}")
            return "Error al realizar la búsqueda web."

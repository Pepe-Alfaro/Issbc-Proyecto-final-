# services/ollama_service.py
import ollama
import re

class OllamaService:
    def obtener_modelos_disponibles(self):
        """Devuelve una lista de los nombres de modelos locales de Ollama"""
        try:
            modelos_raw = ollama.list()
            return [m['model'] for m in modelos_raw.get('models', [])]
        except Exception as e:
            print(f"Error obteniendo modelos Ollama: {e}")
            return []

    def analizar_con_ollama(self, texto, contexto_pdfs="", modelo="phi3:mini"):
        """Usa Ollama para hacer un análisis cualitativo del texto"""
        prompt = f"""
        Actúa como un experto en diagnóstico de repositorios. 
        Analiza esta descripción o contexto de un repositorio de GitHub: '{texto}'.
        """
        if contexto_pdfs:
            prompt += f"\n\nTen en cuenta el siguiente CONTEXTO EXTRAÍDO DE MANUALES O README:\n{contexto_pdfs[:2000]}"
            
        prompt += """
        \nIndica brevemente si parece un proyecto serio, si hay indicios de falta de cohesión o si es inestable.
        ESPECIAL ATENCIÓN: Diferencia entre un repositorio 'Estable' (pocos cambios porque ya funciona bien) y uno 'Legacy/Obsoleto'. Si el contexto (README) indica 'maintenance mode', 'deprecated' o 'no longer supported', márcalo explícitamente como obsoleto.
        Sé directo y profesional. Responde en español.
        """
        print("🤖 Consultando a Ollama...")
        try:
            respuesta = ollama.chat(model=modelo, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return respuesta['message']['content']
        except Exception as e:
            return f"Error conectando con la IA local: {e}"

    def analizar_sentimiento(self, comentarios, modelo="phi3:mini"):
        """Evalúa el nivel de toxicidad y el estancamiento (inercia de mantenimiento)"""
        if not comentarios:
            return {"toxicidad": 1, "estancado": False}
            
        comentarios_str = "\n---\n".join(comentarios)
        prompt = f"""
        Analiza los siguientes comentarios extraídos de Issues de un repositorio.
        Necesito que extraigas dos métricas basándote estrictamente en las reglas.

        INSTRUCCIONES CRÍTICAS:
        1. "toxicidad": Del 1 al 10.
           - IGNORA explícitamente palabras de frustración técnica como "error", "bug", "broken", "bad" o "sucks".
           - SOLO marca toxicidad (puntuación > 6) si hay insultos directos o ataques personales.
        2. "estancado": true o false.
           - Si los usuarios preguntan por fechas de lanzamiento, nuevas versiones, o se quejan de que sus PRs no son revisadas o el proyecto parece abandonado, marca true (Inercia de Mantenimiento).
        
        Devuelve SOLO un objeto JSON válido con este formato exacto:
        {{"toxicidad": 1, "estancado": false}}
        No añadas texto antes ni después del JSON.

        Comentarios:
        {comentarios_str[:2000]}
        """
        try:
            respuesta = ollama.chat(model=modelo, messages=[
                {'role': 'user', 'content': prompt}
            ])
            texto_respuesta = respuesta['message']['content'].strip()
            # Buscar el objeto JSON en la respuesta por si añade texto
            import json
            match = re.search(r'\{.*\}', texto_respuesta, re.DOTALL)
            if match:
                datos = json.loads(match.group(0))
                return {
                    "toxicidad": min(10, max(1, int(datos.get("toxicidad", 1)))),
                    "estancado": bool(datos.get("estancado", False))
                }
            return {"toxicidad": 1, "estancado": False}
        except Exception as e:
            print(f"Error analizando sentimiento y estancamiento: {e}")
            return {"toxicidad": 1, "estancado": False}
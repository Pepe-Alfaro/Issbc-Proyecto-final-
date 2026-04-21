# services/ollama_service.py
#import ollama
import re

class OllamaService:
    def analizar_con_ollama(self, texto, contexto_pdfs=""):
        """Usa Ollama para hacer un análisis cualitativo del texto"""
        prompt = f"""
        Actúa como un experto en diagnóstico de repositorios. 
        Analiza esta descripción o contexto de un repositorio de GitHub: '{texto}'.
        """
        if contexto_pdfs:
            prompt += f"\n\nTen en cuenta el siguiente CONTEXTO EXTRAÍDO DE MANUALES LOCALES:\n{contexto_pdfs[:2000]}"
            
        prompt += """
        \nIndica brevemente si parece un proyecto serio, si hay indicios de falta de cohesión o si es inestable.
        Sé directo y profesional. Responde en español.
        """
        print("🤖 Consultando a Ollama...")
        try:
            respuesta = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            return respuesta['message']['content']
        except Exception as e:
            return f"Error conectando con la IA local: {e}"

    def analizar_sentimiento(self, comentarios):
        """Evalúa el nivel de toxicidad de los comentarios del 1 al 10"""
        if not comentarios:
            return 1 
            
        comentarios_str = "\n---\n".join(comentarios)
        prompt = f"""
        Analiza los siguientes comentarios extraídos de Issues de un repositorio.
        Determina el nivel de hostilidad o toxicidad del 1 al 10 (donde 1 es completamente amigable y 10 es lenguaje abusivo y hostil).
        Devuelve SOLO el número final, sin explicaciones.
        
        Comentarios:
        {comentarios_str[:2000]}
        """
        try:
            respuesta = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            texto_num = respuesta['message']['content'].strip()
            nums = re.findall(r'\d+', texto_num)
            if nums:
                return min(10, max(1, int(nums[0])))
            return 1
        except Exception as e:
            print(f"Error analizando sentimiento: {e}")
            return 1
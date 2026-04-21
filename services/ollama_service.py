# services/ollama_service.py
#import ollama

class OllamaService:
    def analizar_con_ollama(self, texto):
        """Usa Ollama para hacer un análisis cualitativo del texto"""
        prompt = f"""
        Actúa como un experto en diagnóstico de repositorios. 
        Analiza esta descripción o contexto de un repositorio de GitHub: '{texto}'.
        Indica brevemente si parece un proyecto serio, si hay indicios de falta de cohesión o si es inestable.
        Sé directo y profesional.
        """
        print("🤖 Consultando a Ollama...")
        try:
            respuesta = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            return respuesta['message']['content']
        except Exception as e:
            return f"Error conectando con la IA local: {e}"
# controller/controller.py
from services.github_service import GitHubService
from services.ollama_service import OllamaService

class DiagnosticoController:
    def __init__(self, model):
        self.model = model
        # Instanciamos los servicios externos
        self.github_service = GitHubService()
        self.ollama_service = OllamaService()

    def update_model(self, data):
        self.model.observables.update(data)
        self.model.modo = data.get("modo", "Local")

    def _actualizar_datos_externos(self):
        """Función auxiliar para pedir los datos a GitHub si hay una URL"""
        url = self.model.observables.get("url_repo", "")
        if url:
            datos = self.github_service.extraer_datos_repo(url)
            if datos:
                self.model.observables["dias_sin_commits"] = datos["dias_inactividad"]
                self.model.observables["falta_docs"] = datos["falta_docs"]
                self.model.observables["descripcion_repo"] = datos["descripcion"]
    
    def generar_hipotesis(self):
        self._actualizar_datos_externos()
    
        dias = self.model.observables.get("dias_sin_commits", 0)
        falta_docs = self.model.observables.get("falta_docs", False)
    
        # 📝 Definición de Hipótesis según metodología CommonKADS
        nuevas_hipotesis = []

        # Hipótesis 1: Abandono Técnico
        # Se confirma si hay inactividad prolongada Y falta de gestión de issues
        if dias > 365:
            nuevas_hipotesis.append({
                "nombre": "Abandono Técnico (CommonKADS)", 
                "probabilidad": "Muy Alta", 
                "estado": "Confirmada"
            })
        elif dias > 180:
            nuevas_hipotesis.append({
                "nombre": "Mantenimiento Irregular", 
                "probabilidad": "Media", 
                "estado": "Posible"
            })

        # Hipótesis 2: Barrera de Entrada para Colaboradores
        # Se dispara si falta documentación técnica básica
        if falta_docs:
            nuevas_hipotesis.append({
                "nombre": "Dificultad de Adopción", 
                "probabilidad": "Alta", 
                "estado": "Sugerida"
            })

    # Hipótesis 3: Riesgo de Continuidad
    # Combinación de inactividad con otros factores (puedes añadir más métricas)
        if dias > 90 and falta_docs:
            nuevas_hipotesis.append({
                "nombre": "Riesgo de Continuidad", 
                "probabilidad": "Alta", 
                "estado": "Crítico"
            })

        self.model.hipotesis = nuevas_hipotesis

    def generar_diagnostico(self):
        # 1. Pedimos a GitHub los datos actualizados
        self._actualizar_datos_externos()

        # 2. Pedimos a Ollama que analice el texto (IA)
        texto_repo = self.model.observables.get("descripcion_repo", "")
        analisis_ia = self.ollama_service.analizar_con_ollama(texto_repo)

        # 3. Generamos veredicto combinado
        dias = self.model.observables.get("dias_sin_commits", 0)
        
        if self.model.observables.get("comentarios_toxicos"):
            self.model.diagnostico_final = "REPOSITORIO EN ESTADO CRÍTICO"
            self.model.justificacion = f"🚨 Se detectó hostilidad explícita.\n\n📊 CommonKADS: {dias} días de inactividad.\n\n🧠 Análisis IA: {analisis_ia}"
        elif dias > 365:
            self.model.diagnostico_final = "REPOSITORIO OBSOLETO"
            self.model.justificacion = f"📊 CommonKADS: Abandono técnico severo (>1 año sin commits).\n\n🧠 Análisis IA: {analisis_ia}"
        else:
            self.model.diagnostico_final = "REPOSITORIO ESTABLE"
            self.model.justificacion = f"📊 CommonKADS: Actividad normal ({dias} días sin commits). \n\n🧠 Análisis IA: {analisis_ia}"
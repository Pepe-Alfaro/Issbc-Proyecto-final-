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
                self.model.observables["dias_sin_commits"] = datos.get("dias_inactividad", 0)
                self.model.observables["falta_docs"] = datos.get("falta_docs", False)
                self.model.observables["descripcion_repo"] = datos.get("descripcion", "")
                self.model.observables["estrellas"] = datos.get("estrellas", 0)
                self.model.observables["issues_abiertas"] = datos.get("issues_abiertas", 0)
    
    def generar_hipotesis(self):
        self._actualizar_datos_externos()
    
        dias = self.model.observables.get("dias_sin_commits", 0)
        falta_docs = self.model.observables.get("falta_docs", False)
        issues = self.model.observables.get("issues_abiertas", 0)
    
        # 📝 Definición de Hipótesis según metodología CommonKADS
        nuevas_hipotesis = []

        # Abandono Crítico: Si dias_inactividad > 365.
        if dias > 365:
            nuevas_hipotesis.append({
                "nombre": "Abandono Crítico", 
                "probabilidad": "Muy Alta", 
                "estado": "Confirmada",
                "evidencia": f"Inactividad severa ({dias} días sin commits)",
                "accion": "Archivar proyecto o buscar nuevos mantenedores"
            })

        # Mantenimiento Deficiente: Si falta_docs es True Y issues_abiertas > 50.
        if falta_docs and issues > 50:
            nuevas_hipotesis.append({
                "nombre": "Mantenimiento Deficiente", 
                "probabilidad": "Alta", 
                "estado": "Sugerida",
                "evidencia": f"Falta docs básica y exceso de issues ({issues})",
                "accion": "Pausar desarrollo, exigir documentación y triaje"
            })
            
        # Proyecto Saturado: Si issues_abiertas es muy alto comparado con la actividad reciente.
        if issues > 100 and dias > 30:
            nuevas_hipotesis.append({
                "nombre": "Proyecto Saturado", 
                "probabilidad": "Media", 
                "estado": "Posible",
                "evidencia": f"Alta carga de issues ({issues}) con inactividad ({dias} días)",
                "accion": "Cerrar issues antiguas (Stale bot) y delegar"
            })

        # Hipótesis adicional si falta documentación pero no tiene tantas issues
        if falta_docs and issues <= 50:
            nuevas_hipotesis.append({
                "nombre": "Déficit Informativo", 
                "probabilidad": "Alta", 
                "estado": "Sugerida",
                "evidencia": "Ausencia de README o Wiki",
                "accion": "Redactar guía de inicio rápido (Getting Started)"
            })

        # Si no hay síntomas negativos, generamos la hipótesis de que está sano
        if not nuevas_hipotesis:
            nuevas_hipotesis.append({
                "nombre": "Proyecto Sano / Estable", 
                "probabilidad": "Muy Alta", 
                "estado": "Confirmada",
                "evidencia": f"Actividad normal ({dias} días), {issues} issues, docs presentes",
                "accion": "Continuar con el ciclo de desarrollo habitual"
            })

        self.model.hipotesis = nuevas_hipotesis

    def generar_diagnostico(self):
        # 1. Pedimos a GitHub los datos actualizados
        self._actualizar_datos_externos()

        # 2. Veredicto Analítico (Juicio puro basado en datos numéricos)
        dias = self.model.observables.get("dias_sin_commits", 0)
        falta_docs = self.model.observables.get("falta_docs", False)
        issues = self.model.observables.get("issues_abiertas", 0)
        
        veredicto_numerico = "REPOSITORIO ESTABLE"
        justificacion_numerica = f"Actividad normal ({dias} días sin commits), {issues} issues abiertas."
        
        if dias > 365:
            veredicto_numerico = "REPOSITORIO OBSOLETO / ABANDONO CRÍTICO"
            justificacion_numerica = f"Abandono técnico severo (>1 año sin commits). {issues} issues abiertas."
        elif falta_docs and issues > 50:
            veredicto_numerico = "REPOSITORIO CON MANTENIMIENTO DEFICIENTE"
            justificacion_numerica = f"Falta documentación básica y acumula excesivas issues ({issues})."
        elif issues > 100 and dias > 30:
            veredicto_numerico = "REPOSITORIO SATURADO"
            justificacion_numerica = f"Alta acumulación de issues ({issues}) con inactividad reciente ({dias} días sin commits)."
        elif dias > 180:
            veredicto_numerico = "REPOSITORIO CON MANTENIMIENTO IRREGULAR"
            justificacion_numerica = f"Inactividad prolongada ({dias} días sin commits)."

        # 3. Pedimos a Ollama que analice el texto (IA)
        texto_repo = self.model.observables.get("descripcion_repo", "")
        analisis_ia = self.ollama_service.analizar_con_ollama(texto_repo)

        # 4. Generamos veredicto combinado
        if self.model.observables.get("comentarios_toxicos"):
            self.model.diagnostico_final = "REPOSITORIO EN ESTADO CRÍTICO"
            self.model.justificacion = f"🚨 Se detectó hostilidad explícita.\n\n📊 CommonKADS: {justificacion_numerica}\n\n🧠 Análisis IA: {analisis_ia}"
        else:
            self.model.diagnostico_final = veredicto_numerico
            self.model.justificacion = f"📊 Análisis Cuantitativo: {justificacion_numerica}\n\n🧠 Análisis IA: {analisis_ia}"
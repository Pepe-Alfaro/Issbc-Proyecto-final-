# controller/controller.py
from services.github_service import GitHubService
from services.ollama_service import OllamaService
from services.cache_service import CacheService
import PyPDF2

class DiagnosticoController:
    def __init__(self, model):
        self.model = model
        # Instanciamos los servicios externos
        self.github_service = GitHubService()
        self.ollama_service = OllamaService()
        self.cache_service = CacheService()

    def update_model(self, data):
        self.model.observables.update(data)
        self.model.modo = data.get("modo", "Local")
        self.model.motor = data.get("motor", "📊 CommonKADS")

    def _actualizar_datos_externos(self):
        """Función auxiliar para pedir los datos a GitHub si hay una URL"""
        url = self.model.observables.get("url_repo", "")
        if url:
            # 1. Comprobar Caché
            datos = self.cache_service.get(url)
            
            # 2. Si no hay caché, pedir a GitHub
            if not datos:
                datos = self.github_service.extraer_datos_repo(url)
                if datos:
                    # Análisis de Sentimiento Pesado solo se hace una vez y se cachea
                    comentarios = datos.get("comentarios_recientes", [])
                    if comentarios:
                        nivel_toxicidad = self.ollama_service.analizar_sentimiento(comentarios)
                        datos["comentarios_toxicos"] = nivel_toxicidad > 6
                    else:
                        datos["comentarios_toxicos"] = False
                    
                    self.cache_service.set(url, datos)

            if datos:
                self.model.observables["dias_sin_commits"] = datos.get("dias_inactividad", 0)
                self.model.observables["falta_docs"] = datos.get("falta_docs", False)
                self.model.observables["descripcion_repo"] = datos.get("descripcion", "")
                self.model.observables["estrellas"] = datos.get("estrellas", 0)
                self.model.observables["issues_abiertas"] = datos.get("issues_abiertas", 0)
                self.model.observables["forks"] = datos.get("forks", 0)
                self.model.observables["lenguaje"] = datos.get("lenguaje", "")
                self.model.observables["prs_abiertas"] = datos.get("prs_abiertas", 0)
                self.model.observables["contribuyentes"] = datos.get("contribuyentes", 1)
                self.model.observables["tiene_licencia"] = datos.get("tiene_licencia", False)
                self.model.observables["comentarios_toxicos"] = datos.get("comentarios_toxicos", False)
                self.model.observables["rate_limit_info"] = datos.get("rate_limit_info", "?/?")
                self.model.observables["ultimos_commits"] = datos.get("ultimos_commits", [])

    def _extraer_texto_pdfs(self):
        texto_completo = ""
        for pdf_path in getattr(self.model, "pdfs_locales", []):
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        texto_completo += page.extract_text() + "\n"
            except Exception as e:
                print(f"Error leyendo PDF {pdf_path}: {e}")
        return texto_completo
    
    def generar_hipotesis(self):
        self._actualizar_datos_externos()
    
        dias = self.model.observables.get("dias_sin_commits", 0)
        falta_docs = self.model.observables.get("falta_docs", False)
        issues = self.model.observables.get("issues_abiertas", 0)
        estrellas = self.model.observables.get("estrellas", 0)
        forks = self.model.observables.get("forks", 0)
        prs = self.model.observables.get("prs_abiertas", 0)
        contribuyentes = self.model.observables.get("contribuyentes", 1)
        tiene_licencia = self.model.observables.get("tiene_licencia", False)
    
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
            
        # --- NUEVAS HIPÓTESIS ---
        if estrellas > 100 and forks > 30:
            nuevas_hipotesis.append({
                "nombre": "Comunidad en Expansión", 
                "probabilidad": "Alta", 
                "estado": "Confirmada",
                "evidencia": f"Alta popularidad ({estrellas} estrellas, {forks} forks)",
                "accion": "Mantener la buena gestión y considerar donaciones/patrocinios"
            })
            
        if prs > 10 and dias > 15:
            nuevas_hipotesis.append({
                "nombre": "Cuello de Botella (Reviews)", 
                "probabilidad": "Alta", 
                "estado": "Sugerida",
                "evidencia": f"{prs} PRs abiertas y sin actividad reciente",
                "accion": "Asignar revisores o cerrar PRs obsoletas"
            })
            
        if not tiene_licencia:
            nuevas_hipotesis.append({
                "nombre": "Riesgo Legal", 
                "probabilidad": "Crítica", 
                "estado": "Confirmada",
                "evidencia": "El repositorio no tiene una licencia explícita",
                "accion": "Añadir archivo LICENSE (ej. MIT, Apache 2.0)"
            })
            
        if contribuyentes <= 1 and estrellas > 10:
            nuevas_hipotesis.append({
                "nombre": "Proyecto Frágil (Bus Factor)", 
                "probabilidad": "Media", 
                "estado": "Posible",
                "evidencia": "Popular pero mantenido por una sola persona",
                "accion": "Delegar responsabilidades y atraer core-contributors"
            })
            
        if contribuyentes >= 5 and issues < 10:
            nuevas_hipotesis.append({
                "nombre": "Comunidad Eficiente", 
                "probabilidad": "Alta", 
                "estado": "Sugerida",
                "evidencia": "Múltiples contribuyentes con baja tasa de issues",
                "accion": "Continuar prácticas actuales"
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

        motor_seleccionado = getattr(self.model, "motor", "📊 CommonKADS")

        if "CommonKADS" in motor_seleccionado:
            # 2. Veredicto Analítico (Juicio puro basado en datos numéricos)
            dias = self.model.observables.get("dias_sin_commits", 0)
            falta_docs = self.model.observables.get("falta_docs", False)
            issues = self.model.observables.get("issues_abiertas", 0)
            prs = self.model.observables.get("prs_abiertas", 0)
            contribuyentes = self.model.observables.get("contribuyentes", 1)
            tiene_licencia = self.model.observables.get("tiene_licencia", True) # Por defecto true para no asustar si no se lee
            
            veredicto_numerico = "REPOSITORIO ESTABLE"
            justificacion_numerica = f"Actividad normal ({dias} días sin commits), {issues} issues abiertas."
            
            if dias > 365:
                veredicto_numerico = "REPOSITORIO OBSOLETO / ABANDONO CRÍTICO"
                justificacion_numerica = f"Abandono técnico severo (>1 año sin commits). {issues} issues abiertas."
            elif falta_docs and issues > 50:
                veredicto_numerico = "REPOSITORIO CON MANTENIMIENTO DEFICIENTE"
                justificacion_numerica = f"Falta documentación básica y acumula excesivas issues ({issues})."
            elif prs > 10 and dias > 15:
                veredicto_numerico = "REPOSITORIO CON CUELLO DE BOTELLA (PRs)"
                justificacion_numerica = f"Hay un claro bloqueo en revisiones con {prs} PRs esperando."
            elif not tiene_licencia:
                veredicto_numerico = "REPOSITORIO EN RIESGO LEGAL"
                justificacion_numerica = f"Falta archivo de licencia. Impide uso comercial o colaboración segura."
            elif contribuyentes <= 1 and issues > 10:
                veredicto_numerico = "REPOSITORIO FRÁGIL (MANTENIMIENTO INDIVIDUAL)"
                justificacion_numerica = f"El proyecto depende enteramente de una persona para resolver {issues} issues."
            elif issues > 100 and dias > 30:
                veredicto_numerico = "REPOSITORIO SATURADO"
                justificacion_numerica = f"Alta acumulación de issues ({issues}) con inactividad reciente ({dias} días sin commits)."
            elif dias > 180:
                veredicto_numerico = "REPOSITORIO CON MANTENIMIENTO IRREGULAR"
                justificacion_numerica = f"Inactividad prolongada ({dias} días sin commits)."
            elif contribuyentes >= 5 and issues < 10:
                veredicto_numerico = "PROYECTO ALTAMENTE RECOMENDADO"
                justificacion_numerica = f"Comunidad activa ({contribuyentes} devs), y bajos reportes de fallos."

            self.model.diagnostico_final = veredicto_numerico
            self.model.justificacion = f"📊 Análisis Cuantitativo (CommonKADS): {justificacion_numerica}"
        else:
            # 3. Pedimos a Ollama que analice el texto (IA)
            texto_repo = self.model.observables.get("descripcion_repo", "")
            contexto_pdfs = self._extraer_texto_pdfs()
            
            analisis_ia = self.ollama_service.analizar_con_ollama(texto_repo, contexto_pdfs)

            self.model.diagnostico_final = "DIAGNÓSTICO BASADO EN IA"
            self.model.justificacion = f"🧠 Análisis IA (Ollama):\n{analisis_ia}"

        # 4. Generamos veredicto combinado con toxicidad si existe
        if self.model.observables.get("comentarios_toxicos"):
            self.model.diagnostico_final = "REPOSITORIO EN ESTADO CRÍTICO"
            justificacion_previa = self.model.justificacion
            self.model.justificacion = f"🚨 Se detectó hostilidad explícita en la comunidad.\n\n{justificacion_previa}"
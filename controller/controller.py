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
        self.model.modelo_ollama = data.get("modelo_ollama", "phi3:mini")

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
                        modelo = getattr(self.model, "modelo_ollama", "phi3:mini")
                        nivel_toxicidad = self.ollama_service.analizar_sentimiento(comentarios, modelo)
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
                self.model.observables["rate_limit_info"] = self.github_service.get_rate_limit_info()
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
    
        # 📝 Definición de Hipótesis según metodología CommonKADS con porcentajes
        nuevas_hipotesis = []

        # 1. Abandono Crítico
        prob = min(100, int(dias / 3)) if dias > 0 else 0
        nuevas_hipotesis.append({
            "nombre": "Abandono Crítico", 
            "probabilidad": f"{prob}%", 
            "prob_num": prob,
            "estado": "Confirmada" if prob > 80 else ("Sugerida" if prob > 40 else "Descartada"),
            "evidencia": f"Inactividad de {dias} días",
            "accion": "Archivar proyecto o buscar nuevos mantenedores"
        })

        # 2. Mantenimiento Deficiente
        prob_mant = 0
        if falta_docs: prob_mant += 30
        prob_mant += min(70, issues)
        nuevas_hipotesis.append({
            "nombre": "Mantenimiento Deficiente", 
            "probabilidad": f"{prob_mant}%", 
            "prob_num": prob_mant,
            "estado": "Confirmada" if prob_mant > 80 else ("Sugerida" if prob_mant > 40 else "Descartada"),
            "evidencia": f"Docs: {'No' if falta_docs else 'Sí'}, Issues: {issues}",
            "accion": "Pausar desarrollo, exigir documentación y triaje"
        })
        
        # 3. Proyecto Saturado
        prob_sat = min(100, int((issues / max(1, contribuyentes)) * 2 + min(30, dias)))
        nuevas_hipotesis.append({
            "nombre": "Proyecto Saturado", 
            "probabilidad": f"{prob_sat}%", 
            "prob_num": prob_sat,
            "estado": "Confirmada" if prob_sat > 80 else ("Sugerida" if prob_sat > 40 else "Descartada"),
            "evidencia": f"{issues} issues para {contribuyentes} devs con inactividad ({dias} días)",
            "accion": "Cerrar issues antiguas (Stale bot) y delegar"
        })
        
        # 4. Déficit Informativo
        prob_def = 100 if falta_docs else 0
        nuevas_hipotesis.append({
            "nombre": "Déficit Informativo", 
            "probabilidad": f"{prob_def}%", 
            "prob_num": prob_def,
            "estado": "Confirmada" if prob_def == 100 else "Descartada",
            "evidencia": "Ausencia de README o Wiki" if falta_docs else "Documentación presente",
            "accion": "Redactar guía de inicio rápido"
        })
        
        # 5. Comunidad en Expansión
        prob_exp = min(100, int((estrellas / 5) + (forks * 2)))
        nuevas_hipotesis.append({
            "nombre": "Comunidad en Expansión", 
            "probabilidad": f"{prob_exp}%", 
            "prob_num": prob_exp,
            "estado": "Confirmada" if prob_exp > 80 else ("Sugerida" if prob_exp > 40 else "Descartada"),
            "evidencia": f"{estrellas} estrellas, {forks} forks",
            "accion": "Considerar donaciones/patrocinios"
        })
        
        # 6. Cuello de Botella (Reviews)
        prob_pr = min(100, int((prs * 5) + min(50, dias)))
        nuevas_hipotesis.append({
            "nombre": "Cuello de Botella (Reviews)", 
            "probabilidad": f"{prob_pr}%", 
            "prob_num": prob_pr,
            "estado": "Confirmada" if prob_pr > 80 else ("Sugerida" if prob_pr > 40 else "Descartada"),
            "evidencia": f"{prs} PRs abiertas, {dias} días inactividad",
            "accion": "Asignar revisores o cerrar PRs obsoletas"
        })
        
        # 7. Riesgo Legal
        prob_leg = 100 if not tiene_licencia else 0
        nuevas_hipotesis.append({
            "nombre": "Riesgo Legal", 
            "probabilidad": f"{prob_leg}%", 
            "prob_num": prob_leg,
            "estado": "Confirmada" if prob_leg == 100 else "Descartada",
            "evidencia": "Falta licencia" if not tiene_licencia else "Licencia explícita encontrada",
            "accion": "Añadir archivo LICENSE"
        })
        
        # 8. Proyecto Frágil (Bus Factor)
        prob_bus = 0
        if contribuyentes <= 1:
            prob_bus = min(100, 50 + estrellas)
        nuevas_hipotesis.append({
            "nombre": "Proyecto Frágil (Bus Factor)", 
            "probabilidad": f"{prob_bus}%", 
            "prob_num": prob_bus,
            "estado": "Confirmada" if prob_bus > 80 else ("Sugerida" if prob_bus > 40 else "Descartada"),
            "evidencia": f"1 contribuyente principal, {estrellas} estrellas",
            "accion": "Delegar responsabilidades"
        })
        
        # 9. Proyecto Sano / Estable
        prob_sano = max(0, 100 - max(prob, prob_mant, prob_sat, prob_pr, prob_bus))
        nuevas_hipotesis.append({
            "nombre": "Proyecto Sano / Estable", 
            "probabilidad": f"{prob_sano}%", 
            "prob_num": prob_sano,
            "estado": "Confirmada" if prob_sano > 80 else ("Sugerida" if prob_sano > 40 else "Descartada"),
            "evidencia": f"Métricas estables. Actividad: {dias}d, Issues: {issues}",
            "accion": "Continuar ciclo habitual"
        })

        # Ordenar de mayor a menor probabilidad
        nuevas_hipotesis.sort(key=lambda x: x["prob_num"], reverse=True)

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
            modelo = getattr(self.model, "modelo_ollama", "phi3:mini")
            
            analisis_ia = self.ollama_service.analizar_con_ollama(texto_repo, contexto_pdfs, modelo)

            self.model.diagnostico_final = "DIAGNÓSTICO BASADO EN IA"
            self.model.justificacion = f"🧠 Análisis IA (Ollama):\n{analisis_ia}"

        # 4. Generamos veredicto combinado con toxicidad si existe
        if self.model.observables.get("comentarios_toxicos"):
            self.model.diagnostico_final = "REPOSITORIO EN ESTADO CRÍTICO"
            justificacion_previa = self.model.justificacion
            self.model.justificacion = f"🚨 Se detectó hostilidad explícita en la comunidad.\n\n{justificacion_previa}"
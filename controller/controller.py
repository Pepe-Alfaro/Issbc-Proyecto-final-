# controller/controller.py
from services.github_service import GitHubService
from services.ollama_service import OllamaService
from services.cache_service import CacheService
from services.web_search_service import WebSearchService
import PyPDF2

class DiagnosticoController:
    def __init__(self, model):
        self.model = model
        # Instanciamos los servicios externos
        self.github_service = GitHubService()
        self.ollama_service = OllamaService()
        self.cache_service = CacheService()
        self.web_search_service = WebSearchService()

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
                        analisis_social = self.ollama_service.analizar_sentimiento(comentarios, modelo)
                        if isinstance(analisis_social, dict):
                            datos["comentarios_toxicos"] = analisis_social.get("toxicidad", 1) > 6
                            datos["comunidad_estancada"] = analisis_social.get("estancado", False)
                        else:
                            datos["comentarios_toxicos"] = analisis_social > 6
                            datos["comunidad_estancada"] = False
                    else:
                        datos["comentarios_toxicos"] = False
                        datos["comunidad_estancada"] = False
                    
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
                self.model.observables["comunidad_estancada"] = datos.get("comunidad_estancada", False)
                self.model.observables["pr_avg_age_days"] = datos.get("pr_avg_age_days", 0)
                self.model.observables["pr_old_ratio"] = datos.get("pr_old_ratio", 0.0)
                self.model.observables["rate_limit_info"] = self.github_service.get_rate_limit_info()
                self.model.observables["ultimos_commits"] = datos.get("ultimos_commits", [])
                self.model.observables["readme_content"] = datos.get("readme_content", "")
                self.model.observables["contributing_content"] = datos.get("contributing_content", "")
                self.model.observables["coc_content"] = datos.get("coc_content", "")

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
        
        ratio_issues = (issues / estrellas) if estrellas > 0 else issues
        
        if estrellas > 10000 and ratio_issues < 0.01:
            prob_mant += min(10, issues) # Penalización leve para repos grandes
        else:
            prob_mant += min(70, issues)
            
        nuevas_hipotesis.append({
            "nombre": "Mantenimiento Deficiente", 
            "probabilidad": f"{prob_mant}%", 
            "prob_num": prob_mant,
            "estado": "Confirmada" if prob_mant > 80 else ("Sugerida" if prob_mant > 40 else "Descartada"),
            "evidencia": f"Docs: {'No' if falta_docs else 'Sí'}, Issues/Stars Ratio: {ratio_issues:.4f}",
            "accion": "Pausar desarrollo, exigir documentación y triaje"
        })
        
        # 3. Proyecto Saturado
        if estrellas >= 10000 and ratio_issues < 0.01:
            prob_sat = 0
            evidencia_sat = f"Gran proyecto con excelente ratio de issues ({ratio_issues:.4f})"
        else:
            prob_sat = min(100, int((issues / max(1, contribuyentes)) * 2 + min(30, dias)))
            evidencia_sat = f"{issues} issues para {contribuyentes} devs con inactividad ({dias} días)"
            
        nuevas_hipotesis.append({
            "nombre": "Proyecto Saturado", 
            "probabilidad": f"{prob_sat}%", 
            "prob_num": prob_sat,
            "estado": "Confirmada" if prob_sat > 80 else ("Sugerida" if prob_sat > 40 else "Descartada"),
            "evidencia": evidencia_sat,
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
        
        # 8. Desbordamiento (Deuda Técnica)
        prob_deuda = min(100, int((prs * 2) + (issues / max(1, contribuyentes)))) if dias < 10 else 0
        if estrellas > 10000 and ratio_issues < 0.005:
            prob_deuda = 0  # Proyectos inmensos tienen volúmenes distintos y controlados
            
        nuevas_hipotesis.append({
            "nombre": "Desbordamiento (Deuda Técnica)",
            "probabilidad": f"{prob_deuda}%",
            "prob_num": prob_deuda,
            "estado": "Confirmada" if prob_deuda > 80 else ("Sugerida" if prob_deuda > 40 else "Descartada"),
            "evidencia": f"Actividad continua (hace {dias}d) pero acumula {prs} PRs y {issues} issues",
            "accion": "Pausar nuevas features y hacer sprint de revisión (Bug-squash)"
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
            estrellas = self.model.observables.get("estrellas", 0)
            pr_avg_age = self.model.observables.get("pr_avg_age_days", 0)
            pr_old_ratio = self.model.observables.get("pr_old_ratio", 0.0)
            
            ratio_issues = (issues / estrellas) if estrellas > 0 else issues
            
            veredicto_numerico = "REPOSITORIO ESTABLE"
            justificacion_numerica = f"Actividad normal ({dias} días sin commits), {issues} issues abiertas."
            
            readme_lower = self.model.observables.get("readme_content", "").lower()
            es_mantenimiento = "maintenance mode" in readme_lower or "deprecated" in readme_lower or "no longer supported" in readme_lower
            
            if dias > 365 or es_mantenimiento:
                veredicto_numerico = "OBSOLETO"
                justificacion_numerica = f"Inactividad severa (>365 días) o el proyecto está explícitamente marcado como Legacy/Maintenance."
            elif ratio_issues > 0.05 or pr_avg_age > 180:
                veredicto_numerico = "CUELLO DE BOTELLA"
                justificacion_numerica = f"Alto ratio de issues ({ratio_issues:.4f}) O antigüedad media de PRs crítica ({int(pr_avg_age)} días)."
            elif ratio_issues < 0.01 and dias < 30:
                veredicto_numerico = "ALTAMENTE RECOMENDADO"
                justificacion_numerica = f"Excelente ratio issues/estrellas ({ratio_issues:.4f}) y actividad reciente ({dias} días sin commits)."

            self.model.diagnostico_final = veredicto_numerico
            self.model.justificacion = f"📊 Análisis Cuantitativo (CommonKADS): {justificacion_numerica}"
        else:
            # 3. Pedimos a Ollama que analice el texto (IA)
            texto_repo = self.model.observables.get("descripcion_repo", "")
            contexto_pdfs = self._extraer_texto_pdfs()
            
            # NUEVO: Si estamos en modo "Local + Web", añadimos contexto extra de internet
            if "Web" in self.model.modo:
                print("🌐 Modo 'Local + Web' activo. Recopilando contexto web...")
                
                # RAG: Priorizar CONTRIBUTING.md y CODE_OF_CONDUCT.md
                coc = self.model.observables.get("coc_content", "")
                contrib = self.model.observables.get("contributing_content", "")
                
                if coc:
                    contexto_pdfs = f"\n\n--- DOCUMENTO CRÍTICO: CODE_OF_CONDUCT.md ---\n{coc[:1000]}\n" + contexto_pdfs
                if contrib:
                    contexto_pdfs = f"\n\n--- DOCUMENTO CRÍTICO: CONTRIBUTING.md ---\n{contrib[:1000]}\n" + contexto_pdfs
                
                # a) Añadimos el README (que es contexto web directo del repo)
                readme = self.model.observables.get("readme_content", "")
                if readme:
                    contexto_pdfs += f"\n\n--- CONTEXTO WEB (README) ---\n{readme[:1500]}"
                
                # b) Hacemos una búsqueda web en base a la URL o descripción
                url_repo = self.model.observables.get("url_repo", "")
                if url_repo:
                    nombre_repo = url_repo.split("/")[-1]
                    info_web = self.web_search_service.buscar_info_web(f"github {nombre_repo} repository")
                    contexto_pdfs += f"\n\n--- CONTEXTO WEB (BÚSQUEDA) ---\nResultados de búsqueda sobre '{nombre_repo}':\n{info_web}"
            
            modelo = getattr(self.model, "modelo_ollama", "phi3:mini")
            
            analisis_ia = self.ollama_service.analizar_con_ollama(texto_repo, contexto_pdfs, modelo)

            self.model.diagnostico_final = "DIAGNÓSTICO BASADO EN IA"
            self.model.justificacion = f"🧠 Análisis IA (Ollama):\n{analisis_ia}"

        # 4. Generamos veredicto combinado con flags sociales (toxicidad / estancamiento)
        if self.model.observables.get("comentarios_toxicos"):
            self.model.diagnostico_final = "ESTADO CRÍTICO"
            justificacion_previa = self.model.justificacion
            self.model.justificacion = f"🚨 Se detectó hostilidad explícita en la comunidad.\n\n{justificacion_previa}"
        elif self.model.observables.get("comunidad_estancada") and self.model.diagnostico_final not in ["OBSOLETO", "ESTADO CRÍTICO"]:
            if self.model.diagnostico_final == "ALTAMENTE RECOMENDADO" or self.model.diagnostico_final == "REPOSITORIO ESTABLE":
                self.model.diagnostico_final = "CUELLO DE BOTELLA"
            justificacion_previa = self.model.justificacion
            self.model.justificacion = f"⚠️ IA Detectó Inercia: La comunidad reporta estancamiento (PRs ignorados, falta de releases).\n\n{justificacion_previa}"
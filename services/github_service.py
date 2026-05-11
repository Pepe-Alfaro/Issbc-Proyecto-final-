# services/github_service.py
import os
import datetime
from github import Github
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class GitHubService:
    def __init__(self):
        # Leer el token de forma segura al inicializar el servicio
        self.token = os.getenv("GITHUB_TOKEN", "")
        # Si hay token lo usa; si no, intenta conexión anónima (limitada)
        self.g = Github(self.token) if self.token else Github()

    def extraer_datos_repo(self, url_repo):
        """Extrae métricas reales usando PyGithub y devuelve un diccionario"""
        print(f"📡 Conectando a GitHub: {url_repo}...")
        try:
            # Limpiar la URL para obtener el formato 'usuario/repo'
            path = url_repo.replace("https://github.com/", "").strip("/")
            if path.endswith(".git"):
                path = path[:-4]
            repo = self.g.get_repo(path)

            # 1. Obtener días desde el último commit
            ultimo_commit = repo.get_commits()[0]
            fecha_commit = ultimo_commit.commit.author.date
            
            # Asegurar comparación con zona horaria UTC
            hoy = datetime.datetime.now(datetime.timezone.utc)
            dias_inactividad = (hoy - fecha_commit.replace(tzinfo=datetime.timezone.utc)).days

            # 2. Comprobar documentación (Wiki o README)
            tiene_wiki = repo.has_wiki
            readme_content = ""
            try:
                readme = repo.get_readme()
                tiene_readme = True
                readme_content = readme.decoded_content.decode('utf-8', errors='ignore')
            except:
                tiene_readme = False
            falta_docs = not (tiene_wiki or tiene_readme)

            contributing_content = ""
            try:
                contributing_content = repo.get_contents("CONTRIBUTING.md").decoded_content.decode('utf-8', errors='ignore')
            except:
                pass

            coc_content = ""
            try:
                coc_content = repo.get_contents("CODE_OF_CONDUCT.md").decoded_content.decode('utf-8', errors='ignore')
            except:
                pass

            # 3. Métricas adicionales para CommonKADS (Sugeridas)
            estrellas = repo.stargazers_count
            issues_abiertas = repo.open_issues_count
            forks = repo.forks_count
            lenguaje = repo.language or "No detectado"

            # 4. Extracciones que requieren llamadas adicionales a la API (paginadas)
            pr_avg_age_days = 0
            pr_old_ratio = 0.0
            try:
                open_prs = repo.get_pulls(state='open')
                prs_abiertas = open_prs.totalCount
                
                if prs_abiertas > 0:
                    # Muestreo rápido de las PRs (primeras 30) para calcular inercia
                    sampled_prs = list(open_prs[:30])
                    if sampled_prs:
                        now = datetime.datetime.now(datetime.timezone.utc)
                        ages = [(now - pr.created_at.replace(tzinfo=datetime.timezone.utc)).days for pr in sampled_prs]
                        pr_avg_age_days = sum(ages) / len(ages)
                        old_prs = sum(1 for age in ages if age > 180) # PRs con más de 6 meses
                        pr_old_ratio = old_prs / len(ages)
            except:
                prs_abiertas = 0
                
            try:
                contribuyentes = repo.get_contributors().totalCount
            except:
                contribuyentes = 1 # Asumimos al menos el creador
                
            try:
                repo.get_license()
                tiene_licencia = True
            except:
                tiene_licencia = False

            # 5. Extraer descripción para el análisis de IA (Ollama)
            descripcion = repo.description or "Repositorio sin descripción proporcionada."

            # 6. Rate Limit
            try:
                rate_limit = self.g.get_rate_limit().rate
                rate_limit_info = f"{rate_limit.remaining}/{rate_limit.limit}"
            except:
                rate_limit_info = "?/?"

            # 7. Últimos 3 commits
            ultimos_commits = []
            try:
                for c in repo.get_commits()[:3]:
                    msg = c.commit.message.split('\n')[0][:50]
                    fecha = c.commit.author.date.strftime('%Y-%m-%d')
                    ultimos_commits.append(f"{fecha}: {msg}")
            except:
                pass

            # 8. Comentarios recientes (para análisis de sentimiento)
            comentarios_recientes = []
            try:
                for issue in repo.get_issues(state='all', sort='updated', direction='desc')[:5]:
                    if issue.body:
                        comentarios_recientes.append(issue.body[:200])
                    for comment in issue.get_comments()[:2]:
                        if comment.body:
                            comentarios_recientes.append(comment.body[:200])
            except:
                pass

            # Devolvemos los datos procesados al controlador
            return {
                "dias_inactividad": dias_inactividad,
                "falta_docs": falta_docs,
                "estrellas": estrellas,
                "issues_abiertas": issues_abiertas,
                "forks": forks,
                "lenguaje": lenguaje,
                "prs_abiertas": prs_abiertas,
                "pr_avg_age_days": pr_avg_age_days,
                "pr_old_ratio": pr_old_ratio,
                "contribuyentes": contribuyentes,
                "tiene_licencia": tiene_licencia,
                "descripcion": descripcion,
                "rate_limit_info": rate_limit_info,
                "ultimos_commits": ultimos_commits,
                "comentarios_recientes": comentarios_recientes,
                "readme_content": readme_content,
                "contributing_content": contributing_content,
                "coc_content": coc_content
            }
        except Exception as e:
            print(f"❌ Error de conexión con GitHub: {e}")
            return None

    def get_rate_limit_info(self):
        """Consulta directamente el límite actual de la API"""
        try:
            rate_limit = self.g.get_rate_limit().rate
            return f"{rate_limit.remaining}/{rate_limit.limit}"
        except:
            return "?/?"
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
        self.g = Github(self.token) if self.token else Github()

    def extraer_datos_repo(self, url_repo):
        """Extrae métricas reales usando PyGithub y devuelve un diccionario"""
        print(f"📡 Conectando a GitHub: {url_repo}...")
        try:
            path = url_repo.replace("https://github.com/", "").strip("/")
            repo = self.g.get_repo(path)

            # 1. Obtener días desde el último commit
            ultimo_commit = repo.get_commits()[0]
            fecha_commit = ultimo_commit.commit.author.date
            
            hoy = datetime.datetime.now(datetime.timezone.utc)
            dias_inactividad = (hoy - fecha_commit.replace(tzinfo=datetime.timezone.utc)).days

            # 2. Comprobar documentación (Wiki o README)
            tiene_wiki = repo.has_wiki
            try:
                repo.get_readme()
                tiene_readme = True
            except:
                tiene_readme = False
            falta_docs = not (tiene_wiki or tiene_readme)

            # 3. Extraer texto para la IA
            descripcion = repo.description or "Repositorio sin descripción proporcionada."

            # Devolvemos los datos procesados al controlador
            return {
                "dias_inactividad": dias_inactividad,
                "falta_docs": falta_docs,
                "descripcion": descripcion
            }
        except Exception as e:
            print(f"❌ Error de conexión con GitHub: {e}")
            return None
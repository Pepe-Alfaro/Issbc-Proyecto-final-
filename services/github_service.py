import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubService:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        self.g = Github(token)

    def obtener_metricas(self, url_repo):
        try:
            path = url_repo.replace("https://github.com/", "").strip("/")
            repo = self.g.get_repo(path)
            
            ultimo_commit = repo.get_commits()[0].commit.author.date
            # Aquí podrías sacar más datos: estrellas, número de issues, etc.
            return {
                "fecha_ultimo_commit": ultimo_commit,
                "lenguaje": repo.language,
                "estrellas": repo.stargazers_count
            }
        except Exception as e:
            print(f"Error en GitHubService: {e}")
            return None
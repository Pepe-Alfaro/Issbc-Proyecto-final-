# controller/controller.py

from github import Github
import datetime


class DiagnosticoController:
    def __init__(self, model):
        self.model = model
        self.token = ""
        self.g = Github(self.token)

    def extraer_datos_github(self, url_repo):
        """Extrae métricas reales usando PyGithub"""
        try:
            # Limpiar la URL para obtener 'usuario/repo'
            path = url_repo.replace("https://github.com/", "").strip("/")
            repo = self.g.get_repo(path)

            # 1. Obtener días desde el último commit
            ultimo_commit = repo.get_commits()[0]
            fecha_commit = ultimo_commit.commit.author.date
            
            # Asegurar que comparamos fechas con zona horaria (UTC)
            hoy = datetime.datetime.now(datetime.timezone.utc)
            dias_inactividad = (hoy - fecha_commit.replace(tzinfo=datetime.timezone.utc)).days

            # 2. Actualizar el modelo con datos REALES [cite: 25, 29]
            self.model.observables["dias_sin_commits"] = dias_inactividad
            # Puedes añadir más métricas, como el lenguaje principal o estrellas
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    def update_model(self, data):
        self.model.observables.update(data)
        self.model.modo = data.get("modo", "Local")

    def generar_hipotesis(self):
        # Ahora usa los datos reales guardados en el modelo [cite: 30]
        dias = self.model.observables["dias_sin_commits"]
        self.model.hipotesis = [
            {"nombre": "Repo Obsoleto", "probabilidad": "Alta" if dias > 365 else "Baja", "estado": "Posible"},
            {"nombre": "Comunidad Tóxica", "probabilidad": "Crítica" if self.model.observables["comentarios_toxicos"] else "Baja", "estado": "Posible"}
        ]

    def generar_diagnostico(self):
        # Lógica de veredicto final basada en los síntomas [cite: 7, 31]
        if self.model.observables["comentarios_toxicos"]:
            self.model.diagnostico_final = "REPOSITORIO EN ESTADO CRÍTICO"
            self.model.justificacion = "El análisis detectó hostilidad. Días de inactividad: " + str(self.model.observables["dias_sin_commits"])
        else:
            self.model.diagnostico_final = "REPOSITORIO ESTABLE"
            self.model.justificacion = "Los parámetros técnicos son correctos."
        


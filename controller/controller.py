from services.github_service import GitHubService
import datetime

class DiagnosticoController:
    def __init__(self, model):
        self.model = model
        self.github_service = GitHubService() # Usamos el servicio

    def extraer_datos_reales(self, url):
        datos = self.github_service.obtener_metricas(url)
        if datos:
            hoy = datetime.datetime.now(datetime.timezone.utc)
            dias = (hoy - datos["fecha_ultimo_commit"].replace(tzinfo=datetime.timezone.utc)).days
            self.model.observables["dias_sin_commits"] = dias
            return True
        return False
    
    # ... resto de tus métodos (generar_hipotesis, etc.)
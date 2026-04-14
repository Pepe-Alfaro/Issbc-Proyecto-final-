# model/model.py

class DiagnosticoModel:
    def __init__(self):
        self.observables = {"dias_sin_commits": 0, "falta_docs": False, "comentarios_toxicos": False}
        self.modo = "Local"
        self.pdfs_locales = []
        self.hipotesis = []
        self.diagnostico_final = ""
        self.justificacion = ""
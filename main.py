# main.py
import sys
from PyQt5.QtWidgets import QApplication
from model.model import DiagnosticoModel
from controller.controller import DiagnosticoController
from view.view import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Ensamblaje MVC
    modelo = DiagnosticoModel()
    controlador = DiagnosticoController(modelo)
    ventana = MainWindow(controlador)
    
    ventana.show()
    sys.exit(app.exec_())
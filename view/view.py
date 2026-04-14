# vista/view.py
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton, 
                             QListWidget, QMessageBox, QFileDialog, QGroupBox, 
                             QDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTextEdit, QFormLayout, QApplication,
                             QLineEdit, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

# ==========================================
# DIÁLOGOS ADICIONALES
# ==========================================

class HipotesisDialog(QDialog):
    def __init__(self, hipotesis_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hipótesis Posibles")
        self.setMinimumSize(600, 350)
        self.init_ui(hipotesis_data)

    def init_ui(self, hipotesis_data):
        layout = QVBoxLayout(self)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Hipótesis", "Probabilidad", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.setRowCount(len(hipotesis_data))
        
        font_tabla = QFont("Segoe UI", 11)
        self.tabla.setFont(font_tabla)
        
        for row, hip in enumerate(hipotesis_data):
            self.tabla.setItem(row, 0, QTableWidgetItem(hip["nombre"]))
            self.tabla.setItem(row, 1, QTableWidgetItem(hip["probabilidad"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(hip["estado"]))
            
        layout.addWidget(self.tabla)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(120)
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)


class DiagnosticoDialog(QDialog):
    def __init__(self, diagnostico, justificacion, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagnóstico Final y Justificación")
        self.setMinimumSize(600, 500)
        self.init_ui(diagnostico, justificacion)

    def init_ui(self, diagnostico, justificacion):
        layout = QVBoxLayout(self)
        
        lbl_diag_titulo = QLabel("🎯 Diagnóstico Final:")
        lbl_diag_titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(lbl_diag_titulo)
        
        lbl_diag_texto = QLabel(diagnostico)
        if "CRÍTICO" in diagnostico:
            lbl_diag_texto.setStyleSheet("color: #ff7b72; font-size: 18px; font-weight: bold; padding: 15px; border: 2px solid #ff7b72; border-radius: 8px;")
        else:
            lbl_diag_texto.setStyleSheet("color: #3fb950; font-size: 18px; font-weight: bold; padding: 15px; border: 2px solid #3fb950; border-radius: 8px;")
        layout.addWidget(lbl_diag_texto)
        
        lbl_just_titulo = QLabel("🧠 Justificación del Razonamiento (LLM):")
        lbl_just_titulo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_just_titulo.setStyleSheet("margin-top: 20px;")
        layout.addWidget(lbl_just_titulo)
        
        txt_justificacion = QTextEdit()
        txt_justificacion.setReadOnly(True)
        txt_justificacion.setFont(QFont("Segoe UI", 12))
        txt_justificacion.setText(justificacion)
        layout.addWidget(txt_justificacion)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(120)
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)

# ==========================================
# VISTA PRINCIPAL (V)
# ==========================================

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.tema_oscuro = True
        self.aplicar_tema()
        self.init_ui()

    def aplicar_tema(self):
        # NOTA: Checkboxes rellenados de color vivo y botones con efecto de pulsado (:pressed)
        if self.tema_oscuro:
            style = """
                QMainWindow { background-color: #0d1117; }
                QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Arial, sans-serif; }
                
                /* Mejoras en los bordes de los grupos */
                QGroupBox { font-size: 16px; font-weight: bold; color: #58a6ff; border: 2px solid #30363d; border-radius: 12px; margin-top: 25px; padding: 25px 15px 15px 15px; }
                QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }
                
                /* Botones normales con efecto pulsado */
                QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 14px; }
                QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
                QPushButton:pressed { background-color: #161b22; border: 2px solid #58a6ff; }
                
                /* Botón Diagnóstico */
                QPushButton#btn_accion { background-color: #238636; color: white; border: 2px solid #2ea043; border-radius: 10px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion:hover { background-color: #2ea043; }
                QPushButton#btn_accion:pressed { background-color: #1c6b2a; border: 2px solid #ffffff; }
                
                /* Botón Hipótesis */
                QPushButton#btn_accion_hip { background-color: #1f6feb; color: white; border: 2px solid #388bfd; border-radius: 10px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion_hip:hover { background-color: #388bfd; }
                QPushButton#btn_accion_hip:pressed { background-color: #1158c7; border: 2px solid #ffffff; }
                
                /* Botón Peligro (Limpiar) */
                QPushButton#btn_peligro { background-color: transparent; color: #ff7b72; border: 2px solid #ff7b72; border-radius: 8px; }
                QPushButton#btn_peligro:hover { background-color: rgba(255, 123, 114, 0.15); }
                QPushButton#btn_peligro:pressed { background-color: rgba(255, 123, 114, 0.3); border-color: #d73a49; }
                
                /* Cajas de texto y listas con bordes redondeados */
                QLineEdit, QComboBox, QSpinBox { background-color: #161b22; color: #c9d1d9; border: 2px solid #30363d; padding: 10px; border-radius: 8px; font-size: 15px; }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #58a6ff; }
                
                QSpinBox::up-button { width: 35px; border-left: 2px solid #30363d; background-color: #21262d; border-top-right-radius: 6px; }
                QSpinBox::down-button { width: 35px; border-left: 2px solid #30363d; background-color: #21262d; border-bottom-right-radius: 6px; }
                
                /* Checkboxes - AHORA SE RELLENAN DE COLOR */
                QCheckBox { spacing: 12px; }
                QCheckBox::indicator { width: 22px; height: 22px; border: 2px solid #8b949e; border-radius: 6px; background-color: transparent; }
                QCheckBox::indicator:hover { border: 2px solid #58a6ff; }
                QCheckBox::indicator:checked { background-color: #1f6feb; border: 2px solid #58a6ff; }
                
                QListWidget { background-color: #010409; border: 2px solid #30363d; border-radius: 8px; padding: 10px; font-size: 14px; }
                QProgressBar { border: 2px solid #30363d; border-radius: 8px; text-align: center; background-color: #161b22; color: white; font-weight: bold; }
                QProgressBar::chunk { background-color: #1f6feb; border-radius: 4px; }
            """
        else:
            style = """
                QMainWindow { background-color: #ffffff; }
                QWidget { background-color: #ffffff; color: #24292e; font-family: 'Segoe UI', Arial, sans-serif; }
                
                /* Mejoras en los bordes de los grupos */
                QGroupBox { font-size: 16px; font-weight: bold; color: #0366d6; border: 2px solid #e1e4e8; border-radius: 12px; margin-top: 25px; padding: 25px 15px 15px 15px; }
                QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }
                
                /* Botones normales con efecto pulsado */
                QPushButton { background-color: #fafbfc; color: #24292e; border: 1px solid #e1e4e8; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 14px; }
                QPushButton:hover { background-color: #f3f4f6; border-color: #d1d5da; }
                QPushButton:pressed { background-color: #e1e4e8; border: 2px solid #0366d6; }
                
                /* Botón Diagnóstico */
                QPushButton#btn_accion { background-color: #2ea44f; color: white; border: 2px solid #34d058; border-radius: 10px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion:hover { background-color: #2c974b; }
                QPushButton#btn_accion:pressed { background-color: #22863a; border: 2px solid #000000; }
                
                /* Botón Hipótesis */
                QPushButton#btn_accion_hip { background-color: #0366d6; color: white; border: 2px solid #79b8ff; border-radius: 10px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion_hip:hover { background-color: #005cc5; }
                QPushButton#btn_accion_hip:pressed { background-color: #004ea5; border: 2px solid #000000; }
                
                /* Botón Peligro (Limpiar) */
                QPushButton#btn_peligro { background-color: transparent; color: #d73a49; border: 2px solid #d73a49; border-radius: 8px; }
                QPushButton#btn_peligro:hover { background-color: rgba(215, 58, 73, 0.1); }
                QPushButton#btn_peligro:pressed { background-color: rgba(215, 58, 73, 0.25); border-color: #cb2431; }
                
                /* Cajas de texto y listas con bordes redondeados */
                QLineEdit, QComboBox, QSpinBox { background-color: #fafbfc; color: #24292e; border: 2px solid #e1e4e8; padding: 10px; border-radius: 8px; font-size: 15px; }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #0366d6; }
                
                QSpinBox::up-button { width: 35px; border-left: 2px solid #e1e4e8; background-color: #f6f8fa; border-top-right-radius: 6px; }
                QSpinBox::down-button { width: 35px; border-left: 2px solid #e1e4e8; background-color: #f6f8fa; border-bottom-right-radius: 6px; }
                
                /* Checkboxes - AHORA SE RELLENAN DE COLOR */
                QCheckBox { spacing: 12px; }
                QCheckBox::indicator { width: 22px; height: 22px; border: 2px solid #959da5; border-radius: 6px; background-color: transparent; }
                QCheckBox::indicator:hover { border: 2px solid #0366d6; }
                QCheckBox::indicator:checked { background-color: #0366d6; border: 2px solid #005cc5; }
                
                QListWidget { background-color: #f6f8fa; border: 2px solid #e1e4e8; border-radius: 8px; padding: 10px; font-size: 14px; }
                QProgressBar { border: 2px solid #e1e4e8; border-radius: 8px; text-align: center; background-color: #fafbfc; color: #24292e; font-weight: bold; }
                QProgressBar::chunk { background-color: #0366d6; border-radius: 4px; }
            """
        QApplication.instance().setStyleSheet(style)

    def toggle_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.aplicar_tema()
        self.btn_tema.setText("☀️ Modo Claro" if self.tema_oscuro else "🌙 Modo Oscuro")

    def init_ui(self):
        self.setWindowTitle("Diagnóstico GitHub - ISSBC")
        self.setMinimumSize(950, 780) 

        container = QWidget()
        container.setObjectName("centralWidget")
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(25) # Más espacio para respirar entre componentes
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- CABECERA ---
        header_layout = QHBoxLayout()
        
        lbl_logo = QLabel()
        ruta_logo = os.path.join(os.path.dirname(__file__), 'github_logo.png')
        if os.path.exists(ruta_logo):
            pixmap = QPixmap(ruta_logo).scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pixmap)
        else:
            lbl_logo.setText("🐙")
            lbl_logo.setFont(QFont("Segoe UI", 48)) 

        lbl_titulo = QLabel("Panel de Diagnóstico de Repositorios")
        lbl_titulo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        self.btn_tema = QPushButton("☀️ Modo Claro")
        self.btn_tema.clicked.connect(self.toggle_tema)
        self.btn_tema.setFixedSize(160, 45) 

        header_layout.addWidget(lbl_logo)
        header_layout.addSpacing(15) 
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_tema)
        main_layout.addLayout(header_layout)

        # --- ENTRADA DE URL ---
        group_url = QGroupBox("🔗 Repositorio a Analizar")
        lay_url = QHBoxLayout(group_url)
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("Ej: https://github.com/usuario/repositorio")
        self.txt_url.setMinimumHeight(45) 
        lay_url.addWidget(self.txt_url)
        main_layout.addWidget(group_url)

        # --- PANEL CENTRAL DIVIDIDO ---
        panel_central = QHBoxLayout()
        panel_central.setSpacing(25)
        
        # Columna Izquierda: Síntomas
        group_obs = QGroupBox("📊 Métricas y Observables")
        obs_layout = QVBoxLayout(group_obs)
        
        form_cuant = QFormLayout()
        self.spin_dias = QSpinBox()
        self.spin_dias.setRange(0, 9999)
        self.spin_dias.setSuffix(" días")
        self.spin_dias.setMinimumHeight(45)
        
        lbl_inactividad = QLabel("⏳ Inactividad (commits):")
        lbl_inactividad.setFont(QFont("Segoe UI", 15))
        form_cuant.addRow(lbl_inactividad, self.spin_dias)
        
        self.chk_docs = QCheckBox("📚 Carencia grave de documentación")
        self.chk_docs.setFont(QFont("Segoe UI", 15))
        
        self.chk_toxico = QCheckBox("⚠️ Alertas de toxicidad en comunidad")
        self.chk_toxico.setFont(QFont("Segoe UI", 15))
        
        obs_layout.addLayout(form_cuant)
        obs_layout.addSpacing(20)
        obs_layout.addWidget(self.chk_docs)
        obs_layout.addSpacing(15)
        obs_layout.addWidget(self.chk_toxico)
        obs_layout.addStretch()
        
        panel_central.addWidget(group_obs, 1)

        # Columna Derecha: Base de Conocimiento
        group_config = QGroupBox("⚙️ Base de Conocimiento Local")
        lay_config = QVBoxLayout(group_config)
        
        combo_lay = QHBoxLayout()
        lbl_modo = QLabel("Modo:")
        lbl_modo.setFont(QFont("Segoe UI", 15))
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["🧠 Local (PDFs)", "🌐 Local + Web"])
        self.combo_modo.setMinimumHeight(45)
        combo_lay.addWidget(lbl_modo)
        combo_lay.addWidget(self.combo_modo, 1)
        
        self.lista_archivos = QListWidget()
        
        botones_pdf_lay = QHBoxLayout()
        btn_add_pdf = QPushButton("📂 Añadir PDF")
        btn_add_pdf.setMinimumHeight(45)
        btn_add_pdf.clicked.connect(self.importar_pdf)
        
        btn_borrar_pdf = QPushButton("🗑️ Limpiar")
        btn_borrar_pdf.setObjectName("btn_peligro")
        btn_borrar_pdf.setMinimumHeight(45)
        btn_borrar_pdf.clicked.connect(self.lista_archivos.clear)
        
        botones_pdf_lay.addWidget(btn_add_pdf)
        botones_pdf_lay.addWidget(btn_borrar_pdf)
        
        lay_config.addLayout(combo_lay)
        lay_config.addSpacing(10)
        lay_config.addWidget(self.lista_archivos)
        lay_config.addSpacing(10)
        lay_config.addLayout(botones_pdf_lay)
        
        panel_central.addWidget(group_config, 1)
        
        main_layout.addLayout(panel_central)

        # --- BARRA DE CARGA ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # --- BOTONES DE ACCIÓN ---
        actions_lay = QHBoxLayout()
        actions_lay.addStretch()
        
        self.btn_hip = QPushButton("🔍 Evaluar Hipótesis")
        self.btn_hip.setObjectName("btn_accion_hip")
        self.btn_hip.setFixedSize(280, 60) 
        
        self.btn_diag = QPushButton("⚙️ Generar Diagnóstico")
        self.btn_diag.setObjectName("btn_accion")
        self.btn_diag.setFixedSize(280, 60)
        
        actions_lay.addWidget(self.btn_hip)
        actions_lay.addSpacing(25)
        actions_lay.addWidget(self.btn_diag)
        actions_lay.addStretch()
        
        main_layout.addLayout(actions_lay)

        # Conexiones
        self.btn_hip.clicked.connect(lambda: self.iniciar_carga(self.mostrar_hipotesis))
        self.btn_diag.clicked.connect(lambda: self.iniciar_carga(self.mostrar_diagnostico))

    # --- LÓGICA DE LA INTERFAZ ---

    def iniciar_carga(self, callback_final):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_hip.setEnabled(False)
        self.btn_diag.setEnabled(False)
        
        self.carga_actual = 0
        self.callback_post_carga = callback_final

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_barra)
        self.timer.start(20)

    def actualizar_barra(self):
        self.carga_actual += 2
        self.progress_bar.setValue(self.carga_actual)
        
        if self.carga_actual >= 100:
            self.timer.stop()
            self.progress_bar.setVisible(False)
            self.btn_hip.setEnabled(True)
            self.btn_diag.setEnabled(True)
            self.callback_post_carga()

    def importar_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Manuales/Docs", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                self.controller.model.pdfs_locales.append(f)
                nombre_archivo = f.split("/")[-1] 
                self.lista_archivos.addItem(f"📄 {nombre_archivo}")

    def get_data(self):
        return {
            "url_repo": self.txt_url.text(),
            "falta_docs": self.chk_docs.isChecked(),
            "comentarios_toxicos": self.chk_toxico.isChecked(),
            "dias_sin_commits": self.spin_dias.value(),
            "modo": self.combo_modo.currentText()
        }

    def mostrar_hipotesis(self):
        self.controller.update_model(self.get_data())
        self.controller.generar_hipotesis()
        dialog = HipotesisDialog(self.controller.model.hipotesis, self)
        dialog.exec_()

    def mostrar_diagnostico(self):
        self.controller.update_model(self.get_data())
        self.controller.generar_diagnostico()
        dialog = DiagnosticoDialog(self.controller.model.diagnostico_final, self.controller.model.justificacion, self)
        dialog.exec_()
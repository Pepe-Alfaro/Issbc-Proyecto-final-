# vista/view.py
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton, 
                             QListWidget, QMessageBox, QFileDialog, QGroupBox, 
                             QDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTextEdit, QFormLayout, QApplication,
                             QLineEdit, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils.worker import Worker

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
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Hipótesis", "Probabilidad", "Estado", "Evidencia Detectada", "Acción Recomendada"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setRowCount(len(hipotesis_data))
        
        font_tabla = QFont("Segoe UI", 11)
        self.tabla.setFont(font_tabla)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("QTableWidget { border: none; }")
        
        for row, hip in enumerate(hipotesis_data):
            self.tabla.setItem(row, 0, QTableWidgetItem(hip.get("nombre", "")))
            self.tabla.setItem(row, 1, QTableWidgetItem(hip.get("probabilidad", "")))
            self.tabla.setItem(row, 2, QTableWidgetItem(hip.get("estado", "")))
            self.tabla.setItem(row, 3, QTableWidgetItem(hip.get("evidencia", "")))
            self.tabla.setItem(row, 4, QTableWidgetItem(hip.get("accion", "")))
            
        layout.addWidget(self.tabla)
        
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(120)
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.clicked.connect(self.accept)
        btn_lay.addWidget(btn_cerrar)
        layout.addLayout(btn_lay)


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
        
        self.lbl_diag_texto = QLabel(diagnostico)
        self.lbl_diag_texto.setWordWrap(True)
        if "CRÍTICO" in diagnostico or "DEFICIENTE" in diagnostico or "OBSOLETO" in diagnostico:
            self.lbl_diag_texto.setStyleSheet("color: #f85149; font-size: 18px; font-weight: bold; padding: 20px; border: 1px solid rgba(248,81,73,0.4); border-radius: 8px; background-color: rgba(248,81,73,0.1);")
        else:
            self.lbl_diag_texto.setStyleSheet("color: #2ea043; font-size: 18px; font-weight: bold; padding: 20px; border: 1px solid rgba(46,160,67,0.4); border-radius: 8px; background-color: rgba(46,160,67,0.1);")
        layout.addWidget(self.lbl_diag_texto)
        
        lbl_just_titulo = QLabel("🧠 Justificación del Razonamiento (IA & KADS):")
        lbl_just_titulo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_just_titulo.setStyleSheet("margin-top: 15px; color: #8b949e;")
        layout.addWidget(lbl_just_titulo)
        
        self.txt_justificacion = QTextEdit()
        self.txt_justificacion.setReadOnly(True)
        self.txt_justificacion.setFont(QFont("Segoe UI", 12))
        self.txt_justificacion.setText(justificacion)
        layout.addWidget(self.txt_justificacion)

        btn_lay = QHBoxLayout()
        btn_exportar = QPushButton("📄 Exportar Informe (MD)")
        btn_exportar.setFixedHeight(40)
        btn_exportar.clicked.connect(self.exportar_markdown)
        btn_lay.addWidget(btn_exportar)
        
        btn_lay.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(120)
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.clicked.connect(self.accept)
        btn_lay.addWidget(btn_cerrar)
        layout.addLayout(btn_lay)

    def exportar_markdown(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Informe", "informe_diagnostico.md", "Markdown (*.md)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("# Informe de Diagnóstico de Repositorio\n\n")
                    f.write(f"## 🎯 Veredicto\n**{self.lbl_diag_texto.text()}**\n\n")
                    f.write(f"## 🧠 Justificación\n{self.txt_justificacion.toPlainText()}\n")
                QMessageBox.information(self, "Exportación Exitosa", f"Informe guardado en:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")

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
        if self.tema_oscuro:
            style = """
                QMainWindow, QDialog { background-color: #0d1117; }
                QWidget { color: #c9d1d9; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
                
                QGroupBox { 
                    font-size: 15px; 
                    font-weight: 600; 
                    color: #58a6ff; 
                    border: 1px solid #30363d; 
                    border-radius: 12px; 
                    margin-top: 20px; 
                    padding: 20px 15px 15px 15px; 
                    background-color: #161b22;
                }
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    subcontrol-position: top left;
                    left: 20px; 
                    padding: 0 5px; 
                    background-color: #161b22;
                    border-radius: 4px;
                }
                
                QPushButton { 
                    background-color: #21262d; 
                    color: #c9d1d9; 
                    border: 1px solid #30363d; 
                    border-radius: 8px; 
                    padding: 8px 16px; 
                    font-weight: 600; 
                    font-size: 14px; 
                }
                QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
                QPushButton:pressed { background-color: #282e33; border-color: #58a6ff; }
                
                QPushButton#btn_accion { background-color: #238636; color: #ffffff; border: 1px solid rgba(240, 246, 252, 0.1); border-radius: 8px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion:hover { background-color: #2ea043; border-color: rgba(240, 246, 252, 0.1); }
                QPushButton#btn_accion:pressed { background-color: #238636; }
                
                QPushButton#btn_accion_hip { background-color: #1f6feb; color: #ffffff; border: 1px solid rgba(240, 246, 252, 0.1); border-radius: 8px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion_hip:hover { background-color: #388bfd; border-color: rgba(240, 246, 252, 0.1); }
                QPushButton#btn_accion_hip:pressed { background-color: #1f6feb; }
                
                QPushButton#btn_peligro { background-color: transparent; color: #f85149; border: 1px solid #30363d; }
                QPushButton#btn_peligro:hover { background-color: #da3633; color: white; border-color: #f85149; }
                
                QLineEdit, QComboBox, QSpinBox { 
                    background-color: #0d1117; 
                    color: #c9d1d9; 
                    border: 1px solid #30363d; 
                    padding: 10px 15px; 
                    border-radius: 6px; 
                    font-size: 14px; 
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #58a6ff; outline: none; }
                QComboBox::drop-down { border: none; width: 30px; }
                QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #8b949e; margin-right: 10px; }
                
                QListWidget { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 5px; font-size: 14px; outline: 0;}
                QListWidget::item { padding: 8px; border-radius: 4px; }
                QListWidget::item:hover { background-color: #161b22; }
                QListWidget::item:selected { background-color: #1f6feb; color: white; }
                
                QProgressBar { border: none; border-radius: 4px; background-color: #21262d; height: 8px; text-align: center; }
                QProgressBar::chunk { background-color: #238636; border-radius: 4px; }
                
                QTableWidget { background-color: #0d1117; alternate-background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; gridline-color: #30363d; }
                QHeaderView::section { background-color: #161b22; color: #8b949e; font-weight: bold; padding: 8px; border: none; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; }
                QTableWidget::item { padding: 5px; }
                
                QTextEdit { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 10px; color: #c9d1d9; }
            """
        else:
            style = """
                QMainWindow, QDialog { background-color: #f6f8fa; }
                QWidget { color: #24292f; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
                
                QGroupBox { 
                    font-size: 15px; 
                    font-weight: 600; 
                    color: #0969da; 
                    border: 1px solid #d0d7de; 
                    border-radius: 12px; 
                    margin-top: 20px; 
                    padding: 20px 15px 15px 15px; 
                    background-color: #ffffff;
                }
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    subcontrol-position: top left;
                    left: 20px; 
                    padding: 0 5px; 
                    background-color: #ffffff;
                    border-radius: 4px;
                }
                
                QPushButton { 
                    background-color: #f3f4f6; 
                    color: #24292f; 
                    border: 1px solid #d0d7de; 
                    border-radius: 8px; 
                    padding: 8px 16px; 
                    font-weight: 600; 
                    font-size: 14px; 
                }
                QPushButton:hover { background-color: #ebecf0; border-color: #babbbd; }
                QPushButton:pressed { background-color: #e2e4e8; border-color: #0969da; }
                
                QPushButton#btn_accion { background-color: #2da44e; color: #ffffff; border: 1px solid rgba(27, 31, 36, 0.15); border-radius: 8px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion:hover { background-color: #2c974b; border-color: rgba(27, 31, 36, 0.15); }
                QPushButton#btn_accion:pressed { background-color: #298e46; }
                
                QPushButton#btn_accion_hip { background-color: #0969da; color: #ffffff; border: 1px solid rgba(27, 31, 36, 0.15); border-radius: 8px; font-size: 16px; font-weight: bold; }
                QPushButton#btn_accion_hip:hover { background-color: #0a58ca; border-color: rgba(27, 31, 36, 0.15); }
                QPushButton#btn_accion_hip:pressed { background-color: #0950b3; }
                
                QPushButton#btn_peligro { background-color: transparent; color: #cf222e; border: 1px solid #d0d7de; }
                QPushButton#btn_peligro:hover { background-color: #a40e26; color: white; border-color: #a40e26; }
                
                QLineEdit, QComboBox, QSpinBox { 
                    background-color: #ffffff; 
                    color: #24292f; 
                    border: 1px solid #d0d7de; 
                    padding: 10px 15px; 
                    border-radius: 6px; 
                    font-size: 14px; 
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #0969da; outline: none; }
                QComboBox::drop-down { border: none; width: 30px; }
                QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #57606a; margin-right: 10px; }
                
                QListWidget { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 8px; padding: 5px; font-size: 14px; outline: 0;}
                QListWidget::item { padding: 8px; border-radius: 4px; }
                QListWidget::item:hover { background-color: #f6f8fa; }
                QListWidget::item:selected { background-color: #0969da; color: white; }
                
                QProgressBar { border: none; border-radius: 4px; background-color: #eaeef2; height: 8px; text-align: center; }
                QProgressBar::chunk { background-color: #2da44e; border-radius: 4px; }
                
                QTableWidget { background-color: #ffffff; alternate-background-color: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px; gridline-color: #d0d7de; }
                QHeaderView::section { background-color: #f6f8fa; color: #57606a; font-weight: bold; padding: 8px; border: none; border-right: 1px solid #d0d7de; border-bottom: 1px solid #d0d7de; }
                QTableWidget::item { padding: 5px; }
                
                QTextEdit { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 8px; padding: 10px; color: #24292f; }
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
        main_layout.setSpacing(25)
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
        
        self.lbl_rate_limit = QLabel("API Limits: -/-")
        self.lbl_rate_limit.setFont(QFont("Segoe UI", 12))
        self.lbl_rate_limit.setStyleSheet("color: #8b949e;")
        
        self.btn_tema = QPushButton("☀️ Modo Claro")
        self.btn_tema.clicked.connect(self.toggle_tema)
        self.btn_tema.setFixedSize(160, 45) 

        header_layout.addWidget(lbl_logo)
        header_layout.addSpacing(15) 
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_rate_limit)
        header_layout.addSpacing(15)
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
        
        # Columna Izquierda: Síntomas y Métricas
        group_obs = QGroupBox("📊 Métricas y Observables")
        obs_layout = QVBoxLayout(group_obs)
        
        form_cuant = QFormLayout()
        
        # 1. Días de Inactividad
        self.lbl_val_dias = QLabel("-")
        self.lbl_val_dias.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_inactividad = QLabel("⏳ Inactividad (commits):")
        lbl_inactividad.setFont(QFont("Segoe UI", 14))
        lbl_inactividad.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_inactividad, self.lbl_val_dias)

        # 2. Issues Abiertas
        self.lbl_val_issues = QLabel("-")
        self.lbl_val_issues.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_issues = QLabel("🐛 Issues Abiertas:")
        lbl_issues.setFont(QFont("Segoe UI", 14))
        lbl_issues.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_issues, self.lbl_val_issues)

        # 3. Estrellas
        self.lbl_val_estrellas = QLabel("-")
        self.lbl_val_estrellas.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_estrellas = QLabel("⭐ Estrellas:")
        lbl_estrellas.setFont(QFont("Segoe UI", 14))
        lbl_estrellas.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_estrellas, self.lbl_val_estrellas)
        
        # 4. Documentación
        self.lbl_val_docs = QLabel("-")
        self.lbl_val_docs.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_docs = QLabel("📚 Carencia grave docs:")
        lbl_docs.setFont(QFont("Segoe UI", 14))
        lbl_docs.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_docs, self.lbl_val_docs)
        
        # 5. Toxicidad
        self.lbl_val_toxico = QLabel("-")
        self.lbl_val_toxico.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_toxico = QLabel("⚠️ Toxicidad en comunidad:")
        lbl_toxico.setFont(QFont("Segoe UI", 14))
        lbl_toxico.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_toxico, self.lbl_val_toxico)
        
        # 6. Forks
        self.lbl_val_forks = QLabel("-")
        self.lbl_val_forks.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_forks = QLabel("🍴 Forks:")
        lbl_forks.setFont(QFont("Segoe UI", 14))
        lbl_forks.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_forks, self.lbl_val_forks)

        # 7. PRs
        self.lbl_val_prs = QLabel("-")
        self.lbl_val_prs.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_prs = QLabel("🔄 PRs Abiertas:")
        lbl_prs.setFont(QFont("Segoe UI", 14))
        lbl_prs.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_prs, self.lbl_val_prs)

        # 8. Contribuyentes
        self.lbl_val_contrib = QLabel("-")
        self.lbl_val_contrib.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_contrib = QLabel("👥 Contribuyentes:")
        lbl_contrib.setFont(QFont("Segoe UI", 14))
        lbl_contrib.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_contrib, self.lbl_val_contrib)

        # 9. Licencia
        self.lbl_val_licencia = QLabel("-")
        self.lbl_val_licencia.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_licencia = QLabel("⚖️ Licencia:")
        lbl_licencia.setFont(QFont("Segoe UI", 14))
        lbl_licencia.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_licencia, self.lbl_val_licencia)

        # 10. Lenguaje
        self.lbl_val_lenguaje = QLabel("-")
        self.lbl_val_lenguaje.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl_lenguaje = QLabel("💻 Lenguaje:")
        lbl_lenguaje.setFont(QFont("Segoe UI", 14))
        lbl_lenguaje.setStyleSheet("color: #8b949e;")
        form_cuant.addRow(lbl_lenguaje, self.lbl_val_lenguaje)
        
        obs_layout.addLayout(form_cuant)
        
        lbl_commits = QLabel("🕒 Últimos Commits:")
        lbl_commits.setFont(QFont("Segoe UI", 14))
        lbl_commits.setStyleSheet("color: #8b949e; margin-top: 10px;")
        obs_layout.addWidget(lbl_commits)
        
        self.lista_commits = QListWidget()
        self.lista_commits.setFixedHeight(100)
        obs_layout.addWidget(self.lista_commits)
        
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

        combo_motor_lay = QHBoxLayout()
        lbl_motor = QLabel("Motor:")
        lbl_motor.setFont(QFont("Segoe UI", 15))
        self.combo_motor = QComboBox()
        self.combo_motor.addItems(["📊 CommonKADS", "🧠 Ollama (IA)"])
        self.combo_motor.setMinimumHeight(45)
        combo_motor_lay.addWidget(lbl_motor)
        combo_motor_lay.addWidget(self.combo_motor, 1)
        
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
        lay_config.addLayout(combo_motor_lay)
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
        self.btn_hip.clicked.connect(self.generar_hipotesis_async)
        self.btn_diag.clicked.connect(self.generar_diagnostico_async)

    # --- LÓGICA DE LA INTERFAZ ---

    def generar_hipotesis_async(self):
        self.btn_hip.setEnabled(False)
        self.btn_diag.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.controller.update_model(self.get_data())
        self.worker = Worker(self.controller.generar_hipotesis)
        self.worker.finished.connect(self.mostrar_hipotesis_terminado)
        self.worker.start()

    def mostrar_hipotesis_terminado(self, result):
        self.btn_hip.setEnabled(True)
        self.btn_diag.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        
        self.actualizar_vista_desde_modelo()
        dialog = HipotesisDialog(self.controller.model.hipotesis, self)
        dialog.exec_()

    def generar_diagnostico_async(self):
        self.btn_hip.setEnabled(False)
        self.btn_diag.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.controller.update_model(self.get_data())
        self.worker = Worker(self.controller.generar_diagnostico)
        self.worker.finished.connect(self.mostrar_diagnostico_terminado)
        self.worker.start()

    def mostrar_diagnostico_terminado(self, result):
        self.btn_hip.setEnabled(True)
        self.btn_diag.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        
        self.actualizar_vista_desde_modelo()
        dialog = DiagnosticoDialog(self.controller.model.diagnostico_final, self.controller.model.justificacion, self)
        dialog.exec_()

    def importar_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Manuales/Docs", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                self.controller.model.pdfs_locales.append(f)
                nombre_archivo = f.split("/")[-1] 
                self.lista_archivos.addItem(f"📄 {nombre_archivo}")

    def get_data(self):
        # NOTA: Solo recogemos la URL y el modo. Las métricas ahora son puramente informativas
        # y se extraen exclusivamente mediante GitHubService en el controlador.
        return {
            "url_repo": self.txt_url.text(),
            "modo": self.combo_modo.currentText(),
            "motor": self.combo_motor.currentText()
        }

    def mostrar_hipotesis(self):
        self.controller.update_model(self.get_data())
        self.controller.generar_hipotesis()
        
        # Opcional: Actualizar la vista visualmente con los datos extraídos por GitHub
        self.actualizar_vista_desde_modelo()
        
        dialog = HipotesisDialog(self.controller.model.hipotesis, self)
        dialog.exec_()

    def mostrar_diagnostico(self):
        self.controller.update_model(self.get_data())
        self.controller.generar_diagnostico()
        
        # Opcional: Actualizar la vista visualmente con los datos extraídos por GitHub
        self.actualizar_vista_desde_modelo()
        
        dialog = DiagnosticoDialog(self.controller.model.diagnostico_final, self.controller.model.justificacion, self)
        dialog.exec_()

    def actualizar_vista_desde_modelo(self):
        """Si introducimos una URL, GitHub sobrescribe los datos. Esta función actualiza la UI para que el usuario los vea."""
        obs = self.controller.model.observables
        if "dias_sin_commits" in obs:
            self.lbl_val_dias.setText(f"{obs['dias_sin_commits']} días")
        if "issues_abiertas" in obs:
            self.lbl_val_issues.setText(str(obs["issues_abiertas"]))
        if "estrellas" in obs:
            self.lbl_val_estrellas.setText(str(obs["estrellas"]))
        if "falta_docs" in obs:
            self.lbl_val_docs.setText("⚠️ Sí" if obs["falta_docs"] else "✅ No")
        if "comentarios_toxicos" in obs:
            self.lbl_val_toxico.setText("🚨 Sí" if obs["comentarios_toxicos"] else "✅ No")
        if "forks" in obs:
            self.lbl_val_forks.setText(str(obs["forks"]))
        if "prs_abiertas" in obs:
            self.lbl_val_prs.setText(str(obs["prs_abiertas"]))
        if "contribuyentes" in obs:
            self.lbl_val_contrib.setText(str(obs["contribuyentes"]))
        if "tiene_licencia" in obs:
            self.lbl_val_licencia.setText("✅ Sí" if obs["tiene_licencia"] else "❌ No")
        if "lenguaje" in obs:
            self.lbl_val_lenguaje.setText(str(obs["lenguaje"]))
        if "rate_limit_info" in obs:
            self.lbl_rate_limit.setText(f"API Limits: {obs['rate_limit_info']}")
        if "ultimos_commits" in obs:
            self.lista_commits.clear()
            for commit in obs["ultimos_commits"]:
                self.lista_commits.addItem(commit)
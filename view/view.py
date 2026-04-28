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
        style = """
            QMainWindow, QDialog, QWidget#centralWidget { background-color: #0f0f11; }
            QWidget { color: #a1a1aa; font-family: 'Inter', 'Segoe UI', sans-serif; }
            
            QFrame#darkPanel { 
                background-color: #151517; 
                border: 1px solid #27272a; 
                border-radius: 8px; 
            }
            
            QFrame#metricCard {
                background-color: #101012; 
                border: 1px solid #27272a; 
                border-radius: 6px; 
            }
            
            QLabel { color: #a1a1aa; }
            QLabel#metricTitle { font-size: 12px; color: #71717a; }
            QLabel#metricValue { font-size: 16px; font-weight: bold; color: #ffffff; }
            
            QLineEdit { 
                background-color: #151517; 
                color: #ffffff; 
                border: 1px solid #27272a; 
                padding: 12px 15px; 
                border-radius: 6px; 
                font-size: 14px; 
            }
            QLineEdit:focus { border: 1px solid #3b82f6; }
            
            QPushButton#btn_icon {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton#btn_icon:hover { background-color: #27272a; border-radius: 4px; }
            
            QPushButton#btn_flat {
                background-color: #151517;
                color: #e4e4e7;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton#btn_flat:hover { background-color: #27272a; }
            
            QComboBox#flatCombo {
                background-color: transparent;
                color: #a1a1aa;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                min-height: 28px;
            }
            QComboBox#flatCombo:hover { border-color: #3f3f46; color: #ffffff; }
            QComboBox#flatCombo::drop-down { border: none; width: 20px; }
            QComboBox#flatCombo::down-arrow { 
                image: none; border-left: 4px solid transparent; 
                border-right: 4px solid transparent; border-top: 4px solid #71717a; 
            }
            QComboBox QAbstractItemView {
                background-color: #151517;
                color: #ffffff;
                border: 1px solid #27272a;
                selection-background-color: #27272a;
            }
            
            QListWidget#commitsList {
                background-color: transparent;
                border: 1px dashed #27272a;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-style: italic;
                color: #71717a;
            }
            QListWidget#logsArea {
                background-color: #0f0f11;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #a1a1aa;
            }
            
            QPushButton#btn_accion_hip { 
                background-color: #2563eb; 
                color: #ffffff; 
                border: none; 
                border-radius: 6px; 
                font-size: 13px; 
                font-weight: 600; 
                padding: 10px 20px;
            }
            QPushButton#btn_accion_hip:hover { background-color: #1d4ed8; }
            
            QPushButton#btn_accion { 
                background-color: #10b981; 
                color: #ffffff; 
                border: none; 
                border-radius: 6px; 
                font-size: 13px; 
                font-weight: 600; 
                padding: 10px 20px;
            }
            QPushButton#btn_accion:hover { background-color: #059669; }
            
            QProgressBar {
                border: none;
                background-color: #27272a;
                height: 4px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 2px;
            }
            
            QTableWidget { 
                background-color: #0f0f11; 
                alternate-background-color: #151517; 
                border: 1px solid #27272a; 
                border-radius: 8px; 
                gridline-color: #27272a; 
            }
            QHeaderView::section { 
                background-color: #151517; 
                color: #a1a1aa; 
                font-weight: 600; 
                padding: 12px; 
                border: none; 
                border-right: 1px solid #27272a; 
                border-bottom: 1px solid #27272a; 
            }
            QTableWidget::item { padding: 12px; }
            
            QTextEdit { 
                background-color: #0f0f11; 
                border: 1px solid #27272a; 
                border-radius: 8px; 
                padding: 16px; 
                color: #e4e4e7; 
                font-size: 14px;
            }
        """
        QApplication.instance().setStyleSheet(style)

    def toggle_tema(self):
        # En este diseño ignoramos el modo claro, siempre es oscuro, pero mantenemos el toggle para simular funcionalidad
        pass

    def init_ui(self):
        from PyQt5.QtWidgets import QFrame, QGridLayout
        
        self.setWindowTitle("RepoDiagnostic")
        self.setMinimumSize(1050, 780) 

        container = QWidget()
        container.setObjectName("centralWidget")
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        lbl_titulo = QLabel("RepoDiagnostic")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #ffffff;")
        
        self.lbl_rate_limit = QLabel("API Limits: -/-")
        self.lbl_rate_limit.setFont(QFont("Segoe UI", 11))
        
        self.btn_tema = QPushButton("☀️")
        self.btn_tema.setObjectName("btn_icon")
        self.btn_tema.setFixedSize(32, 32)
        self.btn_tema.clicked.connect(self.toggle_tema)

        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_rate_limit)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.btn_tema)
        main_layout.addLayout(header_layout)

        # Separator line
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("background-color: #27272a;")
        main_layout.addWidget(line1)

        # --- URL INPUT ---
        lay_url = QVBoxLayout()
        lbl_url = QLabel("Repositorio a Analizar")
        lbl_url.setFont(QFont("Segoe UI", 12))
        lbl_url.setStyleSheet("color: #a1a1aa; font-weight: 500;")
        lay_url.addWidget(lbl_url)
        
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("🔍 https://github.com/usuario/repositorio")
        self.txt_url.setMinimumHeight(45)
        lay_url.addWidget(self.txt_url)
        lay_url.addSpacing(10)
        main_layout.addLayout(lay_url)

        # --- CENTRAL SPLIT ---
        panel_central = QHBoxLayout()
        panel_central.setSpacing(20)
        
        # LEFT PANEL: Metrics
        group_obs = QFrame()
        group_obs.setObjectName("darkPanel")
        obs_layout = QVBoxLayout(group_obs)
        obs_layout.setContentsMargins(20, 20, 20, 20)
        
        hdr_metrics = QHBoxLayout()
        lbl_metrics = QLabel("📊 Métricas y Observables")
        lbl_metrics.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_metrics.setStyleSheet("color: #e4e4e7;")
        hdr_metrics.addWidget(lbl_metrics)
        hdr_metrics.addStretch()
        obs_layout.addLayout(hdr_metrics)
        
        obs_layout.addSpacing(20)
        
        form_cuant = QFormLayout()
        form_cuant.setSpacing(20)
        
        self.metric_labels = {}
        metrics_def = [
            ("dias", "⏳ Inactividad (commits):"),
            ("issues", "🐛 Issues Abiertas:"),
            ("estrellas", "⭐ Estrellas:"),
            ("docs", "📚 Carencia grave docs:"),
            ("toxico", "⚠️ Toxicidad en comunidad:"),
            ("forks", "🍴 Forks:"),
            ("prs", "🔄 PRs Abiertas:"),
            ("contrib", "👥 Contribuyentes:"),
            ("licencia", "⚖️ Licencia:"),
            ("lenguaje", "💻 Lenguaje:")
        ]
        
        for key, title in metrics_def:
            lbl_t = QLabel(title)
            lbl_t.setFont(QFont("Segoe UI", 14))
            lbl_t.setStyleSheet("color: #a1a1aa;")
            
            lbl_v = QLabel("-")
            lbl_v.setFont(QFont("Segoe UI", 16, QFont.Bold))
            lbl_v.setStyleSheet("color: #ffffff;")
            
            form_cuant.addRow(lbl_t, lbl_v)
            self.metric_labels[key] = lbl_v

        obs_layout.addLayout(form_cuant)
        
        lbl_commits = QLabel("🕒 Últimos Commits")
        lbl_commits.setFont(QFont("Segoe UI", 14))
        lbl_commits.setStyleSheet("color: #a1a1aa;")
        obs_layout.addWidget(lbl_commits)
        
        self.lista_commits = QListWidget()
        self.lista_commits.setObjectName("commitsList")
        self.lista_commits.setMinimumHeight(150)
        self.lista_commits.addItem("Esperando análisis...")
        obs_layout.addWidget(self.lista_commits)
        
        panel_central.addWidget(group_obs, 1)

        # RIGHT PANEL: Local Knowledge
        group_config = QFrame()
        group_config.setObjectName("darkPanel")
        lay_config = QVBoxLayout(group_config)
        lay_config.setContentsMargins(20, 20, 20, 20)
        
        hdr_lk = QHBoxLayout()
        lbl_lk = QLabel("Base de Conocimiento Local")
        lbl_lk.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_lk.setStyleSheet("color: #e4e4e7;")
        hdr_lk.addWidget(lbl_lk)
        hdr_lk.addStretch()
        
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["🧠 Local (PDFs)", "🌐 Local + Web"])
        self.combo_modo.setObjectName("flatCombo")
        
        self.combo_motor = QComboBox()
        self.combo_motor.addItems(["📊 CommonKADS", "🧠 Ollama (IA)"])
        self.combo_motor.setObjectName("flatCombo")
        self.combo_motor.currentIndexChanged.connect(self.toggle_ollama_options)
        
        self.combo_ollama_modelos = QComboBox()
        self.combo_ollama_modelos.setObjectName("flatCombo")
        self.combo_ollama_modelos.setVisible(False)
        try:
            import ollama
            modelos_raw = ollama.list()
            modelos_nombres = [m['model'] for m in modelos_raw.get('models', [])]
            if modelos_nombres:
                self.combo_ollama_modelos.addItems(modelos_nombres)
            else:
                self.combo_ollama_modelos.addItem("phi3:mini")
        except:
            self.combo_ollama_modelos.addItem("phi3:mini")
            
        hdr_lk.addWidget(self.combo_modo)
        hdr_lk.addWidget(self.combo_motor)
        hdr_lk.addWidget(self.combo_ollama_modelos)
        lay_config.addLayout(hdr_lk)
        
        lay_config.addSpacing(15)
        
        self.lista_archivos = QListWidget()
        self.lista_archivos.setObjectName("logsArea")
        self.lista_archivos.addItem("Logs y análisis detallado aparecerán aquí...")
        lay_config.addWidget(self.lista_archivos)
        
        lay_config.addSpacing(15)
        
        botones_pdf_lay = QHBoxLayout()
        botones_pdf_lay.addStretch()
        
        self.btn_borrar_pdf = QPushButton("🗑️ Limpiar")
        self.btn_borrar_pdf.setObjectName("btn_flat")
        self.btn_borrar_pdf.clicked.connect(self.lista_archivos.clear)
        
        self.btn_add_pdf = QPushButton("📄 Añadir PDF")
        self.btn_add_pdf.setObjectName("btn_flat")
        self.btn_add_pdf.clicked.connect(self.importar_pdf)
        
        botones_pdf_lay.addWidget(self.btn_borrar_pdf)
        botones_pdf_lay.addWidget(self.btn_add_pdf)
        lay_config.addLayout(botones_pdf_lay)
        
        panel_central.addWidget(group_config, 1)
        
        main_layout.addLayout(panel_central)

        # Separator line bottom
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background-color: #27272a; margin-top: 10px;")
        main_layout.addWidget(line2)

        # --- BOTTOM BAR ---
        bottom_lay = QHBoxLayout()
        bottom_lay.setContentsMargins(0, 10, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumWidth(300)
        
        bottom_lay.addWidget(self.progress_bar)
        bottom_lay.addStretch()
        
        self.btn_hip = QPushButton("Evaluar Hipótesis")
        self.btn_hip.setObjectName("btn_accion_hip")
        
        self.btn_diag = QPushButton("Generar Diagnóstico")
        self.btn_diag.setObjectName("btn_accion")
        
        bottom_lay.addWidget(self.btn_hip)
        bottom_lay.addWidget(self.btn_diag)
        
        main_layout.addLayout(bottom_lay)

        # Conexiones
        self.btn_hip.clicked.connect(self.generar_hipotesis_async)
        self.btn_diag.clicked.connect(self.generar_diagnostico_async)

        # Configuración inicial
        self.toggle_ollama_options()

    # --- LÓGICA DE LA INTERFAZ ---
    def toggle_ollama_options(self):
        es_ollama = "Ollama" in self.combo_motor.currentText()
        self.combo_ollama_modelos.setVisible(es_ollama)

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
        from PyQt5.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Manuales/Docs", "", "PDF Files (*.pdf)")
        if files:
            if not hasattr(self.controller.model, "pdfs_locales"):
                self.controller.model.pdfs_locales = []
            if self.lista_archivos.item(0) and "aparecerán aquí" in self.lista_archivos.item(0).text():
                self.lista_archivos.clear()
            for f in files:
                self.controller.model.pdfs_locales.append(f)
                nombre_archivo = f.split("/")[-1] 
                self.lista_archivos.addItem(f"📄 {nombre_archivo}")

    def get_data(self):
        return {
            "url_repo": self.txt_url.text(),
            "modo": self.combo_modo.currentText(),
            "motor": self.combo_motor.currentText(),
            "modelo_ollama": self.combo_ollama_modelos.currentText()
        }

    def actualizar_vista_desde_modelo(self):
        obs = self.controller.model.observables
        labels = self.metric_labels
        
        if "dias_sin_commits" in obs:
            labels["dias"].setText(f"{obs['dias_sin_commits']} días")
        if "issues_abiertas" in obs:
            labels["issues"].setText(str(obs["issues_abiertas"]))
        if "estrellas" in obs:
            labels["estrellas"].setText(str(obs["estrellas"]))
        if "falta_docs" in obs:
            labels["docs"].setText("⚠️ Sí" if obs["falta_docs"] else "✅ No")
        if "comentarios_toxicos" in obs:
            labels["toxico"].setText("🚨 Sí" if obs["comentarios_toxicos"] else "✅ No")
        if "forks" in obs:
            labels["forks"].setText(str(obs["forks"]))
        if "prs_abiertas" in obs:
            labels["prs"].setText(str(obs["prs_abiertas"]))
        if "contribuyentes" in obs:
            labels["contrib"].setText(str(obs["contribuyentes"]))
        if "tiene_licencia" in obs:
            labels["licencia"].setText("✅ Sí" if obs["tiene_licencia"] else "❌ No")
        if "lenguaje" in obs:
            labels["lenguaje"].setText(str(obs["lenguaje"]))
            
        if "rate_limit_info" in obs:
            self.lbl_rate_limit.setText(f"API Limits: {obs['rate_limit_info']}")
            
        if "ultimos_commits" in obs:
            self.lista_commits.clear()
            for commit in obs["ultimos_commits"]:
                self.lista_commits.addItem(commit)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog,
                            QProgressBar, QTableWidget, QTableWidgetItem, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import sys
import pandas as pd
import back

class AutomationWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, excel_path, competencia):
        super().__init__()
        self.excel_path = excel_path
        self.competencia = competencia

    def run(self):
        try:
            # Chamar a função de automação do back.py
            back.run_automation(self.excel_path, self.competencia, self.progress, self.status)
        finally:
            self.finished.emit()

class NFEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação B/PALMA")
        self.setMinimumSize(800, 600)
        self.excel_path = None

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Header
        header = QLabel("Automação de emissão NF-e Vinhedo")
        header.setObjectName("header")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # File selection area
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)

        self.file_label = QLabel("Nenhum arquivo selecionado")
        self.file_label.setObjectName("fileLabel")
        select_file_btn = QPushButton("Selecionar Planilha")
        select_file_btn.clicked.connect(self.select_file)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_file_btn)
        layout.addWidget(file_widget)

        # Competencia input area
        competencia_widget = QWidget()
        competencia_layout = QHBoxLayout(competencia_widget)

        competencia_label = QLabel("Competência:")
        self.competencia_input = QLineEdit()
        self.competencia_input.setPlaceholderText("Digite a competência")

        competencia_layout.addWidget(competencia_label)
        competencia_layout.addWidget(self.competencia_input)
        layout.addWidget(competencia_widget)

        # Progress area
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.status_label = QLabel("Aguardando início...")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        # Table for showing data
        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        layout.addWidget(self.table)

        # Control buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)

        self.start_btn = QPushButton("Iniciar Automação")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_automation)

        self.stop_btn = QPushButton("Parar")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_automation)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addWidget(button_widget)

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }

            #header {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }

            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:disabled {
                background-color: #bdc3c7;
            }

            #fileLabel {
                padding: 10px;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }

            #progressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }

            #progressBar::chunk {
                background-color: #2ecc71;
            }

            #statusLabel {
                color: #7f8c8d;
                padding: 10px;
            }

            #dataTable {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: none;
            }
        """)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Planilha Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.excel_path = file_path
            self.file_label.setText(file_path.split('/')[-1])
            self.start_btn.setEnabled(True)
            self.load_data()

    def load_data(self):
        try:
            df = pd.read_excel(self.excel_path)
            self.table.setRowCount(len(df))
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(df.columns)

            for i in range(len(df)):
                for j in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[i, j]))
                    self.table.setItem(i, j, item)

            self.table.resizeColumnsToContents()

        except Exception as e:
            self.status_label.setText(f"Erro ao carregar arquivo: {str(e)}")

    def start_automation(self):
        competencia = self.competencia_input.text()
        self.worker = AutomationWorker(self.excel_path, competencia)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self.automation_finished)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.worker.start()

    def stop_automation(self):
        if hasattr(self, 'worker'):
            self.worker.terminate()
            self.worker.wait()
            self.automation_finished()

    def automation_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Automação finalizada")
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    window = NFEWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

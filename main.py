import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, 
    QWidget, QLabel, QComboBox, QLineEdit, QMessageBox, QTableView, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class DataFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Filter Application")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.file_label = QLabel("Select a file format:")
        self.layout.addWidget(self.file_label)

        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems(["CSV", "JSON", "Parquet"])
        self.layout.addWidget(self.file_format_combo)

        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.file_button)

        self.filter_label = QLabel("Enter filter criteria (e.g., column > value):")
        self.layout.addWidget(self.filter_label)

        self.filter_input = QLineEdit()
        self.layout.addWidget(self.filter_input)

        self.add_filter_button = QPushButton("Add Filter")
        self.add_filter_button.clicked.connect(self.add_filter)
        self.layout.addWidget(self.add_filter_button)

        self.apply_filter_button = QPushButton("Apply Filters")
        self.apply_filter_button.clicked.connect(self.apply_filters)
        self.layout.addWidget(self.apply_filter_button)

        self.save_button = QPushButton("Save Filtered Data")
        self.save_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_button)

        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.data = None
        self.file_path = None
        self.filters = []

    def load_file(self):
        file_format = self.file_format_combo.currentText().lower()
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choose File", "", f"{file_format.upper()} Files (*.{file_format});;All Files (*)", options=options)
        if self.file_path:
            if file_format == 'csv':
                self.data = pd.read_csv(self.file_path)
            elif file_format == 'json':
                self.data = pd.read_json(self.file_path)
            elif file_format == 'parquet':
                self.data = pd.read_parquet(self.file_path)
            self.display_data(self.data)

    def display_data(self, data):
        model = QStandardItemModel(data.shape[0], data.shape[1])
        model.setHorizontalHeaderLabels(data.columns)

        for row in range(data.shape[0]):
            for column in range(data.shape[1]):
                item = QStandardItem(str(data.iat[row, column]))
                model.setItem(row, column, item)

        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_filter(self):
        filter_criteria = self.filter_input.text()
        if filter_criteria:
            self.filters.append(filter_criteria)
            self.filter_input.clear()
            self.filter_label.setText(f"Current Filters: {', '.join(self.filters)}")

    def apply_filters(self):
        if self.data is not None:
            try:
                filtered_data = self.data.copy()
                for f in self.filters:
                    filtered_data = filtered_data.query(f)
                self.display_data(filtered_data)
                self.filtered_data = filtered_data
                self.result_label.setText(f"Filters applied successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply filters: {e}")
        else:
            QMessageBox.critical(self, "Error", "No data loaded to filter")

    def save_file(self):
        if hasattr(self, 'filtered_data'):
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;JSON Files (*.json);;Parquet Files (*.parquet)", options=options)
            if save_path:
                try:
                    if save_path.endswith('.csv'):
                        self.filtered_data.to_csv(save_path, index=False)
                    elif save_path.endswith('.json'):
                        self.filtered_data.to_json(save_path, orient='records', lines=True)
                    elif save_path.endswith('.parquet'):
                        self.filtered_data.to_parquet(save_path, index=False)
                    QMessageBox.information(self, "Success", f"File saved successfully: {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            QMessageBox.critical(self, "Error", "No filtered data to save")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DataFilterApp()
    mainWin.show()
    sys.exit(app.exec_())

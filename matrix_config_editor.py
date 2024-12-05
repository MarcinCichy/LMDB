from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import json

CONFIG_FILE = "matrix_config.json"


def load_matrix_config():
    """Wczytuje konfigurację matryc z pliku JSON."""
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Błąd wczytywania konfiguracji matryc: {e}")
        return {}


def save_matrix_config(config):
    """Zapisuje konfigurację matryc do pliku JSON."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
            print(f"Zapisano konfigurację matryc w {CONFIG_FILE}")
    except Exception as e:
        print(f"Błąd zapisu konfiguracji matryc: {e}")


class MatrixConfigEditor(QDialog):
    """Okno przypisywania matryc do grubości materiału."""
    def __init__(self, grubosci, matryce, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Przypisz Matryce")
        self.grubosci = grubosci
        self.matryce = matryce
        self.config = load_matrix_config()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabela konfiguracji
        self.table = QTableWidget(len(self.grubosci), len(self.matryce))
        self.table.setHorizontalHeaderLabels([str(m) for m in self.matryce])
        self.table.setVerticalHeaderLabels([str(g) for g in self.grubosci])

        # Wypełnienie tabeli
        for row, grubosc in enumerate(self.grubosci):
            for col, matryca in enumerate(self.matryce):
                item = QTableWidgetItem()
                item.setCheckState(Qt.Checked if str(grubosc) in self.config and matryca in self.config[str(grubosc)] else Qt.Unchecked)
                self.table.setItem(row, col, item)

        # Automatyczne dopasowanie szerokości kolumn
        self.table.resizeColumnsToContents()

        # Obliczenie całkowitej szerokości okna na podstawie szerokości kolumn
        total_column_width = sum(self.table.columnWidth(col) for col in range(self.table.columnCount()))
        total_column_width += self.table.verticalHeader().width()  # Dodaj szerokość nagłówka wierszy
        total_column_width += 40  # Margines na przewijanie (więcej dla większej tabeli)

        # Obliczenie całkowitej wysokości okna na podstawie liczby wierszy
        row_height = self.table.rowHeight(0) if self.table.rowCount() > 0 else 30  # Przybliżona wysokość wiersza
        header_height = self.table.horizontalHeader().height()  # Wysokość nagłówka kolumn
        total_height = header_height + (row_height * len(self.grubosci)) + 60  # Dodanie wysokości na przyciski i marginesy

        # Ustawienie większych rozmiarów okna
        self.resize(total_column_width, total_height)

        layout.addWidget(self.table)

        # Przycisk Zapisz
        save_button = QPushButton("Zapisz")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_config(self):
        """Zapisuje nową konfigurację."""
        new_config = {}
        for row, grubosc in enumerate(self.grubosci):
            selected_matryce = []
            for col, matryca in enumerate(self.matryce):
                item = self.table.item(row, col)
                if item and item.checkState() == Qt.Checked:
                    selected_matryce.append(matryca)
            new_config[str(grubosc)] = selected_matryce

        save_matrix_config(new_config)
        QMessageBox.information(self, "Sukces", "Konfiguracja matryc została zapisana.")
        self.accept()


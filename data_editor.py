from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon
import pandas as pd
from data_loader import save_data_to_json
from utils import parse_decimal_input


def safe_to_numeric(value):
    """Bezpieczna konwersja wartości na liczbę dziesiętną."""
    try:
        # Najpierw zamień przecinki na kropki
        value = parse_decimal_input(value)
        return pd.to_numeric(value)
    except ValueError:
        return value  # Jeśli nie można przekonwertować, zwróć oryginalną wartość


DATA_FILE = 'Ubytki.xlsx'


class DataEditorDialog(QDialog):
    """Okno dialogowe do edycji danych."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edycja Danych Treningowych")
        self.data = data.copy()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabela danych
        self.table = QTableWidget(len(self.data), len(self.data.columns))
        self.table.setHorizontalHeaderLabels(self.data.columns)

        for row, (_, row_data) in enumerate(self.data.iterrows()):
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

        # Automatyczne dopasowanie szerokości kolumn
        self.table.resizeColumnsToContents()

        # Dopasowanie szerokości okna do kolumn
        total_column_width = sum(self.table.columnWidth(col) for col in range(self.table.columnCount()))
        total_column_width += self.table.verticalHeader().width()  # Uwzględnij szerokość nagłówka wierszy
        total_column_width += 20  # Dodanie marginesu dla przewijania

        # Ustawienie minimalnej wysokości okna dla 15 wierszy
        row_height = self.table.rowHeight(0) if self.table.rowCount() > 0 else 30  # Przybliżona wysokość wiersza
        header_height = self.table.horizontalHeader().height()  # Wysokość nagłówka kolumn
        total_height = header_height + (row_height * 15) + 40  # 15 wierszy + margines

        self.resize(total_column_width, total_height)

        layout.addWidget(self.table)

        # Przyciski zarządzania danymi
        button_layout = QHBoxLayout()

        # Przycisk Dodaj Wiersz
        add_button = QPushButton("Dodaj Wiersz")
        add_button.setIcon(QIcon("icons/add.png"))  # Zastąp odpowiednią ikoną
        add_button.clicked.connect(self.add_row)
        button_layout.addWidget(add_button)

        # Przycisk Usuń Wiersz
        remove_button = QPushButton("Usuń Wiersz")
        remove_button.setIcon(QIcon("icons/remove.png"))  # Zastąp odpowiednią ikoną
        remove_button.clicked.connect(self.remove_row)
        button_layout.addWidget(remove_button)

        # Przycisk Przenieś Góra
        up_button = QPushButton("Góra")
        up_button.setIcon(QIcon("icons/up.png"))  # Zastąp odpowiednią ikoną
        up_button.clicked.connect(self.move_row_up)
        button_layout.addWidget(up_button)

        # Przycisk Przenieś Dół
        down_button = QPushButton("Dół")
        down_button.setIcon(QIcon("icons/down.png"))  # Zastąp odpowiednią ikoną
        down_button.clicked.connect(self.move_row_down)
        button_layout.addWidget(down_button)

        # Przycisk Zapisz Zmiany
        save_button = QPushButton("Zapisz Zmiany")
        save_button.setIcon(QIcon("icons/save.png"))  # Zastąp odpowiednią ikoną
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_row(self):
        """Dodaje nowy wiersz."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

    def remove_row(self):
        """Usuwa zaznaczony wiersz."""
        selected_rows = set(idx.row() for idx in self.table.selectionModel().selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

    def move_row_up(self):
        """Przesuwa zaznaczony wiersz w górę."""
        current_row = self.table.currentRow()
        if current_row > 0:
            self.swap_rows(current_row, current_row - 1)
            self.table.selectRow(current_row - 1)

    def move_row_down(self):
        """Przesuwa zaznaczony wiersz w dół."""
        current_row = self.table.currentRow()
        if current_row < self.table.rowCount() - 1:
            self.swap_rows(current_row, current_row + 1)
            self.table.selectRow(current_row + 1)

    def swap_rows(self, row1, row2):
        """Zamienia zawartość dwóch wierszy."""
        for col in range(self.table.columnCount()):
            item1 = self.table.item(row1, col)
            item2 = self.table.item(row2, col)
            value1 = item1.text() if item1 else ""
            value2 = item2.text() if item2 else ""
            self.table.setItem(row1, col, QTableWidgetItem(value2))
            self.table.setItem(row2, col, QTableWidgetItem(value1))

    def save_changes(self):
        try:
            # Wczytaj dane z tabeli
            rows = self.table.rowCount()
            cols = self.table.columnCount()
            new_data = []

            for row in range(rows):
                row_data = []
                for col in range(cols):
                    item = self.table.item(row, col)
                    value = item.text() if item else ""
                    row_data.append(value)
                new_data.append(row_data)

            new_data = pd.DataFrame(new_data, columns=self.data.columns)
            new_data = new_data.apply(lambda x: x.map(safe_to_numeric))

            # Zapisz dane do JSON
            save_data_to_json(new_data)

            # Aktualizuj dane w głównym oknie
            self.parent().data = new_data

            # Sprawdź, czy model istnieje
            print(f"Model przekazany z obiektu nadrzędnego: {getattr(self.parent(), 'model', None)}")
            if hasattr(self.parent(), "model") and self.parent().model is not None:
                self.parent().model.train_models(new_data, force_retrain=True)
                print("Model przetrenowano na nowych danych.")
            else:
                print("Nie znaleziono modelu w obiekcie nadrzędnym.")

            QMessageBox.information(self, "Sukces", "Dane zapisano i modele przetrenowano.")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie udało się zapisać danych: {e}")




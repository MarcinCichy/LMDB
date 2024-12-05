from PyQt5.QtWidgets import QApplication
from ui_main import MainWindow
from data_loader import load_data
from model_utils import BDModel
from matrix_config_editor import MatrixConfigEditor
from data_editor import DataEditorDialog

if __name__ == "__main__":
    app = QApplication([])

    # Inicjalizacja modelu
    model = BDModel()

    # Wczytanie danych
    data = load_data()

    # Próba wczytania lub przetrenowania modeli
    print("Próba wczytania istniejących modeli...")
    model.train_models(data, force_retrain=False)  # force_retrain=False oznacza brak wymuszania treningu

    # Przygotowanie wartości dla MatrixConfigEditor
    grubosci = sorted(data['Grubosc'].unique())  # Pobierz unikalne grubości materiału
    matryce = sorted(set(data['V'].unique()))  # Pobierz unikalne szerokości matryc

    # Inicjalizacja MatrixConfigEditor
    matrix_config_editor = MatrixConfigEditor(grubosci, matryce)

    # Inicjalizacja DataEditorDialog
    data_editor = DataEditorDialog(data)

    # Inicjalizacja głównego okna z dodatkiem DXF
    window = MainWindow(data, model, matrix_config_editor, data_editor)

    # Wywołanie metody, która wypełnia listy rozwijane
    window.populate_comboboxes()

    # Uruchomienie głównego okna
    window.show()

    app.exec_()

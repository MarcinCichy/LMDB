LMDB/
├── main.py                # Główne okno aplikacji
├── ui_main.py             # Zarządzanie UI
├── model_utils.py         # Klasa BDModel (zarządzanie modelem, trenowanie, obliczanie BD)
├── data_loader.py         # Wczytywanie danych z pliku Excel i ich przetwarzanie
├── data_editor.py         # Klasa DataEditorDialog (edytor danych w osobnym oknie)
├── utils.py               # Funkcje pomocnicze (np. parsowanie wartości liczbowych)
├── config.json            # Opcjonalny plik konfiguracyjny
├── Ubytki.xlsx            # Plik z danymi treningowymi
├── segment_manager.py     # Zarządzanie tabelą segmentów
├── parameter_manager.py   # Zarządzanie parametrami
├── bd_calculator.py       # Obliczenia ubytków materiału
├── models/
│   ├── model_CZ_from_excel.joblib   # Model dla materiału CZ
│   └── model_N_from_excel.joblib    # Model dla materiału N


import os
import pandas as pd
import joblib
from xgboost import XGBRegressor
import time


class BDModel:
    def __init__(self):
        self.model_CZ = None
        self.model_N = None
        self.model_path_CZ = "models/model_CZ_from_excel.joblib"
        self.model_path_N = "models/model_N_from_excel.joblib"

    def train_models(self, data, force_retrain=False):
        """Trenuje modele dla materiałów CZ i N."""
        print("Rozpoczęcie procesu zarządzania modelami.")
        print(f"Ścieżki zapisów: {self.model_path_CZ}, {self.model_path_N}")

        # Przygotowanie danych
        X = data[['Grubosc', 'V', 'Kat']]
        y_CZ = data['BD_CZ']
        y_N = data['BD_N']

        # Wczytaj istniejące modele, jeśli nie wymuszamy treningu
        if not force_retrain and os.path.exists(self.model_path_CZ) and os.path.exists(self.model_path_N):
            try:
                print("Wczytywanie zapisanych modeli...")
                self.model_CZ = joblib.load(self.model_path_CZ)
                self.model_N = joblib.load(self.model_path_N)
                print(f"Data modyfikacji modelu CZ: {time.ctime(os.path.getmtime(self.model_path_CZ))}")
                print(f"Data modyfikacji modelu N: {time.ctime(os.path.getmtime(self.model_path_N))}")
                return
            except Exception as e:
                print(f"Błąd podczas wczytywania modeli: {e}. Rozpoczęcie ponownego treningu.")

        # Trenuj modele
        print("Trening modeli...")
        self.model_CZ = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.1)
        self.model_CZ.fit(X, y_CZ)

        self.model_N = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.1)
        self.model_N.fit(X, y_N)

        # Usuń istniejące pliki modeli przed zapisem
        try:
            if os.path.exists(self.model_path_CZ):
                os.remove(self.model_path_CZ)
            if os.path.exists(self.model_path_N):
                os.remove(self.model_path_N)
        except Exception as e:
            print(f"Błąd podczas usuwania starych modeli: {e}")

        # Zapis nowych modeli
        try:
            joblib.dump(self.model_CZ, self.model_path_CZ)
            print(f"Model CZ zapisano do: {os.path.abspath(self.model_path_CZ)}")
            print(f"Nowa data modyfikacji modelu CZ: {time.ctime(os.path.getmtime(self.model_path_CZ))}")

            joblib.dump(self.model_N, self.model_path_N)
            print(f"Model N zapisano do: {os.path.abspath(self.model_path_N)}")
            print(f"Nowa data modyfikacji modelu N: {time.ctime(os.path.getmtime(self.model_path_N))}")
        except Exception as e:
            print(f"Błąd podczas zapisywania modeli: {e}")

        # Weryfikacja zapisanych plików
        if not os.path.exists(self.model_path_CZ) or not os.path.exists(self.model_path_N):
            print("Błąd: Modele nie zostały zapisane!")
        else:
            print("Modele zostały poprawnie zapisane.")

    def oblicz_bd(self, t, V, kat, material):
        """Oblicza BD na podstawie modelu."""
        model = self.model_CZ if material == "CZ" else self.model_N
        X_new = pd.DataFrame([[t, V, kat]], columns=['Grubosc', 'V', 'Kat'])
        print(f"Obliczenia dla: {X_new}")
        bd_value = model.predict(X_new)[0]
        print(f"Wynik BD: {bd_value}")
        return max(bd_value, 0.0)

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QHBoxLayout, QWidget,
    QAction, QMenuBar, QGraphicsView, QGraphicsScene, QFileDialog
)
from PyQt5.QtCore import Qt, QPoint
import ezdxf
from PyQt5.QtGui import QPainter


class CustomGraphicsView(QGraphicsView):
    """Rozszerzony QGraphicsView z obsługą przesuwania i powiększania."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QPainter.Antialiasing)  # Włącz antyaliasing
        self.setDragMode(QGraphicsView.NoDrag)  # Domyślny tryb: brak przeciągania
        self.setInteractive(True)  # Umożliwia interakcję z elementami
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # Powiększanie wokół kursora
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)  # Skalowanie względem centrum widoku
        self._dragging = False  # Flaga przesuwania
        self._last_mouse_position = QPoint()  # Ostatnia pozycja myszy
        self.padding = 500  # Dodatkowy obszar sceny w pikselach

    def set_scene_padding(self):
        """Dodaje obszar wokół rysunku, aby umożliwić przesuwanie."""
        if self.scene() is not None:
            # Pobierz oryginalny obszar sceny
            original_rect = self.scene().itemsBoundingRect()
            # Powiększ obszar o zadany padding
            padded_rect = original_rect.adjusted(
                -self.padding, -self.padding, self.padding, self.padding
            )
            self.scene().setSceneRect(padded_rect)

    def mousePressEvent(self, event):
        """Rozpoczęcie przesuwania sceny."""
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)  # Zmień kursor na "zamkniętą łapkę"
            self._dragging = True
            self._last_mouse_position = event.pos()  # Zapisz pozycję myszy
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Przesuwanie sceny w odpowiedzi na ruch myszy."""
        if self._dragging:
            delta = event.pos() - self._last_mouse_position  # Oblicz różnicę pozycji
            self._last_mouse_position = event.pos()  # Zaktualizuj ostatnią pozycję myszy
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Zakończenie przesuwania sceny."""
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # Przywróć domyślny kursor
            self._dragging = False
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Obsługuje powiększanie i pomniejszanie za pomocą kółka myszy."""
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:  # Zoom in
            self.scale(zoom_in_factor, zoom_in_factor)
        else:  # Zoom out
            self.scale(zoom_out_factor, zoom_out_factor)

class MainWindow(QMainWindow):
    def __init__(self, data, model, matrix_config_editor, data_editor):
        super().__init__()
        self.setWindowTitle("Kalkulator Ubytku Materiału BD")
        self.data = data
        self.model = model
        self.matrix_config_editor = matrix_config_editor
        self.data_editor = data_editor

        # Scena DXF dla widoku graficznego
        self.dxf_scene = QGraphicsScene()

        self.init_ui()

        # Uruchom w trybie zmaksymalizowanym
        self.showMaximized()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()  # Główne okno: lewa i prawa sekcja

        # Lewa sekcja (parametry + tabela segmentów)
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Sekcja parametrów
        params_layout = QHBoxLayout()

        self.grubosc_input = QComboBox()
        self.grubosc_input.currentIndexChanged.connect(self.update_v_input)
        params_layout.addWidget(QLabel("Grubość [mm]:"))
        params_layout.addWidget(self.grubosc_input)

        self.V_input = QComboBox()
        params_layout.addWidget(QLabel("V [mm]:"))
        params_layout.addWidget(self.V_input)

        self.material_input = QComboBox()
        self.material_input.addItems(["CZ", "N"])
        params_layout.addWidget(QLabel("Materiał:"))
        params_layout.addWidget(self.material_input)

        left_layout.addLayout(params_layout)

        # Tabela segmentów
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Długość [mm]", "Kąt gięcia [°]", "BD [mm]"])
        left_layout.addWidget(self.table)

        # Przyciski do zarządzania segmentami
        buttons_layout = QHBoxLayout()
        add_segment_button = QPushButton("Dodaj Segment")
        add_segment_button.clicked.connect(self.add_segment)
        buttons_layout.addWidget(add_segment_button)

        remove_segment_button = QPushButton("Usuń Segment")
        remove_segment_button.clicked.connect(self.remove_segment)
        buttons_layout.addWidget(remove_segment_button)

        left_layout.addLayout(buttons_layout)

        # Przycisk obliczania
        self.calculate_button = QPushButton("Oblicz Łączną Długość")
        self.calculate_button.clicked.connect(self.calculate_total_bd)
        left_layout.addWidget(self.calculate_button)

        # Wyniki
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.result_label)

        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(400)  # Stała szerokość lewej części

        # Prawa sekcja (widok DXF)
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        load_dxf_button = QPushButton("Wczytaj Plik DXF")
        load_dxf_button.clicked.connect(self.load_dxf_file)
        right_layout.addWidget(load_dxf_button)

        self.dxf_view = CustomGraphicsView()
        self.dxf_view.setScene(self.dxf_scene)
        right_layout.addWidget(self.dxf_view)

        right_widget.setLayout(right_layout)

        # Dodanie sekcji do głównego układu
        self.main_layout.addWidget(left_widget, stretch=1)  # Lewa część proporcja 1
        self.main_layout.addWidget(right_widget, stretch=3)  # Prawa część proporcja 3

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def load_dxf_file(self):
        """Wczytuje plik DXF i wyświetla jego zawartość."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz Plik DXF", "", "Pliki DXF (*.dxf)")
        if not file_path:
            return

        try:
            doc = ezdxf.readfile(file_path)
            self.dxf_scene.clear()

            # Renderowanie elementów DXF
            for entity in doc.modelspace():
                if entity.dxftype() == 'LINE':
                    start = entity.dxf.start
                    end = entity.dxf.end
                    self.dxf_scene.addLine(start.x, -start.y, end.x, -end.y)
                elif entity.dxftype() == 'CIRCLE':
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    self.dxf_scene.addEllipse(
                        center.x - radius, -center.y - radius, 2 * radius, 2 * radius
                    )
                elif entity.dxftype() == 'ARC':
                    # Renderowanie łuków
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    start_angle = entity.dxf.start_angle
                    end_angle = entity.dxf.end_angle

                    # Przekształcenie kątów na układ Qt (0 stopni = godzina 3)
                    start_angle_qt = -start_angle
                    span_angle_qt = -(end_angle - start_angle)

                    # Tworzenie prostokąta opisującego łuk
                    rect = QRectF(
                        center.x - radius, -center.y - radius, 2 * radius, 2 * radius
                    )
                    path = QPainterPath()
                    path.arcMoveTo(rect, start_angle_qt)
                    path.arcTo(rect, start_angle_qt, span_angle_qt)
                    self.dxf_scene.addPath(path)
                elif entity.dxftype() == 'POLYLINE':
                    # Renderowanie polilinii
                    points = [point for point in entity.points()]
                    for i in range(len(points) - 1):
                        self.dxf_scene.addLine(
                            points[i][0], -points[i][1], points[i + 1][0], -points[i + 1][1]
                        )
                elif entity.dxftype() == 'LWPOLYLINE':
                    # Renderowanie LWPOLYLINE z opcjonalnymi zaokrągleniami
                    points = list(entity.points())
                    for i in range(len(points)):
                        start_point = points[i]
                        end_point = points[(i + 1) % len(points)]  # Kolejny punkt lub początek
                        bulge = start_point[4] if len(start_point) > 4 else 0  # Współczynnik zaokrąglenia
                        if bulge == 0:
                            # Rysuj linię prostą
                            self.dxf_scene.addLine(
                                start_point[0], -start_point[1], end_point[0], -end_point[1]
                            )
                        else:
                            # Rysuj łuk na podstawie bulge
                            self.draw_bulge_arc(start_point, end_point, bulge)
                else:
                    print(f"Nieobsługiwany typ: {entity.dxftype()}")

            # Centrowanie widoku
            self.dxf_view.fitInView(self.dxf_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie udało się wczytać pliku DXF:\n{e}")

    def draw_bulge_arc(self, start_point, end_point, bulge):
        """Rysuje łuk na podstawie współczynnika bulge."""
        import math

        # Oblicz promień i środek okręgu
        chord_length = math.sqrt(
            (end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2
        )
        radius = abs(chord_length / (2 * math.sin(2 * math.atan(bulge))))
        center_x = (start_point[0] + end_point[0]) / 2
        center_y = (start_point[1] + end_point[1]) / 2
        angle_start = math.degrees(math.atan2(start_point[1] - center_y, start_point[0] - center_x))
        angle_end = math.degrees(math.atan2(end_point[1] - center_y, end_point[0] - center_x))

        rect = QRectF(center_x - radius, -center_y - radius, 2 * radius, 2 * radius)
        path = QPainterPath()
        path.arcMoveTo(rect, angle_start)
        path.arcTo(rect, angle_start, angle_end - angle_start)
        self.dxf_scene.addPath(path)

    def update_v_input(self):
        """Aktualizuje listę dostępnych szerokości matryc po zmianie grubości."""
        selected_grubosc = self.grubosc_input.currentText()
        if self.data is not None:
            try:
                V_values = sorted(set(self.data.loc[self.data['Grubosc'] == float(selected_grubosc), 'V']))
            except ValueError:
                V_values = []
            self.V_input.clear()
            self.V_input.addItems([str(x) for x in V_values])

    def add_segment(self):
        """Dodaje nowy segment do tabeli."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        dlugosc_item = QTableWidgetItem("100")
        kat_item = QTableWidgetItem("90")
        bd_item = QTableWidgetItem("")
        bd_item.setFlags(Qt.ItemIsEnabled)
        self.table.setItem(row_count, 0, dlugosc_item)
        self.table.setItem(row_count, 1, kat_item)
        self.table.setItem(row_count, 2, bd_item)

    def remove_segment(self):
        """Usuwa zaznaczony segment z tabeli."""
        selected_rows = set(idx.row() for idx in self.table.selectionModel().selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

    def calculate_total_bd(self):
        """Oblicza łączną długość i ubytek materiału."""
        try:
            material = self.material_input.currentText()
            total_length = 0.0
            total_bd = 0.0

            for row in range(self.table.rowCount()):
                dlugosc_item = self.table.item(row, 0)
                kat_item = self.table.item(row, 1)

                if not dlugosc_item or not kat_item:
                    continue

                dlugosc = float(dlugosc_item.text())
                kat = float(kat_item.text())
                grubosc = float(self.grubosc_input.currentText())
                V = float(self.V_input.currentText())

                bd_value = 0.0 if kat == 0 else self.model.oblicz_bd(grubosc, V, kat, material)
                total_length += dlugosc
                total_bd += bd_value

                bd_item = QTableWidgetItem(f"{bd_value:.2f}")
                bd_item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(row, 2, bd_item)

            self.result_label.setText(
                f"Łączna Długość: {total_length:.2f} mm\nŁączny Ubytek (BD): {total_bd:.2f} mm"
            )
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Wystąpił błąd podczas obliczania BD:\n{e}")

    def populate_comboboxes(self):
        """Wypełnia listy rozwijane wartościami na podstawie danych."""
        if self.data is not None:
            # Pobierz unikalne wartości grubości
            grubosc_values = sorted(self.data['Grubosc'].unique())
            self.grubosc_input.clear()
            self.grubosc_input.addItems([str(x) for x in grubosc_values])

            # Automatycznie zaktualizuj V_input na podstawie pierwszej grubości
            if grubosc_values:
                self.update_v_input()
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel, QMessageBox, QHBoxLayout, QAbstractItemView, QApplication, QProgressBar)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from visualization import create_canvas
from utils import paste_data, clear_layout
import matplotlib.pyplot as plt

class ContainerLoadingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Container Loading Visualization")
        self.setGeometry(100, 100, 1200, 800)

        self.vehicle_options = {
            "20' Konteyner": (589, 235, 239, 28000),  # (length in cm, width in cm, height in cm, max weight in kg)
            "40' Konteyner": (1203, 235, 239, 30480),
            "Kamyon": (1200, 250, 300, 40000),
            # Diğer araç türlerini buraya ekleyebilirsiniz
        }

        self.initUI()

    def initUI(self):
        self.vehicle_selector = QComboBox(self)
        self.vehicle_selector.addItems(self.vehicle_options.keys())
        self.vehicle_selector.currentIndexChanged.connect(self.on_vehicle_change)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Ürün Adı', 'Uzunluk (cm)', 'Genişlik (cm)', 'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar'])
        self.table.setRowCount(10)
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)

        self.status_label = QLabel('Durum: Bekliyor', self)
        self.total_weight_label = QLabel('Toplam Ağırlık: 0 kg', self)
        self.total_volume_label = QLabel('Toplam Hacim: 0 m³', self)
        self.remaining_volume_label = QLabel('Kalan Hacim: 0 m³', self)
        self.remaining_weight_label = QLabel('Kalan Tonaj: 0 kg', self)

        self.load_button = QPushButton("Yükle", self)
        self.load_button.clicked.connect(self.start_loading)

        self.zoom_in_button = QPushButton("", self)
        self.zoom_in_button.setIcon(QIcon('zoom_in.png'))  # Büyüteç simgesi dosyasını kullanın
        self.zoom_in_button.setFixedSize(30, 30)
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_out_button = QPushButton("", self)
        self.zoom_out_button.setIcon(QIcon('zoom_out.png'))  # Büyüteç simgesi dosyasını kullanın
        self.zoom_out_button.setFixedSize(30, 30)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        self.canvas, self.ax = create_canvas()

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.zoom_in_button)
        control_layout.addWidget(self.zoom_out_button)
        control_layout.addWidget(self.progress_bar)
        control_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(control_layout)

        self.product_info_layout = QVBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(self.vehicle_selector)
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)
        layout.addWidget(self.total_weight_label)
        layout.addWidget(self.total_volume_label)
        layout.addWidget(self.remaining_volume_label)
        layout.addWidget(self.remaining_weight_label)
        layout.addWidget(self.load_button)
        layout.addLayout(main_layout)
        layout.addLayout(self.product_info_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.table.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == event.KeyPress and event.key() == Qt.Key_V and QApplication.keyboardModifiers() == Qt.ControlModifier:
            paste_data(self.table)
            return True
        return super().eventFilter(source, event)

    def on_vehicle_change(self):
        self.status_label.setText('Durum: Araç Seçildi')

    def start_loading(self):
        self.load_thread = LoadThread(self)
        self.load_thread.progress.connect(self.update_progress)
        self.load_thread.finished.connect(self.loading_finished)
        self.load_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def loading_finished(self):
        self.status_label.setText('Durum: Yükleme Tamamlandı')

    def zoom_in(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 0.9, self.ax.get_xlim()[1] * 0.9)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 0.9, self.ax.get_ylim()[1] * 0.9)
        self.ax.set_zlim(self.ax.get_zlim()[0] * 0.9, self.ax.get_zlim()[1] * 0.9)
        self.canvas.draw()

    def zoom_out(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 1.1, self.ax.get_xlim()[1] * 1.1)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 1.1, self.ax.get_ylim()[1] * 1.1)
        self.ax.set_zlim(self.ax.get_zlim()[0] * 1.1, self.ax.get_zlim()[1] * 1.1)
        self.canvas.draw()

class LoadThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        row_count = self.app.table.rowCount()
        data = []
        for row in range(row_count):
            row_data = []
            for col in range(6):
                item = self.app.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        df = pd.DataFrame(data, columns=['Ürün Adı', 'Uzunluk (cm)', 'Genişlik (cm)', 'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar'])
        df = df[df['Uzunluk (cm)'] != '']  # Boş satırları kaldır
        df = df.astype({'Uzunluk (cm)': 'int', 'Genişlik (cm)': 'int', 'Yükseklik (cm)': 'int', 'Ağırlık (kg)': 'int', 'Miktar': 'int'})

        vehicle = self.app.vehicle_selector.currentText()
        container_dimensions = self.app.vehicle_options[vehicle]
        container_length, container_width, container_height, max_weight = container_dimensions

        self.app.ax.clear()

        total_volume = 0
        total_weight = 0
        cmap = plt.get_cmap('tab10')

        product_colors = {}
        product_volumes = {}
        product_weights = {}

        position_map = np.zeros((container_length, container_width, container_height), dtype=bool)

        total_items = len(df) * df['Miktar'].sum()
        processed_items = 0

        for index, row in df.iterrows():
            color = cmap(index % 10)
            product_colors[row['Ürün Adı']] = color
            product_volumes[row['Ürün Adı']] = 0
            product_weights[row['Ürün Adı']] = 0

            for _ in range(row['Miktar']):
                placed = False
                for z in range(container_height):
                    if placed:
                        break
                    for y in range(container_width):
                        if placed:
                            break
                        for x in range(container_length):
                            if (x + row['Uzunluk (cm)'] <= container_length and
                                y + row['Genişlik (cm)'] <= container_width and
                                z + row['Yükseklik (cm)'] <= container_height and
                                not position_map[x:x+row['Uzunluk (cm)'], y:y+row['Genişlik (cm)'], z:z+row['Yükseklik (cm)']].any()):
                                
                                self.app.ax.bar3d(x, y, z, row['Uzunluk (cm)'], row['Genişlik (cm)'], row['Yükseklik (cm)'], color=color)
                                self.app.ax.text(x + row['Uzunluk (cm)'] / 2, y + row['Genişlik (cm)'] / 2, z + row['Yükseklik (cm)'] / 2, row['Ürün Adı'], color='black', ha='center', va='center')

                                position_map[x:x+row['Uzunluk (cm)'], y:y+row['Genişlik (cm)'], z:z+row['Yükseklik (cm)']] = True

                                volume = (row['Uzunluk (cm)'] * row['Genişlik (cm)'] * row['Yükseklik (cm)']) / 1000000  # Convert cm³ to m³
                                weight = row['Ağırlık (kg)']

                                total_volume += volume
                                total_weight += weight

                                product_volumes[row['Ürün Adı']] += volume
                                product_weights[row['Ürün Adı']] += weight

                                placed = True
                                break

                if not placed:
                    self.app.status_label.setText(f'Uyarı: {row["Ürün Adı"]} ürünü konteynere sığmıyor!')
                    return

                processed_items += 1
                progress = int((processed_items / total_items) * 100)
                self.progress.emit(progress)
                self.app.canvas.draw()

        max_dim = max(container_length, container_width, container_height)
        self.app.ax.set_box_aspect([container_length/max_dim, container_width/max_dim, container_height/max_dim])
        self.app.ax.set_xlim(0, container_length)
        self.app.ax.set_ylim(0, container_width)
        self.app.ax.set_zlim(0, container_height)
        self.app.ax.set_xlabel('Uzunluk (cm)')
        self.app.ax.set_ylabel('Genişlik (cm)')
        self.app.ax.set_zlabel('Yükseklik (cm)')
        self.app.ax.set_title(f'{vehicle} Yükleme Durumu')
        self.app.canvas.draw()

        self.app.total_weight_label.setText(f'Toplam Ağırlık: {total_weight:.2f} kg')
        self.app.total_volume_label.setText(f'Toplam Hacim: {total_volume:.2f} m³')
        remaining_volume = (container_length * container_width * container_height / 1000000) - total_volume
        remaining_weight = max_weight - total_weight
        self.app.remaining_volume_label.setText(f'Kalan Hacim: {remaining_volume:.2f} m³')
        self.app.remaining_weight_label.setText(f'Kalan Tonaj: {remaining_weight:.2f} kg')

        clear_layout(self.app.product_info_layout)

        for product, color in product_colors.items():
            rgba = f"rgba({color[0]*255:.0f}, {color[1]*255:.0f}, {color[2]*255:.0f}, {color[3]:.2f})"
            color_rect = QLabel(self.app)
            color_rect.setStyleSheet(f"background-color: {rgba}; border: 1px solid black;")
            color_rect.setFixedSize(20, 20)
            product_info = f"Ürün: {product}, Hacim: {product_volumes[product]:.2f} m³, Ağırlık: {product_weights[product]:.2f} kg"
            product_label = QLabel(product_info, self.app)
            info_layout = QHBoxLayout()
            info_layout.addWidget(color_rect)
            info_layout.addWidget(product_label)
            self.app.product_info_layout.addLayout(info_layout)

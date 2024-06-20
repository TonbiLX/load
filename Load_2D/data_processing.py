import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import matplotlib.pyplot as plt
from visualization import draw_prism
from utils import clear_layout

class LoadThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.positions = []
        self.colors = []
        self.product_colors = {}
        self.product_volumes = {}
        self.product_weights = {}
        self.total_volume = 0
        self.total_weight = 0
        self.remaining_volume = 0
        self.remaining_weight = 0

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

        total_volume = 0
        total_weight = 0
        cmap = plt.get_cmap('tab10')

        self.product_colors = {}
        self.product_volumes = {}
        self.product_weights = {}

        position_map = np.zeros((container_length, container_width), dtype=bool)

        total_items = len(df) * df['Miktar'].sum()
        processed_items = 0

        def find_position(l, w):
            for y in range(container_width - w + 1):
                for x in range(container_length - l + 1):
                    if not position_map[x:x+l, y:y+w].any():
                        return x, y
            return None, None

        for index, row in df.iterrows():
            color = cmap(index % 10)
            self.product_colors[row['Ürün Adı']] = color
            self.product_volumes[row['Ürün Adı']] = 0
            self.product_weights[row['Ürün Adı']] = 0

            for _ in range(row['Miktar']):
                l, w, h = row['Uzunluk (cm)'], row['Genişlik (cm)'], row['Yükseklik (cm)']
                x, y = find_position(l, w)
                if x is not None and y is not None:
                    self.positions.append((x, y, l, w, h, row['Ürün Adı']))
                    self.colors.append(color)

                    position_map[x:x+l, y:y+w] = True

                    volume = (l * w * h) / 1000000  # Convert cm³ to m³
                    weight = row['Ağırlık (kg)']

                    total_volume += volume
                    total_weight += weight

                    self.product_volumes[row['Ürün Adı']] += volume
                    self.product_weights[row['Ürün Adı']] += weight

                    processed_items += 1
                    progress = int((processed_items / total_items) * 100)
                    self.progress.emit(progress)

        self.total_volume = total_volume
        self.total_weight = total_weight
        self.remaining_volume = (container_length * container_width * container_height / 1000000) - total_volume
        self.remaining_weight = max_weight - total_weight

    def result_plot(self):
        self.app.ax.clear()
        self.draw_container()

        for pos, color in zip(self.positions, self.colors):
            x, y, dx, dy, dz, product_name = pos
            draw_prism(self.app.ax, x, y, dx, dy, dz, color=color, label=product_name)

        self.app.ax.set_xlim(0, self.app.vehicle_options[self.app.vehicle_selector.currentText()][0])
        self.app.ax.set_ylim(0, self.app.vehicle_options[self.app.vehicle_selector.currentText()][1])
        self.app.ax.set_zlim(0, self.app.vehicle_options[self.app.vehicle_selector.currentText()][2])
        self.app.ax.set_box_aspect([self.app.vehicle_options[self.app.vehicle_selector.currentText()][0],
                                    self.app.vehicle_options[self.app.vehicle_selector.currentText()][1],
                                    self.app.vehicle_options[self.app.vehicle_selector.currentText()][2]])

        self.app.canvas.draw()

        self.app.total_weight_label.setText(f'Toplam Ağırlık: {self.total_weight:.2f} kg')
        self.app.total_volume_label.setText(f'Toplam Hacim: {self.total_volume:.2f} m³')
        self.app.remaining_volume_label.setText(f'Kalan Hacim: {self.remaining_volume:.2f} m³')
        self.app.remaining_weight_label.setText(f'Kalan Tonaj: {self.remaining_weight:.2f} kg')

        clear_layout(self.app.product_info_layout)

        for product, color in self.product_colors.items():
            rgba = f"rgba({color[0]*255:.0f}, {color[1]*255:.0f}, {color[2]*255:.0f}, {color[3]:.2f})"
            color_rect = QLabel(self.app)
            color_rect.setStyleSheet(f"background-color: {rgba}; border: 1px solid black;")
            color_rect.setFixedSize(20, 20)
            product_info = f"Ürün: {product}, Hacim: {self.product_volumes[product]:.2f} m³, Ağırlık: {self.product_weights[product]:.2f} kg"
            product_label = QLabel(product_info, self.app)
            info_layout = QHBoxLayout()
            info_layout.addWidget(color_rect)
            info_layout.addWidget(product_label)
            self.app.product_info_layout.addLayout(info_layout)

    def draw_container(self):
        """Draw the container with perspective."""
        vehicle = self.app.vehicle_selector.currentText()
        length, width, height, _ = self.app.vehicle_options[vehicle]
        draw_prism(self.app.ax, 0, 0, length, width, height, color=(0, 0, 0, 0.1), label=None)

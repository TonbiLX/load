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
        df = df[df['Ürün Adı'] != '']

        # Convert necessary columns to numeric types
        df['Uzunluk (cm)'] = pd.to_numeric(df['Uzunluk (cm)'], errors='coerce')
        df['Genişlik (cm)'] = pd.to_numeric(df['Genişlik (cm)'], errors='coerce')
        df['Yükseklik (cm)'] = pd.to_numeric(df['Yükseklik (cm)'], errors='coerce')
        df['Ağırlık (kg)'] = pd.to_numeric(df['Ağırlık (kg)'], errors='coerce')
        df['Miktar'] = pd.to_numeric(df['Miktar'], errors='coerce')

        container_length, container_width, container_height, max_weight = self.app.vehicle_options[self.app.vehicle_selector.currentText()]

        total_volume = 0
        total_weight = 0
        total_items = df['Miktar'].sum()
        processed_items = 0

        position_map = np.zeros((container_length, container_width), dtype=bool)

        for _, row in df.iterrows():
            for _ in range(int(row['Miktar'])):
                l, w, h = int(row['Uzunluk (cm)']), int(row['Genişlik (cm)']), int(row['Yükseklik (cm)'])
                color = plt.get_cmap('tab10')(len(self.product_colors) % 10)
                self.product_colors[row['Ürün Adı']] = color
                if row['Ürün Adı'] not in self.product_volumes:
                    self.product_volumes[row['Ürün Adı']] = 0
                    self.product_weights[row['Ürün Adı']] = 0

                def find_position(l, w):
                    for i in range(container_length - l + 1):
                        for j in range(container_width - w + 1):
                            if not position_map[i:i + l, j:j + w].any():
                                return i, j
                    return None, None

                x, y = find_position(l, w)
                if x is not None and y is not None:
                    self.positions.append((x, y, l, w, h, row['Ürün Adı']))
                    self.colors.append(color)

                    position_map[x:x + l, y:y + w] = True

                    volume = (l * w * h) / 1000000  # Convert cm³ to m³
                    weight = float(row['Ağırlık (kg)'])

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
            rgba = f"rgba({color[0] * 255:.0f}, {color[1] * 255:.0f}, {color[2] * 255:.0f}, {color[3]:.2f})"
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

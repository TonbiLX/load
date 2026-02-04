import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import matplotlib.pyplot as plt
from visualization import draw_prism
from utils import clear_layout


class LoadThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, app, table_data, vehicle_name, container_dims):
        super().__init__()
        self.app = app
        self.table_data = table_data
        self.vehicle_name = vehicle_name
        self.container_dims = container_dims
        self.positions = []
        self.colors = []
        self.product_colors = {}
        self.product_volumes = {}
        self.product_weights = {}
        self.total_volume = 0
        self.total_weight = 0
        self.remaining_volume = 0
        self.remaining_weight = 0
        self.warnings = []

    def run(self):
        container_length, container_width, container_height, max_weight = self.container_dims

        df = pd.DataFrame(self.table_data, columns=[
            'Ürün Adı', 'Uzunluk (cm)', 'Genişlik (cm)',
            'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar'])
        df = df[df['Ürün Adı'] != '']

        # Safe type conversion
        for col in ['Uzunluk (cm)', 'Genişlik (cm)', 'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna()

        if df.empty:
            return

        total_volume = 0
        total_weight = 0
        total_items = int(df['Miktar'].sum())
        processed_items = 0

        # Assign colors per unique product upfront (fix: same product gets same color)
        cmap = plt.get_cmap('tab10')
        for idx, name in enumerate(df['Ürün Adı'].unique()):
            self.product_colors[name] = cmap(idx % 10)
            self.product_volumes[name] = 0
            self.product_weights[name] = 0

        position_map = np.zeros((container_length, container_width), dtype=bool)

        for _, row in df.iterrows():
            l, w, h = int(row['Uzunluk (cm)']), int(row['Genişlik (cm)']), int(row['Yükseklik (cm)'])
            weight = float(row['Ağırlık (kg)'])
            color = self.product_colors[row['Ürün Adı']]

            for _ in range(int(row['Miktar'])):
                # Weight limit check
                if total_weight + weight > max_weight:
                    self.warnings.append(f'{row["Ürün Adı"]} - ağırlık kapasitesi aşıldı!')
                    break

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

                    volume = (l * w * h) / 1000000
                    total_volume += volume
                    total_weight += weight

                    self.product_volumes[row['Ürün Adı']] += volume
                    self.product_weights[row['Ürün Adı']] += weight

                    processed_items += 1
                    if total_items > 0:
                        self.progress.emit(int((processed_items / total_items) * 100))
                else:
                    self.warnings.append(f'{row["Ürün Adı"]} ürünü konteynere sığmıyor!')
                    break

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

        container_length, container_width, container_height, _ = self.container_dims
        self.app.ax.set_xlim(0, container_length)
        self.app.ax.set_ylim(0, container_width)
        self.app.ax.set_zlim(0, container_height)
        self.app.ax.set_box_aspect([container_length, container_width, container_height])

        self.app.canvas.draw()

        self.app.total_weight_label.setText(f'Toplam Ağırlık: {self.total_weight:.2f} kg')
        self.app.total_volume_label.setText(f'Toplam Hacim: {self.total_volume:.2f} m³')
        self.app.remaining_volume_label.setText(f'Kalan Hacim: {self.remaining_volume:.2f} m³')
        self.app.remaining_weight_label.setText(f'Kalan Tonaj: {self.remaining_weight:.2f} kg')

        clear_layout(self.app.product_info_layout)

        for product, color in self.product_colors.items():
            rgba = (f"rgba({color[0] * 255:.0f}, {color[1] * 255:.0f}, "
                    f"{color[2] * 255:.0f}, {color[3]:.2f})")
            color_rect = QLabel(self.app)
            color_rect.setStyleSheet(f"background-color: {rgba}; border: 1px solid black;")
            color_rect.setFixedSize(20, 20)
            product_info = (f"Ürün: {product}, Hacim: {self.product_volumes[product]:.2f} m³, "
                            f"Ağırlık: {self.product_weights[product]:.2f} kg")
            product_label = QLabel(product_info, self.app)
            info_layout = QHBoxLayout()
            info_layout.addWidget(color_rect)
            info_layout.addWidget(product_label)
            self.app.product_info_layout.addLayout(info_layout)

        # Show warnings if any
        if self.warnings:
            self.app.status_label.setText(f'Uyarı: {self.warnings[0]}')

    def draw_container(self):
        """Draw the container with perspective."""
        container_length, container_width, container_height, _ = self.container_dims
        draw_prism(self.app.ax, 0, 0, container_length, container_width, container_height,
                   color=(0, 0, 0, 0.1), label=None)

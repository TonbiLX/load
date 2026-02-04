import pandas as pd
import numpy as np
import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QTableWidget,
                              QPushButton, QComboBox, QLabel, QHBoxLayout,
                              QAbstractItemView, QApplication, QProgressBar)
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
            "20' Konteyner": (589, 235, 239, 28000),
            "40' Konteyner": (1203, 235, 239, 30480),
            "Kamyon": (1200, 250, 300, 40000),
        }

        self.load_thread = None
        self.initUI()

    def initUI(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.vehicle_selector = QComboBox(self)
        self.vehicle_selector.addItems(self.vehicle_options.keys())
        self.vehicle_selector.currentIndexChanged.connect(self.on_vehicle_change)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ['Ürün Adı', 'Uzunluk (cm)', 'Genişlik (cm)', 'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar'])
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
        self.zoom_in_button.setIcon(QIcon(os.path.join(base_dir, 'zoom_in.png')))
        self.zoom_in_button.setFixedSize(30, 30)
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_out_button = QPushButton("", self)
        self.zoom_out_button.setIcon(QIcon(os.path.join(base_dir, 'zoom_out.png')))
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
        if (event.type() == event.KeyPress and event.key() == Qt.Key_V
                and QApplication.keyboardModifiers() == Qt.ControlModifier):
            paste_data(self.table)
            return True
        return super().eventFilter(source, event)

    def on_vehicle_change(self):
        self.status_label.setText('Durum: Araç Seçildi')

    def start_loading(self):
        if self.load_thread is not None and self.load_thread.isRunning():
            return

        # Reset UI
        self.progress_bar.setValue(0)
        self.status_label.setText('Durum: Yükleniyor...')
        self.load_button.setEnabled(False)

        # Collect table data in main thread (thread safety)
        row_count = self.table.rowCount()
        data = []
        for row in range(row_count):
            row_data = []
            for col in range(6):
                item = self.table.item(row, col)
                row_data.append(item.text() if item is not None else '')
            data.append(row_data)

        vehicle = self.vehicle_selector.currentText()
        container_dims = self.vehicle_options[vehicle]

        self.load_thread = LoadThread(data, container_dims, vehicle)
        self.load_thread.progress.connect(self.update_progress)
        self.load_thread.result_ready.connect(self.display_results)
        self.load_thread.warning.connect(self.show_warning)
        self.load_thread.finished.connect(self.loading_finished)
        self.load_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_warning(self, message):
        self.status_label.setText(f'Uyarı: {message}')

    def display_results(self, results):
        self.ax.clear()

        container_length = results['container_length']
        container_width = results['container_width']
        container_height = results['container_height']
        vehicle = results['vehicle']

        # Draw placed items
        for item in results['placed_items']:
            x, y, z = item['x'], item['y'], item['z']
            l, w, h = item['l'], item['w'], item['h']
            color = item['color']
            name = item['name']
            self.ax.bar3d(x, y, z, l, w, h, color=color, alpha=0.8)
            self.ax.text(x + l / 2, y + w / 2, z + h / 2, name,
                         color='black', ha='center', va='center', fontsize=6)

        max_dim = max(container_length, container_width, container_height)
        self.ax.set_box_aspect([
            container_length / max_dim,
            container_width / max_dim,
            container_height / max_dim
        ])
        self.ax.set_xlim(0, container_length)
        self.ax.set_ylim(0, container_width)
        self.ax.set_zlim(0, container_height)
        self.ax.set_xlabel('Uzunluk (cm)')
        self.ax.set_ylabel('Genişlik (cm)')
        self.ax.set_zlabel('Yükseklik (cm)')
        self.ax.set_title(f'{vehicle} Yükleme Durumu')
        self.canvas.draw()

        # Update labels
        self.total_weight_label.setText(f'Toplam Ağırlık: {results["total_weight"]:.2f} kg')
        self.total_volume_label.setText(f'Toplam Hacim: {results["total_volume"]:.2f} m³')
        self.remaining_volume_label.setText(f'Kalan Hacim: {results["remaining_volume"]:.2f} m³')
        self.remaining_weight_label.setText(f'Kalan Tonaj: {results["remaining_weight"]:.2f} kg')

        # Update product info
        clear_layout(self.product_info_layout)
        for product, color in results['product_colors'].items():
            rgba = (f"rgba({color[0] * 255:.0f}, {color[1] * 255:.0f}, "
                    f"{color[2] * 255:.0f}, {color[3]:.2f})")
            color_rect = QLabel(self)
            color_rect.setStyleSheet(f"background-color: {rgba}; border: 1px solid black;")
            color_rect.setFixedSize(20, 20)
            vol = results['product_volumes'][product]
            wgt = results['product_weights'][product]
            product_label = QLabel(
                f"Ürün: {product}, Hacim: {vol:.2f} m³, Ağırlık: {wgt:.2f} kg", self)
            info_layout = QHBoxLayout()
            info_layout.addWidget(color_rect)
            info_layout.addWidget(product_label)
            self.product_info_layout.addLayout(info_layout)

    def loading_finished(self):
        self.load_button.setEnabled(True)
        if self.status_label.text().startswith('Uyarı'):
            return
        self.status_label.setText('Durum: Yükleme Tamamlandı')
        self.progress_bar.setValue(100)

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
    result_ready = pyqtSignal(object)
    warning = pyqtSignal(str)

    def __init__(self, table_data, container_dims, vehicle):
        super().__init__()
        self.table_data = table_data
        self.container_dims = container_dims
        self.vehicle = vehicle

    def run(self):
        container_length, container_width, container_height, max_weight = self.container_dims

        df = pd.DataFrame(self.table_data, columns=[
            'Ürün Adı', 'Uzunluk (cm)', 'Genişlik (cm)',
            'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar'])
        df = df[df['Uzunluk (cm)'] != '']

        # Safe type conversion (avoid crash on non-numeric input)
        for col in ['Uzunluk (cm)', 'Genişlik (cm)', 'Yükseklik (cm)', 'Ağırlık (kg)', 'Miktar']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna()

        if df.empty:
            return

        df = df.astype({
            'Uzunluk (cm)': 'int', 'Genişlik (cm)': 'int',
            'Yükseklik (cm)': 'int', 'Miktar': 'int'
        })

        # Assign colors per unique product upfront (fix color consistency)
        cmap = plt.get_cmap('tab10')
        product_colors = {}
        product_volumes = {}
        product_weights = {}
        for idx, name in enumerate(df['Ürün Adı'].unique()):
            product_colors[name] = cmap(idx % 10)
            product_volumes[name] = 0
            product_weights[name] = 0

        total_volume = 0
        total_weight = 0
        # Fix: total_items should be sum of quantities, not len(df) * sum
        total_items = int(df['Miktar'].sum())
        processed_items = 0

        # Corner-point algorithm instead of brute-force O(n³) cm-by-cm scanning.
        # This avoids the massive 3D boolean array allocation and is much faster.
        placed_boxes = []
        placed_items = []
        available_positions = [(0, 0, 0)]

        def fits(x, y, z, l, w, h):
            if (x + l > container_length or y + w > container_width
                    or z + h > container_height):
                return False
            for bx, by, bz, bl, bw, bh in placed_boxes:
                if (x < bx + bl and x + l > bx
                        and y < by + bw and y + w > by
                        and z < bz + bh and z + h > bz):
                    return False
            return True

        for _, row in df.iterrows():
            l = int(row['Uzunluk (cm)'])
            w = int(row['Genişlik (cm)'])
            h = int(row['Yükseklik (cm)'])
            weight = float(row['Ağırlık (kg)'])
            color = product_colors[row['Ürün Adı']]

            for _ in range(int(row['Miktar'])):
                # Weight limit check
                if total_weight + weight > max_weight:
                    self.warning.emit(f'{row["Ürün Adı"]} - ağırlık kapasitesi aşıldı!')
                    break

                placed = False
                # Sort positions: prefer bottom (z), then back (y), then left (x)
                sorted_positions = sorted(available_positions, key=lambda p: (p[2], p[1], p[0]))

                for pos in sorted_positions:
                    px, py, pz = pos
                    if fits(px, py, pz, l, w, h):
                        placed_boxes.append((px, py, pz, l, w, h))
                        placed_items.append({
                            'x': px, 'y': py, 'z': pz,
                            'l': l, 'w': w, 'h': h,
                            'color': color, 'name': row['Ürün Adı']
                        })

                        # Add new corner positions for future items
                        new_positions = [
                            (px + l, py, pz),
                            (px, py + w, pz),
                            (px, py, pz + h),
                        ]
                        for new_pos in new_positions:
                            if new_pos not in available_positions:
                                available_positions.append(new_pos)

                        volume = (l * w * h) / 1000000
                        total_volume += volume
                        total_weight += weight
                        product_volumes[row['Ürün Adı']] += volume
                        product_weights[row['Ürün Adı']] += weight

                        placed = True
                        break

                if not placed:
                    self.warning.emit(f'{row["Ürün Adı"]} ürünü konteynere sığmıyor!')
                    break

                processed_items += 1
                if total_items > 0:
                    self.progress.emit(int((processed_items / total_items) * 100))

        container_volume = container_length * container_width * container_height / 1000000
        results = {
            'placed_items': placed_items,
            'product_colors': product_colors,
            'product_volumes': product_volumes,
            'product_weights': product_weights,
            'total_volume': total_volume,
            'total_weight': total_weight,
            'remaining_volume': container_volume - total_volume,
            'remaining_weight': max_weight - total_weight,
            'container_length': container_length,
            'container_width': container_width,
            'container_height': container_height,
            'vehicle': self.vehicle,
        }

        self.result_ready.emit(results)

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QPushButton, QComboBox, QLabel, QHBoxLayout, QAbstractItemView, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from data_processing import LoadThread
from utils import paste_data, clear_layout
from visualization import create_canvas

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

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setOrientation(Qt.Vertical)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")

        self.canvas, self.ax = create_canvas()

        self.zoom_in_button = QPushButton()
        self.zoom_in_button.setIcon(QIcon("zoom_in.png"))
        self.zoom_in_button.setIconSize(QPixmap("zoom_in.png").scaled(20, 20).size())
        self.zoom_in_button.setFixedSize(40, 40)
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_out_button = QPushButton()
        self.zoom_out_button.setIcon(QIcon("zoom_out.png"))
        self.zoom_out_button.setIconSize(QPixmap("zoom_out.png").scaled(20, 20).size())
        self.zoom_out_button.setFixedSize(40, 40)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.progress_bar)
        control_layout.addStretch()
        control_layout.addWidget(self.zoom_in_button)
        control_layout.addWidget(self.zoom_out_button)

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
        self.progress_bar.setValue(100)  # Progress bar should reach 100%
        self.load_thread.result_plot()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ContainerLoadingApp()
    window.show()
    sys.exit(app.exec_())

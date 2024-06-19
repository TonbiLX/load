import sys
from PyQt5.QtWidgets import QApplication
from data_processing import ContainerLoadingApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContainerLoadingApp()
    window.show()
    sys.exit(app.exec_())

import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem, QApplication

def paste_data(table):
    clipboard = QApplication.clipboard()
    data = clipboard.text()
    rows = data.split('\n')
    for i, row in enumerate(rows):
        if row.strip() == '':
            continue
        cells = row.split('\t')
        for j, cell in enumerate(cells):
            if i < table.rowCount() and j < table.columnCount():
                table.setItem(i, j, QTableWidgetItem(cell))

def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

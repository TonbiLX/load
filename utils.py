from PyQt5.QtWidgets import QApplication, QTableWidgetItem

def paste_data(table):
    clipboard = QApplication.clipboard()
    data = clipboard.text()
    rows = data.split('\n')
    for row_index, row_data in enumerate(rows):
        columns = row_data.split('\t')
        for col_index, column_data in enumerate(columns):
            table.setItem(row_index, col_index, QTableWidgetItem(column_data))

def clear_layout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())

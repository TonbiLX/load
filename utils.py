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
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item.widget():
            item.widget().deleteLater()

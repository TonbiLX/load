from PyQt5.QtWidgets import QApplication, QTableWidgetItem

def paste_data(table):
    clipboard = QApplication.clipboard()
    data = clipboard.text()
    rows = data.split('\n')
    current_row = table.currentRow()
    current_col = table.currentColumn()

    for row in rows:
        columns = row.split('\t')
        for col in columns:
            item = QTableWidgetItem(col)
            table.setItem(current_row, current_col, item)
            current_col += 1
        current_row += 1
        current_col = table.currentColumn()

def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

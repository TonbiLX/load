from PyQt5.QtWidgets import QTableWidgetItem, QApplication


def paste_data(table):
    clipboard = QApplication.clipboard()
    data = clipboard.text()
    rows = data.split('\n')

    # Use current selection as paste start point
    selected = table.selectedIndexes()
    start_row = selected[0].row() if selected else 0
    start_col = selected[0].column() if selected else 0

    for i, row in enumerate(rows):
        if row.strip() == '':
            continue
        cells = row.split('\t')
        for j, cell in enumerate(cells):
            target_row = start_row + i
            target_col = start_col + j
            if target_row < table.rowCount() and target_col < table.columnCount():
                table.setItem(target_row, target_col, QTableWidgetItem(cell))


def clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())

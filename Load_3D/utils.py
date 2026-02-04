from PyQt5.QtWidgets import QApplication, QTableWidgetItem


def paste_data(table):
    clipboard = QApplication.clipboard()
    data = clipboard.text()
    rows = data.split('\n')

    # Use current selection as paste start point
    selected = table.selectedIndexes()
    start_row = selected[0].row() if selected else 0
    start_col = selected[0].column() if selected else 0

    for row_index, row_data in enumerate(rows):
        if row_data.strip() == '':
            continue
        columns = row_data.split('\t')
        for col_index, column_data in enumerate(columns):
            target_row = start_row + row_index
            target_col = start_col + col_index
            if target_row < table.rowCount() and target_col < table.columnCount():
                table.setItem(target_row, target_col, QTableWidgetItem(column_data))


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())

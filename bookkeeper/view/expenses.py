""" Модуль описывает виджет-таблицу расходов """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-many-instance-attributes
# mypy: disable-error-code="attr-defined"
from typing import Any, Iterable
from collections.abc import Callable
from PySide6 import QtWidgets
from PySide6 import QtCore


from bookkeeper.view.group_widgets import GroupLabel
from bookkeeper.models.expense import Expense


class ExpensesTableWidget(QtWidgets.QTableWidget):
    """ Виджет-таблица расходов """
    def __init__(self,
                 exp_modifier: Callable[[int, str, str], None],
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.data: list[list[Any]] = []
        self.exp_modifier = exp_modifier
        self.setColumnCount(5)
        self.setRowCount(50)
        self.headers = "Дата Сумма Категория Комментарий Выбор".split()
        self.col_to_attr = {0: "expense_date", 1: "amount", 2: "category", 3: "comment"}
        self.setHorizontalHeaderLabels(self.headers)
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.cellDoubleClicked.connect(self.double_click)

    # pylint: disable=unused-argument
    def double_click(self, row: int, column: int) -> None:
        """ Обрабатывает двойное нажатие на ячейку """
        self.cellChanged.connect(self.cell_changed)

    def cell_changed(self, row: int, column: int) -> None:
        """ Обрабатывает изменение ячейки """
        self.cellChanged.disconnect(self.cell_changed)
        pk = int(self.data[row][-1])
        new_val = self.item(row, column).text()
        attr = self.col_to_attr[column]
        self.exp_modifier(pk, attr, new_val)

    def add_data(self, data: list[list[Any]]) -> None:
        """ Добавляет данные в таблицу """
        self.data = data
        for i_row, row in enumerate(data):
            for j_col, text in enumerate(row[:-1]):
                self.setItem(
                    i_row, j_col,
                    QtWidgets.QTableWidgetItem(text.capitalize())
                )
            cb = QtWidgets.QTableWidgetItem()
            cb.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            cb.setCheckState(QtCore.Qt.CheckState.Unchecked)
            #cb.setCheckState(QtWidgets.CheckState.Unchecked)
            self.setItem(i_row, 4, cb)
        


class ExpensesTableGroup(QtWidgets.QGroupBox):
    """ Группа с таблицей расходов """
    def __init__(self,
                 catpk_to_name: Callable[[int], str],
                 exp_modifier: Callable[[int, str, str], None],
                 exp_deleter: Callable[[Iterable[int]], None],
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.data: list[list[Any]] = []
        self.expenses: list[Expense] = []
        self.catpk_to_name = catpk_to_name
        self.exp_deleter = exp_deleter
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabel("<b>Последние траты</b>")
        self.vbox.addWidget(self.label)
        self.table = ExpensesTableWidget(exp_modifier)
        self.vbox.addWidget(self.table)
        self.del_button = QtWidgets.QPushButton('Удалить выбранные траты')
        self.del_button.clicked.connect(self.delete_expenses)
        self.vbox.addWidget(self.del_button)
        self.setLayout(self.vbox)

    def set_expenses(self, exps: list[Expense]) -> None:
        """ Устанавлиявает список трат """
        self.expenses = exps
        self.data = self.exps_to_data(self.expenses)
        self.table.clearContents()
        self.table.add_data(self.data)
        

    def exps_to_data(self, exps: list[Expense]) -> list[list[Any]]:
        """ Конвертирует объекты трат в данные для таблицы """
        data = []
        for exp in exps:
            item = ["", "", "", "", exp.pk]
            if exp.expense_date:
                item[0] = str(exp.expense_date)
            if exp.amount:
                item[1] = str(exp.amount)
            if exp.category:
                item[2] = str(
                    self.catpk_to_name(exp.category))
            if exp.comment:
                item[3] = str(exp.comment)
            data.append(item)
        return data

    def delete_expenses(self) -> None:
        """ Вызывает удаление выделенных трат """
        for row in range(self.table.rowCount()):
            if self.table.item(row, 4) and self.table.item(row, 4).checkState() == QtCore.Qt.CheckState.Checked :
                self.table.item(row, 4).setSelected(True)

        pks_to_del = []
        chosen_ranges = self.table.selectedRanges()
                
                
        for ch_range in chosen_ranges:
            start = ch_range.topRow()
            end = min(ch_range.bottomRow(), len(self.data))
            pks_to_del += [i[-1] for i in self.data[start:end+1]]
        self.exp_deleter(set(pks_to_del))

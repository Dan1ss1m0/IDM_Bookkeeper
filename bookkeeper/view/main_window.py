""" Модуль описывает главное окно """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# mypy: disable-error-code="attr-defined,union-attr"
from typing import Any
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QEvent

from bookkeeper.view.budget import BudgetTableGroup
from bookkeeper.view.new_expense import NewExpenseGroup
from bookkeeper.view.expenses import ExpensesTableGroup
from bookkeeper.view.group_widgets import LabeledCheckBox


class MainWindow(QtWidgets.QWidget):
    """ Главное окно приложения """

    def __init__(self,
                 budget_table: BudgetTableGroup,
                 new_expense: NewExpenseGroup,
                 expenses_table: ExpensesTableGroup,
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Bookkeeper")
        # Бюджет
        self.budget_table = budget_table
        self.vbox.addWidget(self.budget_table, stretch=3)
        # Новая трата
        self.new_expense = new_expense
        self.vbox.addWidget(self.new_expense, stretch=1)
        # Расходы
        self.expenses_table = expenses_table
        self.vbox.addWidget(self.expenses_table, stretch=6)
        self.setLayout(self.vbox)


    # pylint: disable=invalid-name
    def closeEvent(self, event: QEvent) -> None:
        """ Диалоговое окно при закрытии приложения """
        reply = QtWidgets.QMessageBox.question(
            self,
            'Закрыть приложение',
            "Вы уверены?\n"
            + "Все несохраненные данные будут потеряны.")
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            app = QtWidgets.QApplication.instance()
            app.closeAllWindows()
        else:
            event.ignore()

""" Модуль описывает группу с добавлением новой траты """
# pylint: disable = no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-many-instance-attributes
# mypy: disable-error-code="attr-defined"
from typing import Any
from collections.abc import Callable
from PySide6 import QtWidgets

from bookkeeper.view.group_widgets import GroupLabel, \
                                          LabeledComboBoxInput, \
                                          LabeledLineInput
from bookkeeper.models.category import Category


class NewExpenseGroup(QtWidgets.QGroupBox):
    """ Группа виджетов добавления новой траты """
    def __init__(self, cats: list[Category],
                 cats_edit_show: Callable[[], None],
                 exp_adder: Callable[[str, str, str], None],
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.cats_edit_show = cats_edit_show
        self.exp_adder = exp_adder
        self.grid = QtWidgets.QGridLayout()
        self.label = GroupLabel("<b>Новая трата</b>")
        self.grid.addWidget(self.label, 0, 0, 1, 5)
        self.amount_input = LabeledLineInput("Сумма", "0")
        self.grid.addWidget(self.amount_input, 1, 0, 1, 4)
        self.category_input = LabeledComboBoxInput("Категория", [])
        self.grid.addWidget(self.category_input, 2, 0, 1, 4)
        self.cats_edit_button = QtWidgets.QPushButton("Редактировать")
        self.cats_edit_button.clicked.connect(self.cats_edit_show)
        self.grid.addWidget(self.cats_edit_button, 2, 4, 1, 1)
        self.comment_input = LabeledLineInput("Комментарий", "")
        self.grid.addWidget(self.comment_input, 3, 0, 1, 4)
        self.submit_button = QtWidgets.QPushButton("Добавить")
        self.submit_button.clicked.connect(self.add_expense)
        self.grid.addWidget(self.submit_button, 4, 0, 1, 5)
        self.setLayout(self.grid)
        self.set_categories(cats)

    def set_categories(self, cats: list[Category]) -> None:
        """ Устанавливает список категорий """
        self.categories = cats
        self.cat_names = [c.name for c in cats]
        self.category_input.set_items(self.cat_names)

    def add_expense(self) -> None:
        """ Вызывает добавление новой траты """
        self.exp_adder(self.amount_input.text(),
                       self.category_input.text(),
                       self.comment_input.text())
        self.amount_input.clear()
        self.category_input.clear()
        self.comment_input.clear()

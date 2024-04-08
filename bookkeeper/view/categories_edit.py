""" Модуль описывает окно редактирования списка категорий """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-many-instance-attributes
# mypy: disable-error-code="attr-defined"
from collections.abc import Callable
from typing import Any
from PySide6 import QtWidgets

from bookkeeper.view.group_widgets import GroupLabel, \
    LabeledComboBoxInput, \
    LabeledLineInput
from bookkeeper.models.category import Category


class CategoriesEditWindow(QtWidgets.QWidget):
    """ Окно редактирования списка категорий """

    def __init__(self, cats: list[Category],
                 cat_adder: Callable[[str, str | None], None],
                 cat_modifier: Callable[[str, str, str | None], None],
                 cat_deleter: Callable[[str], None],
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.cat_checker: Callable[[str], None] = lambda name: None
        self.grid = QtWidgets.QGridLayout()
        self.label = GroupLabel("<b>Список категорий</b>")
        self.grid.addWidget(self.label, 0, 0, 1, 2)
        self.cats_tree = QtWidgets.QTreeWidget()
        self.cats_tree.setHeaderLabel("")
        self.cats_tree.itemDoubleClicked.connect(self.double_clicked)
        self.grid.addWidget(self.cats_tree, 1, 0, 1, 2)
        self.label = GroupLabel("<b>Действия с выбранной категорией</b>")
        self.grid.addWidget(self.label, 2, 0, 1, 2)
        self.cat_sel = LabeledComboBoxInput("Категория", [])
        self.grid.addWidget(self.cat_sel, 3, 0, 1, 1)
        self.cat_del_button = QtWidgets.QPushButton('Удалить')
        self.cat_del_button.clicked.connect(self.delete_category)
        self.grid.addWidget(self.cat_del_button, 3, 1, 1, 1)
        self.cat_mod_parent = LabeledComboBoxInput("Новый родитель", [])
        self.grid.addWidget(self.cat_mod_parent, 5, 0, 1, 1)
        self.cat_mod_name = LabeledLineInput("Новое название", "")
        self.grid.addWidget(self.cat_mod_name, 6, 0, 1, 1)
        self.cat_mod_button = QtWidgets.QPushButton('Изменить')
        self.cat_mod_button.clicked.connect(self.modify_category)
        self.grid.addWidget(self.cat_mod_button, 6, 1, 1, 1)
        self.label = GroupLabel("<b>Добавление новой категории</b>")
        self.grid.addWidget(self.label, 7, 0, 1, 2)
        self.cat_add_parent = LabeledComboBoxInput("Родитель", [])
        self.grid.addWidget(self.cat_add_parent, 8, 0, 1, 1)
        self.cat_add_name = LabeledLineInput("Название", "Новая категория")
        self.grid.addWidget(self.cat_add_name, 9, 0, 1, 1)
        self.cat_add_button = QtWidgets.QPushButton('Добавить')
        self.grid.addWidget(self.cat_add_button, 9, 1, 1, 1)
        self.cat_add_button.clicked.connect(self.add_category)
        self.setLayout(self.grid)
        self.cat_adder = cat_adder
        self.cat_modifier = cat_modifier
        self.cat_deleter = cat_deleter
        self.set_categories(cats)

    def set_categories(self, cats: list[Category]) -> None:
        """ Устанавливает список категорий """
        self.categories = cats
        self.cat_names = [c.name for c in cats]
        top_items = self._find_children()
        self.cats_tree.clear()
        self.cats_tree.insertTopLevelItems(0, top_items)
        self.cat_sel.set_items(self.cat_names)
        self.cat_add_parent.set_items(["- Без родительской категории -"]
                                      + self.cat_names)
        self.cat_mod_parent.set_items(["- Без родительской категории -"]
                                      + self.cat_names)

    def delete_category(self) -> None:
        """ Вызывает удаление категории """
        self.cat_deleter(self.cat_sel.text())
        self.cat_sel.clear()
        self.cat_mod_name.clear()
        self.cat_mod_parent.clear()

    def set_cat_checker(self, checker: Callable[[str], None]) -> None:
        """ Устанавливает функцию проверки категории """
        self.cat_checker = checker

    def add_category(self) -> None:
        """ Вызывает добавление категории """
        parent_name = self.cat_add_parent.text()
        if parent_name == "- Без родительской категории -":
            self.cat_adder(self.cat_add_name.text(), None)
        else:
            self.cat_checker(parent_name)
            self.cat_adder(self.cat_add_name.text().lower(), self.cat_add_parent.text())
        self.cat_add_name.clear()
        self.cat_add_parent.clear()

    def modify_category(self) -> None:
        """ Вызывает изменение категории """
        new_parent_name = self.cat_mod_parent.text().lower()
        if new_parent_name == "- без родительской категории -":
            self.cat_modifier(self.cat_sel.text().lower(),
                              self.cat_mod_name.text().lower(),
                              None)
        else:
            self.cat_checker(new_parent_name)
            self.cat_modifier(self.cat_sel.text().lower(),
                              self.cat_mod_name.text().lower(),
                              new_parent_name)
        self.cat_mod_name.clear()
        self.cat_mod_parent.clear()
        self.cat_sel.clear()

    def _find_children(self, parent_pk: int | None = None) \
            -> list[QtWidgets.QTreeWidgetItem]:
        """ Находит подкатегории по pk родителя """
        items = []
        children = [c for c in self.categories if c.parent == parent_pk]
        for child in children:
            item = QtWidgets.QTreeWidgetItem([child.name])
            item.addChildren(self._find_children(parent_pk=child.pk))
            items.append(item)
        return items

    def double_clicked(self, item: QtWidgets.QTreeWidgetItem,
                       column: int) -> None:
        """
        Обрабатывает двойное нажатие на категорию в дереве:
        устанавливает выбранную категорию для удаления,
        изменения и добавления подкатегории
        """
        clicked_cat_name = item.text(column)
        item_parent = item.parent()
        if item_parent is None:
            clicked_cat_parent = "- Без родительской категории -"
        else:
            clicked_cat_parent = item.parent().text(column)
        self.cat_sel.set_text(clicked_cat_name)
        self.cat_add_parent.set_text(clicked_cat_name)
        self.cat_mod_name.set_text(clicked_cat_name)
        self.cat_mod_parent.set_text(clicked_cat_parent)

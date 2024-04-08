""" Модуль описывает View модели MVP на основе GUI PySide6 """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=attribute-defined-outside-init
# mypy: disable-error-code="attr-defined,union-attr,call-arg"
from collections.abc import Callable
from typing import Any, Iterable
from PySide6 import QtWidgets

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.view.main_window import MainWindow
from bookkeeper.view.budget import BudgetTableGroup
from bookkeeper.view.new_expense import NewExpenseGroup
from bookkeeper.view.expenses import ExpensesTableGroup
from bookkeeper.view.categories_edit import CategoriesEditWindow


def handle_error(widget: QtWidgets.QWidget,
                 handler: Any
                 ) -> Callable[[Any], None]:
    """ Вызывает окно ошибки при исключении ValueError """
    def inner(*args: Any, **kwargs: Any) -> None:
        try:
            handler(*args, **kwargs)
        except ValueError as err:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(err))
    return inner


class View:

    def __init__(self) -> None:
        self.categories: list[Category] = []
        self.expenses: list[Expense] = []
        self.budgets: list[Budget] = []
        self.config_app()
        self.config_cats_edit()
        self.budget_table = BudgetTableGroup(self.modify_budget)
        self.new_expense = NewExpenseGroup(self.categories,
                                           self.cats_edit_window.show,
                                           self.add_expense)
        self.expenses_table = ExpensesTableGroup(self.catpk_to_name,
                                                 self.modify_expense,
                                                 self.delete_expenses)
        self.config_main_window()

    def config_app(self) -> None:
        """ Конфигупация приложения """
        self.app = QtWidgets.QApplication.instance()

    def config_main_window(self) -> None:
        """ Конфигурирации главного окна """
        self.main_window = MainWindow(self.budget_table, self.new_expense, self.expenses_table)
        self.main_window.resize(600, 700)

    def config_cats_edit(self) -> None:
        """ Конфигурирации окна изменения списка категорий """
        self.cats_edit_window = CategoriesEditWindow(self.categories,
                                                     self.add_category,
                                                     self.modify_category,
                                                     self.delete_category)
        self.cats_edit_window.setWindowTitle("Редактирование категорий")
        self.cats_edit_window.resize(600, 550)

    def set_categories(self, cats: list[Category]) -> None:
        """ Устанавливка списка категорий """
        self.categories = cats
        self.new_expense.set_categories(self.categories)
        self.cats_edit_window.set_categories(self.categories)

    def catpk_to_name(self, pk: int) -> str:
        """ Получение названия категории по pk (primary key) """
        name = [c.name for c in self.categories if int(c.pk) == int(pk)]
        if len(name):
            return str(name[0])
        return ""

    def set_cat_adder(self, handler: Callable[[str, str | None], None]) -> None:
        """ Метод добавления категории """
        self.cat_adder = handle_error(self.main_window, handler)

    def set_cat_modifier(self, handler: Callable[[str, str, str | None], None]) -> None:
        """ Метод изменения категории """
        self.cat_modifier = handle_error(self.main_window, handler)

    def set_cat_deleter(self, handler: Callable[[str], None]) -> None:
        """ Метод удаления категории """
        self.cat_deleter = handle_error(self.main_window, handler)

    def set_cat_checker(self, handler: Callable[[str], None]) -> None:
        """ Метод проверки существования категории """
        self.cat_checker = handle_error(self.main_window, handler)
        self.cats_edit_window.set_cat_checker(self.cat_checker)

    def add_category(self, name: str, parent: str | None) -> None:
        """ Вызов функции добавления категории """
        self.cat_adder(name, parent)

    def modify_category(self, cat_name: str, new_name: str,
                        new_parent: str | None) -> None:
        """ Вызов функции изменения категории """
        self.cat_modifier(cat_name, new_name, new_parent)

    def delete_category(self, cat_name: str) -> None:
        """ Вызов функции удаления категории """
        self.cat_deleter(cat_name)

    def set_expenses(self, exps: list[Expense]) -> None:
        """ Устанавка списка трат """
        self.expenses = exps
        self.expenses_table.set_expenses(self.expenses)

    def set_exp_adder(self, handler: Callable[[str, str, str], None]) -> None:
        """ Метод добавления траты """
        self.exp_adder = handle_error(self.main_window, handler)

    def set_exp_deleter(self, handler: Callable[[set[int]], None]) -> None:
        """Метод удаления трат """
        self.exp_deleter = handle_error(self.main_window, handler)

    def set_exp_modifier(self, handler: Callable[[int, str, str], None]) -> None:
        """ Метод изменения траты """
        self.exp_modifier = handle_error(self.main_window, handler)

    def add_expense(self, amount: str, cat_name: str, comment: str = "") -> None:
        """ Вызов функции добавления траты """
        self.exp_adder(amount, cat_name, comment)

    def delete_expenses(self, exp_pks: Iterable[int]) -> None:
        """ Вызов функции удаления траты """
        if len(list(exp_pks)) == 0:
            QtWidgets.QMessageBox.critical(self.main_window,
                                           'Ошибка',
                                           'Траты для удаления не выбраны.')
        else:
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                'Удаление трат',
                'Вы уверены, что хотите удалить все выбранные траты?')
            if reply == QtWidgets.QMessageBox.Yes:
                self.exp_deleter(exp_pks)

    def modify_expense(self, pk: int, attr: str, new_val: str) -> None:
        """ Вызывает функцию изменения траты """
        self.exp_modifier(pk, attr, new_val)

    def set_budgets(self, budgets: list[Budget]) -> None:
        """ Список бюджетов """
        self.budgets = budgets
        data = [[str(self.budgets[0].daily), str(self.budgets[0].daily_spents), str(int(self.budgets[0].daily) - int(self.budgets[0].daily_spents))], 
                [str(self.budgets[0].weekly), str(self.budgets[0].weekly_spents), str(int(self.budgets[0].weekly) - int(self.budgets[0].weekly_spents))],
                [str(self.budgets[0].mounthly), str(self.budgets[0].mounthly_spents), str(int(self.budgets[0].mounthly) - int(self.budgets[0].mounthly_spents))]]
        self.budget_table.set_budgets(data)

    def set_bdg_modifier(self,
                         handler: Callable[['int | None', str, str], None]
                         ) -> None:
        """Метод изменения бюджета (из bookkeeper_app)"""
        self.bdg_modifier = handle_error(self.main_window, handler)

    def modify_budget(self, new_limit: str, period: str) -> None:
        """ Вызов функции изменения бюджета """
        self.bdg_modifier(new_limit, period)

    def deadline(self) -> None:
        """ Вызов окна предупреждения в случае превышения бюджета """
        msg = "Лимит трат превышен!"
        QtWidgets.QMessageBox.warning(self.main_window, 'ВНИМАНИЕ!', msg)

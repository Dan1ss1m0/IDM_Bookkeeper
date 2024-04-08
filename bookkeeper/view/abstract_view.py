""" Модуль описывает протокол View модели MVP """
from typing import Protocol, Iterable
from collections.abc import Callable

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


class AbstractView(Protocol):
    """ Протокол View модели MVP """

    def set_categories(self, cats: list[Category]) -> None:
        """ устанавливает список категорий """

    def set_expenses(self, cats: list[Expense]) -> None:
        """ устанавливает список трат """

    def set_budgets(self, cats: list[Budget]) -> None:
        """ устанавливает список бюджетов """

    def set_cat_adder(self, handler: Callable[[str, str | None], None]) -> None:
        """ устанавливает функцию добавления категории """

    def set_cat_deleter(self, handler: Callable[[str], None]) -> None:
        """ устанавливает функцию удаления категории """

    def set_cat_checker(self, handler: Callable[[str], None]) -> None:
        """ устанавливает функцию проверки названия категории """

    def set_bdg_modifier(self, handler: Callable[['int | None', str, str],
                                                 None]) -> None:
        """
        устанавливает функцию изменения (удаления, добавления) бюджета
        """

    def set_exp_adder(self, handler: Callable[[str, str, str], None]) -> None:
        """ устанавливает функцию добавления траты """

    def set_exp_deleter(self, handler: Callable[[Iterable[int]], None]) -> None:
        """ устанавливает функцию удаления траты """

    def set_exp_modifier(self, handler: Callable[[int, str, str], None]) -> None:
        """ устанавливает функцию изменения траты """

    def death(self) -> None:
        """ устанавливает функцию превышения бюджета """

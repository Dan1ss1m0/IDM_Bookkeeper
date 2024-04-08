"""
Модуль описывает реализацию Presenter из модели MVP
"""
# mypy: disable-error-code="attr-defined"
from datetime import datetime
from typing import Any, Iterable
from collections.abc import Callable

from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


class Bookkeeper:
    """
    Presenter из модели MVP; работает с любым типом репозитория,
    наследованным от AbstractRepository; работает с GUI,
    основанным на протоколе AbstartView
    """

    def __init__(self,
                 view: AbstractView,
                 repository_factory: Callable[[Any], Any]):
        self.view = view
        self.category_rep = repository_factory(Category)
        self.categories = self.category_rep.get_all()
        self.view.set_categories(self.categories)
        self.view.set_cat_adder(self.add_category)
        self.view.set_cat_modifier(self.modify_category)
        self.view.set_cat_deleter(self.delete_category)
        self.view.set_cat_checker(self.cat_checker)

        self.budgets: list[Budget] = []
        self.budget_rep = repository_factory(Budget)
        self.view.set_bdg_modifier(self.modify_budget)

        self.expense_rep = repository_factory(Expense)
        self.update_expenses()
        self.view.set_exp_adder(self.add_expense)
        self.view.set_exp_deleter(self.delete_expenses)
        self.view.set_exp_modifier(self.modify_expense)

    def show(self) -> None:
        """ Включает отображение view на экране """
        self.view.main_window.show()

    def cat_checker(self, cat_name: str) -> None:
        """ Проверяет, что имя категории (cat_name) есть в репозитории """
        if cat_name not in [c.name for c in self.categories]:
            raise ValueError(f'Категории "{cat_name}" не существует')

    def add_category(self, name: str, parent: str | None) -> None:
        """ Добавляет категорию с названием name и названием родителя parent"""
        if name in [c.name for c in self.categories]:
            raise ValueError(f'Категория "{name}" уже существует')
        if parent is not None:
            if parent not in [c.name for c in self.categories]:
                raise ValueError(f'Категории "{parent}" не существует')
            parent_pk = self.category_rep.get_all_like(like = None, where={'name': parent})[0].pk
        else:
            parent_pk = None
        cat = Category(name, parent_pk)
        self.category_rep.add(cat)
        self.categories = self.category_rep.get_all()
        self.view.set_categories(self.categories)

    def modify_category(self, cat_name: str, new_name: str,
                        new_parent: str | None) -> None:
        """ Изменяет имя и родителя категории """
        if cat_name not in [c.name for c in self.categories]:
            raise ValueError(f'Категории "{cat_name}" не существует')
        if new_name != cat_name:
            if new_name in [c.name for c in self.categories]:
                raise ValueError(f'Категория "{new_name}" уже существует')
        if new_parent is not None:
            if new_parent not in [c.name for c in self.categories]:
                raise ValueError(f'Категории "{new_parent}" не существует')
            parent_pk = self.category_rep.get_all(where={'name': new_parent})[0].pk
        else:
            parent_pk = None
        cat = self.category_rep.get_all_like(like= None, where={'name': cat_name})[0]
        cat.name = new_name
        cat.parent = parent_pk
        self.category_rep.update(cat)
        self.categories = self.category_rep.get_all()
        self.view.set_categories(self.categories)

    def delete_category(self, cat_name: str) -> None:
        """ Удаляет категорию с названием cat_name """
        cat = self.category_rep.get_all_like(like= None, where={"name": cat_name})
        if len(cat) == 0:
            raise ValueError(f'Категории "{cat_name}" не существует')
        cat = cat[0]
        self.category_rep.delete(cat.pk)
        # меняет удаленную категорию на родителя (None если родителя нет)
        for child in self.category_rep.get_all_like(like= None, where={'parent': cat.pk}):
            child.parent = cat.parent
            self.category_rep.update(child)
        self.categories = self.category_rep.get_all()
        self.view.set_categories(self.categories)
        # устанавливает None вместо удаленной категории
        for exp in self.expense_rep.get_all_like(like= None, where={'category': cat.pk}):
            exp.category = None
            self.expense_rep.update(exp)
        self.update_expenses()

    def update_expenses(self) -> None:
        """ Обновляет список трат и то, что он него зависит """
        self.expenses = self.expense_rep.get_all()
        self.view.set_expenses(self.expenses)
        self.update_budgets()

    def add_expense(self, amount: str,
                    cat_name: str,
                    comment: str = "") -> None:
        """
        Добавляет трату на сумму amount в категории cat_name
        c комментарием comment
        """
        try:
            amount_int = int(amount)
        except ValueError as err:
            raise ValueError('Сумма должна быть целым числом.') from err
        if amount_int <= 0:
            raise ValueError('Сумма покупки должна быть положительной')
        cat = self.category_rep.get_all_like(like= None, where={'name': cat_name})
        if len(cat) == 0:
            raise ValueError(f'Категории "{cat_name}" не существует')
        cat = cat[0]
        new_exp = Expense(amount_int, cat.pk, comment=comment)
        self.expense_rep.add(new_exp)
        self.update_expenses()
        if (int(self.budgets[0].daily) < int(self.budgets[0].daily_spents)):
            self.view.deadline()

    def modify_expense(self, pk: int, attr: str, new_val: str) -> None:
        """
        Изменяет трату по id (pk):
        устанавливает в атрибут attr новое значение new_val
        """
        exp = self.expense_rep.get(pk)
        print('exp1', exp)
        if attr == "category":
            val_cat = new_val.lower()
            if val_cat not in [c.name for c in self.categories]:
                self.view.set_expenses(self.expenses)
                raise ValueError(f'Категории "{val_cat}" не существует')
            val_cat = self.category_rep.get_all(where={'name': val_cat})[0].pk
            setattr(exp, attr, val_cat)
        elif attr == "amount":
            try:
                val_amnt = int(new_val)
            except ValueError as err:
                raise ValueError('Сумма должна быть целым числом.') from err
            if val_amnt <= 0:
                self.view.set_expenses(self.expenses)
                raise ValueError('Записываются только траты')
            setattr(exp, attr, val_amnt)
        elif attr == "expense_date":
            try:
                val_date = datetime.fromisoformat(new_val).isoformat(
                    sep='\t', timespec='minutes')
            except ValueError as err:
                self.view.set_expenses(self.expenses)
                raise ValueError('Неправильный формат даты.') from err
            setattr(exp, attr, val_date)
        else:
            setattr(exp, attr, new_val)
        self.expense_rep.update(exp)
        exp = self.expense_rep.get(pk)
        self.update_expenses()

    def delete_expenses(self, exp_pks: Iterable[int]) -> None:
        """ Удаляет траты по списку id (exp_pks) """
        for pk in exp_pks:
            self.expense_rep.delete(pk)
        self.update_expenses()

    def update_budgets(self) -> None:
        """ Обновляет список бюджетов и то, что от него зависит """
        for budget in self.budget_rep.get_all():
            print('Budget1', budget)
            budget.update_spent(self.expense_rep)
            self.budget_rep.update(budget)
        self.budgets = self.budget_rep.get_all()
        self.view.set_budgets(self.budgets)

    def modify_budget(self,
                      new_limit: str,
                      period: str) -> None:
        """
        Изменяет бюджет по id (pk):
        - удаляет бюджет если новый лимит пустой: new_limit==""
        - добавляет бюджет с ограничением new_limit на период period,
        если pk == None (нет в репозитории)
        - изменяяет бюджет, если pk != None (есть в репозитории)
        """
        # добавление
        try:
            new_limit_int = int(new_limit)
        except ValueError as err:
            #self.update_budgets()
            raise ValueError('Неправильный формат.\n'
                             + 'Введите сумму целым числом.') from err
        if new_limit_int < 0:
            self.update_budgets()
            raise ValueError('Введите положительное число')
        
        else:
            budget = self.budget_rep.get(1)
            print('budget1' , budget)
            if period == 'day':
                setattr(budget, 'daily', new_limit)
            if period == 'week':
                setattr(budget, 'weekly', new_limit)
            if period == 'mounth':
                setattr(budget, 'mounthly', new_limit)
            self.budget_rep.update(budget)
            budget = self.budget_rep.get(1)
            print('budget2' , budget)
        self.update_budgets()
            
        
        

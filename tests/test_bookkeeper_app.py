"""
Тесты Presenter из модели MVP
"""
from pytestqt.qt_compat import qt_api
import pytest

from bookkeeper.bookkeeper_app import Bookkeeper
from bookkeeper.view.view import View
from bookkeeper.repository.factory import repository_factory
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def bkkpr():
    if qt_api.QtWidgets.QApplication.instance() is None:
        qt_api.QtWidgets.QApplication()
    view = View()
    repo_gen = repository_factory(MemoryRepository)
    b = Bookkeeper(view, repo_gen)
    return b


def test_show(bkkpr):
    def test_show():
        test_show.was_called = True
    test_show.was_called = False
    bkkpr.view.main_window.show = test_show
    bkkpr.show()
    assert test_show.was_called is True


def test_cat_checker(bkkpr):
    with pytest.raises(ValueError):
        bkkpr.cat_checker("test")


def test_categories(bkkpr):
    # добавление
    bkkpr.add_category("cat1", None)
    cat1 = bkkpr.category_rep.get_all(where={"name": "cat1"})
    assert len(cat1) == 1
    cat1 = cat1[0]
    assert cat1.parent is None
    bkkpr.add_category("cat12", "cat1")
    cat12 = bkkpr.category_rep.get_all(where={"name": "cat12"})
    assert len(cat12) == 1
    cat12 = cat12[0]
    assert cat12.parent == cat1.pk
    with pytest.raises(ValueError):
        bkkpr.add_category("cat1", None)
    with pytest.raises(ValueError):
        bkkpr.add_category("cat21", "cat2")
    # изменение
    with pytest.raises(ValueError):
        bkkpr.modify_category("cat2", "", "")
    with pytest.raises(ValueError):
        bkkpr.modify_category("cat1", "", "")
    with pytest.raises(ValueError):
        bkkpr.modify_category("cat1", "cat12", "")
    with pytest.raises(ValueError):
        bkkpr.modify_category("cat1", "cat1", "cat2")
    bkkpr.modify_category("cat12", "cat12new", None)
    cat12 = bkkpr.category_rep.get_all(where={"name": "cat12new"})
    assert len(cat12) != 0
    cat12 = cat12[0]
    assert cat12.parent is None
    bkkpr.modify_category("cat12new", "cat12", "cat1")
    cat12 = bkkpr.category_rep.get_all(where={"name": "cat12"})
    assert len(cat12) != 0
    cat12 = cat12[0]
    assert cat12.parent == cat1.pk
    # удаление
    with pytest.raises(ValueError):
        bkkpr.delete_category("cat2")
    bkkpr.add_expense("100", "cat1")
    bkkpr.delete_category("cat1")
    cat1 = bkkpr.category_rep.get_all(where={"name": "cat1"})
    assert len(cat1) == 0
    cat12 = bkkpr.category_rep.get_all(where={"name": "cat12"})[0]
    assert cat12.parent is None
    exp = bkkpr.expense_rep.get_all()[0]
    assert exp.category is None


def test_expenses(bkkpr):
    # добавление
    with pytest.raises(ValueError):
        bkkpr.add_expense("100", "cat1")
    bkkpr.add_category("cat1", None)
    with pytest.raises(ValueError):
        bkkpr.add_expense("-100", "cat1")
    with pytest.raises(ValueError):
        bkkpr.add_expense("сто руб.", "cat1")
    bkkpr.add_expense("100", "cat1", comment="test")
    exp1 = bkkpr.expense_rep.get_all(where={"comment": "test"})
    assert len(exp1) == 1
    exp1 = exp1[0]
    assert exp1.amount == 100
    assert exp1.comment == "test"
    assert exp1 == bkkpr.expenses[0]
    # превышение бюджета
    bkkpr.modify_budget(None, "101", "day")

    
def test_budgets(bkkpr):
    # добавление
    bkkpr.modify_budget(None, "101", "day")
    bkkpr.modify_budget(None, "1001", "week")
    bkkpr.modify_budget(None, "10001", "month")
    b_day = bkkpr.budget_rep.get_all(where={"period": "day"})
    b_week = bkkpr.budget_rep.get_all(where={"period": "week"})
    b_month = bkkpr.budget_rep.get_all(where={"period": "month"})
    assert len(b_day) == 1
    b_day = b_day[0]
    assert b_day.limitation == 101
    assert len(b_week) == 1
    assert len(b_month) == 1
    # изменение
    bkkpr.modify_budget(b_day.pk, "99", "day")
    b_day = bkkpr.budget_rep.get_all(where={"period": "day"})[0]
    assert b_day.limitation == 99
    with pytest.raises(ValueError):
        bkkpr.modify_budget(b_day.pk, "-1", "day")
    with pytest.raises(ValueError):
        bkkpr.modify_budget(b_day.pk, "мало", "day")
    # удаление
    bkkpr.modify_budget(b_day.pk, "", "day")
    b_day = bkkpr.budget_rep.get_all(where={"period": "day"})
    assert len(b_day) == 0

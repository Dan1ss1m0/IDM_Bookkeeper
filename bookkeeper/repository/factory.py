""" Модуль, реализующий фабрику репозиториев наследованных от AbstractRepository """
from collections.abc import Callable
from typing import Any

from bookkeeper.repository.abstract_repository import Model


def repository_factory(repo_type: Any, db_file: 'str | None' = None) -> \
        Callable[[Model], Any]:
    """
    Возвращает функцию-фабрику репозитория по типу
    repo_gen(model: Model) -> AbstractRepository
    Для реозитория типа SQLiteRepository необходим
    путь к файлу базы данных db_file
    """
    if db_file is None:
        def repo_gen_db(model: Model) -> Any:
            return repo_type[model]()
        return repo_gen_db

    def repo_gen(model: Model) -> Any:
        return repo_type[model](db_file=db_file, cls=model)
    return repo_gen

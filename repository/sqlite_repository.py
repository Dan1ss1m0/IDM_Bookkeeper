"""
Модуль описывает репозиторий, работающий в БД SQLite
"""

from typing import Any
from inspect import get_annotations
import sqlite3

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий c базой данных SQLite.
    """
    db_file: str
    table_name: str
    fields: dict[str, Any]
    obj_cls: type

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.obj_cls = cls

    def add(self, obj: T) -> int | None:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f"You can't add object {obj} with filled `pk` attribute")
        names = ', '.join(self.fields.keys())
        questions = ', '.join("?" * len(self.fields))
        values = [getattr(obj, f) for f in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES({questions})',
                values
            )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

        
    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(
                f'SELECT * FROM {self.table_name} '
                + f'WHERE ROWID=={pk}'
            ).fetchone()
        con.close()
        if row is None:
            return None
        kwargs = dict(zip(self.fields, row))
        obj = self.obj_cls(**kwargs)
        obj.pk = pk
        return obj

    def get_all(self) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            rows = cur.execute(f'SELECT ROWID, * FROM {self.table_name} ').fetchall()
        con.close()
        all_raws = []
        for r in rows:
            kwargs = dict(zip(self.fields, r[1:]))
            obj = self.obj_cls(**kwargs)
            obj.pk = r[0]
            all_raws.append(obj)
        return all_raws

    def get_all_like(self, like: dict[str, str]) -> list[T]:
        values = [f"%{v}%" for v in like.values()]
        where = dict(zip(like.keys(), values))
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            fields = " AND ".join([f"{f} LIKE ?" for f in where.keys()])
            rows = cur.execute(f'SELECT ROWID, * FROM {self.table_name} '+ f'WHERE {fields}',list(where.values())).fetchall()
        con.close()
        all_raws = []
        for r in rows:
            kwargs = dict(zip(self.fields, r[1:]))
            obj = self.obj_cls(**kwargs)
            obj.pk = r[0]
            all_raws.append(obj)
        return all_raws
        

    def update(self, obj: T) -> None:
        fields = ", ".join([f"{f}=?" for f in self.fields.keys()])
        values = [getattr(obj, f) for f in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'UPDATE {self.table_name} SET {fields} '
                + f'WHERE ROWID=={obj.pk}',
                values
            )
            if cur.rowcount == 0:
                raise ValueError("You can't update object with unknown primary key")
        con.close()

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'DELETE FROM  {self.table_name} '
                + f'WHERE ROWID=={pk}'
            )
            if cur.rowcount == 0:
                raise ValueError("You can't delete object with unknown primary key")
        con.close()

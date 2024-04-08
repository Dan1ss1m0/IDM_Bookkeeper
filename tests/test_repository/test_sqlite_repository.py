import pytest
import sqlite3
from dataclasses import dataclass

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.factory import repository_factory


DB_FILE = "database/test_sqlrepo.db"


@pytest.fixture
def create_bd():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute("DROP TABLE custom")
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE custom(f1, f2)")
    con.close()


@pytest.fixture
def custom_class():
    @dataclass
    class Custom():
        f1: int
        f2: str = "f2_value"
        pk: int = 0
    return Custom


@pytest.fixture
def repo(custom_class, create_bd):
    return SQLiteRepository(db_file=DB_FILE, cls=custom_class)


def test_row2obj(repo):
    row = (11, "test_row2obj")
    obj = repo._row2obj(10, row)
    assert obj.pk == 10
    assert obj.f1 == 11
    assert obj.f2 == "test_row2obj"


def test_crud(repo, custom_class):
    # create
    obj_add = custom_class(f1=1, f2="test_crud")
    pk = repo.add(obj_add)
    assert pk == obj_add.pk
    # read
    obj_get = repo.get(pk)
    assert obj_get is not None
    assert obj_get.pk == obj_add.pk
    assert obj_get.f1 == obj_add.f1
    assert obj_get.f2 == obj_add.f2
    # update
    obj_upd = custom_class(f1=11, f2="test_crud_upd", pk=pk)
    repo.update(obj_upd)
    obj_get = repo.get(pk)
    assert obj_get == obj_upd
    # delete
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class(f1=1, pk=1)
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_update_unexistent(repo, custom_class):
    obj = custom_class(f1=1, pk=100)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class(f1=1, pk=0)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_unexistent(repo):
    assert repo.get(-1) is None


def test_cannot_delete_unexistent(repo):
    with pytest.raises(ValueError):
        repo.delete(-1)



def test_factory(custom_class, create_bd):
    repo_gen = repository_factory(SQLiteRepository, db_file=DB_FILE)
    rep = repo_gen(custom_class)
    test_crud(rep, custom_class)

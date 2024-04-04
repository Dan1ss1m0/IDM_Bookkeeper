"""
Главный модуль
"""
# pylint: disable = no-name-in-module
import sys
from PySide6.QtWidgets import QApplication

from bookkeeper.bookkeeper_app import Bookkeeper
from bookkeeper.view.view import View
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.factory import repository_factory


app = QApplication(sys.argv)
view = View()
repo_gen = repository_factory(SQLiteRepository, db_file="database/bookkeeper.db")
bookkeeper_app = Bookkeeper(view, repo_gen)
bookkeeper_app.show()
print("Application is running")
print(f"Application ends with exit status {app.exec()}")
sys.exit()
""" Модуль описывает виджеты, использующиеся в группах виджетов """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="attr-defined,assignment"
from typing import Any
from PySide6.QtCore import Qt
from PySide6 import QtWidgets


class LabeledLineInput(QtWidgets.QWidget):
    """ Виджет поля для ввода с названием """

    def __init__(self, text: str, placeholder: str,
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)
        self.input = QtWidgets.QLineEdit(self.placeholder)
        self.layout.addWidget(self.input, stretch=4)
        self.setLayout(self.layout)  # type: ignore

    def clear(self) -> None:
        """ Устанавливает значение по умолчанию """
        self.input.setText(self.placeholder)

    def set_text(self, text: str) -> None:
        """ Устанавливает текст (text) """
        self.input.setText(text)

    def text(self) -> str:
        """ Возвращает текущий текст """
        return self.input.text()


class LabeledComboBoxInput(QtWidgets.QWidget):
    """ Виджет выпадающего списка для ввода с названием """

    def __init__(self, text: str, items: list[str],
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)
        self.combo_box = QtWidgets.QComboBox()
        # self.combo_box.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.combo_box.setEditable(True)
        self.combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.combo_box.setMaxVisibleItems(16)
        self.set_items(items)
        self.layout.addWidget(self.combo_box, stretch=4)
        self.setLayout(self.layout)  # type: ignore

    def clear(self) -> None:
        """ Устанавливает значение по умолчанию """
        self.combo_box.setCurrentText(self.combo_box.placeholderText())

    def text(self) -> str:
        """ Возвращает текущий текст """
        return self.combo_box.currentText()

    def set_text(self, text: str) -> None:
        """ Устанавливает текст (text) """
        self.combo_box.setCurrentText(text)

    def set_items(self, items: list[str]) -> None:
        """ Устанавливает элементы выпадающего списка """
        self.items = items
        self.combo_box.clear()
        self.combo_box.addItems(items)
        if len(items) != 0:
            self.combo_box.setPlaceholderText(items[0])
        else:
            self.combo_box.setPlaceholderText("")
        self.clear()


class GroupLabel(QtWidgets.QLabel):
    """ Заголовок для группы виджетов """

    def __init__(self, text: str, *args: Any, **kwargs: Any):
        super().__init__(text, *args, **kwargs)
        # self.setFrameStyle(QtWidgets.QFrame.Plain | QtWidgets.QFrame.Box)
        self.setAlignment(Qt.AlignCenter)
        # self.setLineWidth(1)


class LabeledCheckBox(QtWidgets.QWidget):
    """ Виджет Check Box с названием """

    def __init__(self, text: str, *args: Any,
                 chstate_func: Any = None,
                 init_state: Qt.CheckState = Qt.Unchecked,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)
        self.check_box = QtWidgets.QCheckBox()
        self.check_box.setCheckState(init_state)
        if chstate_func is not None:
            self.check_box.stateChanged.connect(chstate_func)
        self.layout.addWidget(self.check_box, stretch=1)
        self.setLayout(self.layout)  # type: ignore

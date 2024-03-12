import json
import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout
import os


def read_config(config_file_name):
    with open(config_file_name) as CONFIG:
        config = json.load(CONFIG)
    return config


def get_validator(input_type, low, high):
    validator = None
    if input_type == 'Float':
        validator = QtGui.QDoubleValidator(float(low), float(high), 1, notation=QtGui.QDoubleValidator.StandardNotation)
    elif input_type == 'Int':
        validator = QtGui.QIntValidator(int(low), int(high))
    return validator


def create_input(layout, input_data):
    label = input_data['label']
    line_edit = QLineEdit()
    validator = get_validator(input_data['type'],
                              input_data['low'],
                              input_data['high'])
    if validator:
        line_edit.setValidator(validator)

    layout.addRow(QLabel(f'{label}:'), line_edit)

class BLDCGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.label_to_key = {}
        self.initUI()

    def initUI(self):
        config = read_config('gui_config.json')
        if not config:
            self.setWindowTitle('Unknown Config')
            exit_button = QPushButton('Exit', self)
            exit_button.clicked.connect(lambda _: sys.exit())
            layout = QVBoxLayout(self)
            layout.addWidget(exit_button)
            self.setLayout(layout)
            self.setGeometry(300, 300, 300, 150)
            return

        self.setWindowTitle(config['title'])

        main_layout = QVBoxLayout()
        if 'general_inputs' in config:
            general_inputs_layout = QFormLayout()
            for input_data in config['general_inputs']:
                print(input_data)
                create_input(general_inputs_layout, input_data)
                self.label_to_key[input_data['label']] = input_data['key']
            main_layout.addLayout(general_inputs_layout)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = BLDCGenerator()
    gui.show()
    sys.exit(app.exec_())

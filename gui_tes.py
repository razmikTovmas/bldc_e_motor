from PyQt5 import QtGui, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.lineEdit_taxRate = QtWidgets.QLineEdit()
        validator = QtGui.QDoubleValidator(0.0, 100.0, 6, notation=QtGui.QDoubleValidator.StandardNotation)
        self.lineEdit_taxRate.setValidator(validator)
        self.setCentralWidget(self.lineEdit_taxRate)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
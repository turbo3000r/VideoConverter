import Design
from PyQt6 import QtWidgets, QtCore
import sys

def Convert():
    print("Convert")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Design.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(Convert)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    print(w.actions())
    w.show()
    sys.exit(app.exec())
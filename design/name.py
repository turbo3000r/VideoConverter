from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt6 import uic


class UI(QMainWindow):
    def __init__(self):
        super().__init__()

        # loading the ui file with uic module
        uic.loadUi("VideoConverter.ui", self)

app = QApplication([])
window = UI()
window.show()
print(window)
app.exec()

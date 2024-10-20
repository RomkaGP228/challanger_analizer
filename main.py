from data.classes import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
import sys



if __name__ == '__main__':
    funcs.add_new_db()
    app = QApplication(sys.argv)
    dwex = dayswindow_class()
    anwex = add_new_one_class()
    mwex = mainwindow_class(anwex, dwex)
    mwex.show()
    sys.exit(app.exec())

from data.classes import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
import sys
import asyncio




if  __name__ == '__main__':
    funcs.add_new_db()
    app = QApplication(sys.argv)
    anwex = AddNewOneClass()
    mwex = MainWindowClass(anwex)
    mwex.show()
    sys.exit(app.exec())
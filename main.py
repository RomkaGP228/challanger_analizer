from data.classes import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
import sys
import asyncio




async def main():
    funcs.add_new_db()
    app = QApplication(sys.argv)
    anwex = add_new_one_class()
    mwex = main_window_class(anwex)
    mwex.show()
    sys.exit(app.exec())

asyncio.run(main())
from PySide6.QtWidgets import QApplication
from ui import MainWindow
import sys

# Commentaire

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(750, 750)
    window.show()
    sys.exit(app.exec())


# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QApplication
from perceptron_core import PerceptronGUI

def main() -> None:
    import sys
    app = QApplication(sys.argv)
    win = PerceptronGUI(modo="AND")
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

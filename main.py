# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from perceptron_core import PerceptronGUI

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Perceptrón (±1) — AND y OR — PyQt6")

        tabs = QTabWidget()
        # Reutilizamos la GUI parametrizada, pero embebida como pestañas
        self.and_tab = PerceptronGUI(modo="AND")
        self.or_tab  = PerceptronGUI(modo="OR")

        tabs.addTab(self.and_tab, "AND")
        tabs.addTab(self.or_tab, "OR")

        self.setCentralWidget(tabs)
        self.resize(1000, 700)

def main() -> None:
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

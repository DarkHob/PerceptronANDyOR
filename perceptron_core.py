# -*- coding: utf-8 -*-

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Literal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout,
    QHBoxLayout, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QGroupBox, QRadioButton, QMessageBox, QSpacerItem, QSizePolicy
)

# ---------------------------- LÓGICA DEL PERCEPTRÓN ---------------------------

def activacion_bipolar(net: float) -> int:
    """Escalón bipolar: devuelve +1 si net >= 0, si no -1."""
    return 1 if net >= 0 else -1

Modo = Literal["AND", "OR"]

@dataclass
class PerceptronBipolar:
    alpha: float
    w: List[float]  # [w0, w1, w2]
    x0: int         # bias común (±1)
    modo: Modo      # "AND" o "OR"

    def tabla(self) -> List[Tuple[int, int, int, int]]:
        x0 = self.x0
        if self.modo == "AND":
            return [
                (x0,  1,  1,  1),
                (x0,  1, -1, -1),
                (x0, -1,  1, -1),
                (x0, -1, -1, -1),
            ]
        else:
            return [
                (x0,  1,  1,  1),
                (x0,  1, -1,  1),
                (x0, -1,  1,  1),
                (x0, -1, -1, -1),
            ]

    def entrenar(self, max_actualizaciones: int = 10000):
        """Ejecuta el aprendizaje y devuelve (log, iteraciones, pesos_finales)."""
        log = []
        log.append(f"=== PERCEPTRÓN {self.modo} (±1) — Resultados con reinicio por error ===\n")

        # Mostrar tabla
        tabla = self.tabla()
        log.append("\nTABLA DE ACTIVACIÓN\n")
        log.append(" X0  X1  X2 | Yd\n")
        log.append("------------|---\n")
        for r in tabla:
            log.append(f"{r[0]:>3} {r[1]:>3} {r[2]:>3} | {r[3]:>2}\n")
        log.append("\n")

        log.append(
            f"Pesos iniciales: w0={self.w[0]:.6f}, w1={self.w[1]:.6f}, w2={self.w[2]:.6f}\n"
        )
        log.append(f"α={self.alpha}\n\n")

        iteracion = 1
        log.append(f"==> Inicio de iteración Nº {iteracion}\n")

        actualizaciones = 0
        i = 0
        while True:
            x0i, x1i, x2i, yd = tabla[i]
            net = self.w[0]*x0i + self.w[1]*x1i + self.w[2]*x2i
            y = activacion_bipolar(net)
            error = yd - y

            log.append(
                f"Ejercicio {i+1}: (X0,X1,X2,Yd)=({x0i},{x1i},{x2i},{yd}) → salida={y}, error={error}\n"
            )

            if error == 0:
                log.append("  Resultado: Correcto (error=0). Continúa al siguiente ejercicio.\n\n")
                i += 1
                if i == len(tabla):
                    log.append("No se detectaron errores en toda la pasada.\n")
                    log.append(f"==> Fin de iteración Nº {iteracion} (sin cambios)\n")
                    break
            else:
                # Regla de aprendizaje del perceptrón
                dw0 = self.alpha * error * x0i
                dw1 = self.alpha * error * x1i
                dw2 = self.alpha * error * x2i
                self.w[0] += dw0
                self.w[1] += dw1
                self.w[2] += dw2
                actualizaciones += 1

                if yd == 1 and y == -1:
                    razon = "salida debería ser +1 pero fue -1; se aumentan pesos en la dirección de X."
                else:
                    razon = "salida debería ser -1 pero fue +1; se reducen pesos en la dirección de X."

                log.append(f"  Resultado: Incorrecto (error≠0). {razon}\n")
                log.append(
                    f"  Pesos NUEVOS: w0={self.w[0]:+.6f}, w1={self.w[1]:+.6f}, w2={self.w[2]:+.6f}\n"
                )
                log.append(f"==> Fin de iteración Nº {iteracion}\n\n")

                iteracion += 1
                if actualizaciones >= max_actualizaciones:
                    log.append("Se alcanzó el máximo de actualizaciones permitido.\n")
                    break

                log.append(f"==> Inicio de iteración Nº {iteracion}\n")
                i = 0

        log.append("\n==================== RESULTADO FINAL ====================\n")
        log.append(f"Iteraciones (actualizaciones) totales: {iteracion}\n")
        log.append(
            f"Pesos finales: w0={self.w[0]:.6f}, w1={self.w[1]:.6f}, w2={self.w[2]:.6f}\n"
        )
        log.append("=========================================================\n")
        return ("".join(log), iteracion, self.w[:])


# ----------------------------- INTERFAZ GRÁFICA --------------------------------

class PerceptronGUI(QWidget):
    """
    GUI parametrizada por modo. Úsala como:
        PerceptronGUI(modo="AND")  o  PerceptronGUI(modo="OR")
    El selector AND/OR se oculta para que el modo quede fijo.
    """
    def __init__(self, modo: Modo) -> None:
        super().__init__()
        self.modo: Modo = modo
        self.setWindowTitle(f"Perceptrón (±1) — {self.modo} — PyQt6")
        self.setMinimumWidth(900)
        self._build_ui()
        self._apply_bootstrap_like_qss()
        self._actualizar_rotulos()

    # ---- UI ----
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        self.header = QLabel("")
        self.header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.header.setFont(QFont("Inter, Segoe UI, Roboto, Helvetica", 20, QFont.Weight.Bold))
        self.sub = QLabel("")
        self.sub.setObjectName("subtitle")

        layout.addWidget(self.header)
        layout.addWidget(self.sub)

        # (ANTES había selector AND/OR). Ahora se fija el modo y no se muestra.

        # Parámetros
        params_box = QGroupBox("Parámetros")
        grid = QGridLayout(params_box)

        self.input_alpha = QLineEdit("0.1")
        self.input_w0 = QLineEdit("0.0")
        self.input_w1 = QLineEdit("0.0")
        self.input_w2 = QLineEdit("0.0")

        self.rb_x0_pos = QRadioButton("X0 = +1")
        self.rb_x0_neg = QRadioButton("X0 = -1")
        self.rb_x0_pos.setChecked(True)

        grid.addWidget(QLabel("α (factor de aprendizaje)"), 0, 0)
        grid.addWidget(self.input_alpha, 0, 1)
        grid.addWidget(QLabel("w0"), 0, 2)
        grid.addWidget(self.input_w0, 0, 3)
        grid.addWidget(QLabel("w1"), 1, 2)
        grid.addWidget(self.input_w1, 1, 3)
        grid.addWidget(QLabel("w2"), 2, 2)
        grid.addWidget(self.input_w2, 2, 3)

        grid.addWidget(QLabel("Bias común (X0)"), 1, 0)
        rb_row = QHBoxLayout()
        rb_row.addWidget(self.rb_x0_pos)
        rb_row.addWidget(self.rb_x0_neg)
        rb_row.addStretch()
        grid.addLayout(rb_row, 1, 1)

        layout.addWidget(params_box)

        # Tabla de activación
        self.tabla_box = QGroupBox("")
        tlay = QVBoxLayout(self.tabla_box)
        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["X0", "X1", "X2", "Yd"])
        self.table.verticalHeader().setVisible(False)
        self._rellenar_tabla()
        tlay.addWidget(self.table)
        layout.addWidget(self.tabla_box)

        # Botones de acción
        btn_row = QHBoxLayout()
        self.btn_train = QPushButton("Entrenar")
        self.btn_clear = QPushButton("Limpiar")
        btn_row.addWidget(self.btn_train)
        btn_row.addWidget(self.btn_clear)
        btn_row.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(btn_row)

        # Log
        log_box = QGroupBox("Salida / Log")
        llay = QVBoxLayout(log_box)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("log")
        llay.addWidget(self.log)
        layout.addWidget(log_box)

        # Resultados breves
        res_row = QHBoxLayout()
        self.lbl_iters = QLabel("Iteraciones: –")
        self.lbl_w = QLabel("Pesos finales: –")
        res_row.addWidget(self.lbl_iters)
        res_row.addWidget(self.lbl_w)
        res_row.addStretch()
        layout.addLayout(res_row)

        # Conexiones
        self.btn_train.clicked.connect(self._on_train)
        self.btn_clear.clicked.connect(self.log.clear)
        self.rb_x0_pos.toggled.connect(self._rellenar_tabla)
        self.rb_x0_neg.toggled.connect(self._rellenar_tabla)

    def _apply_bootstrap_like_qss(self) -> None:
        """Hoja de estilos inspirada en Bootstrap (primario/secundario, bordes, etc.)."""
        self.setStyleSheet(
            """
            QWidget { font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica', Arial; font-size: 14px; }
            #subtitle { color: #6c757d; }

            QGroupBox { border: 1px solid #dee2e6; border-radius: 12px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #495057; }

            QLineEdit { padding: 6px 10px; border: 1px solid #ced4da; border-radius: 10px; }
            QLineEdit:focus { border: 1px solid #86b7fe; outline: none; }

            QPushButton { padding: 8px 14px; border-radius: 12px; border: 1px solid transparent; }
            QPushButton:hover { filter: brightness(1.03); }
            QPushButton:pressed { transform: translateY(1px); }

            QPushButton { background: #0d6efd; color: white; }
            QPushButton#secondary { background: #6c757d; color: white; }

            QTableWidget { border: 1px solid #dee2e6; border-radius: 10px; }
            QHeaderView::section { background: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; }

            QTextEdit#log { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; }
            """
        )
        # boton secundario (si lo quisieras usar)
        # self.btn_clear.setObjectName("secondary")

    # ---- helpers ----
    def _bias_value(self) -> int:
        return 1 if self.rb_x0_pos.isChecked() else -1

    def _rellenar_tabla(self) -> None:
        x0 = self._bias_value()
        if self.modo == "AND":
            datos = [
                (x0,  1,  1,  1),
                (x0,  1, -1, -1),
                (x0, -1,  1, -1),
                (x0, -1, -1, -1),
            ]
        else:
            datos = [
                (x0,  1,  1,  1),
                (x0,  1, -1,  1),
                (x0, -1,  1,  1),
                (x0, -1, -1, -1),
            ]
        for r, (a,b,c,d) in enumerate(datos):
            for cidx, val in enumerate((a,b,c,d)):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, cidx, item)
        self.table.resizeColumnsToContents()
        self._actualizar_rotulos()

    def _leer_float(self, widget: QLineEdit, nombre: str) -> float | None:
        txt = widget.text().strip().replace(',', '.')
        try:
            return float(txt)
        except ValueError:
            QMessageBox.warning(self, "Entrada inválida", f"El campo '{nombre}' debe ser numérico.")
            widget.setFocus()
            return None

    def _actualizar_rotulos(self) -> None:
        self.header.setText(f"Perceptrón {self.modo} (±1)")
        self.sub.setText("Entrenamiento con reinicio por error — Activación bipolar")
        self.tabla_box.setTitle(f"Tabla de activación ({self.modo} bipolar)")

    # ---- acciones ----
    def _on_train(self) -> None:
        alpha = self._leer_float(self.input_alpha, "α (factor de aprendizaje)")
        if alpha is None:
            return
        w0 = self._leer_float(self.input_w0, "w0")
        if w0 is None:
            return
        w1 = self._leer_float(self.input_w1, "w1")
        if w1 is None:
            return
        w2 = self._leer_float(self.input_w2, "w2")
        if w2 is None:
            return

        x0 = self._bias_value()
        modelo = PerceptronBipolar(alpha=alpha, w=[w0, w1, w2], x0=x0, modo=self.modo)
        log, iters, w_final = modelo.entrenar()
        self.log.setPlainText(log)
        self.lbl_iters.setText(f"Iteraciones: {iters}")
        self.lbl_w.setText(f"Pesos finales: w0={w_final[0]:.6f}, w1={w_final[1]:.6f}, w2={w_final[2]:.6f}")

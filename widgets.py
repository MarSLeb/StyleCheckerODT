from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QDialogButtonBox

# это костыли, но более простого способа поставить кнопку в центр не нашлось.
# Инет говорит, что обычно расположение кнопок зависит от системного стиля
# https://stackoverflow.com/questions/67476677/how-to-center-text-and-buttons-in-qmessagebox-widget
class CenteredMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid_layout = self.layout()


        qt_msgboxex_icon_label = self.findChild(QLabel, "qt_msgboxex_icon_label")
        qt_msgboxex_icon_label.deleteLater()

        qt_msgbox_label = self.findChild(QLabel, "qt_msgbox_label")
        qt_msgbox_label.setAlignment(Qt.AlignCenter)
        grid_layout.removeWidget(qt_msgbox_label)

        qt_msgbox_buttonbox = self.findChild(QDialogButtonBox, "qt_msgbox_buttonbox")
        grid_layout.removeWidget(qt_msgbox_buttonbox)

        grid_layout.addWidget(qt_msgbox_label, 0, 0, alignment=Qt.AlignCenter)
        grid_layout.addWidget(qt_msgbox_buttonbox, 1, 0, alignment=Qt.AlignCenter)
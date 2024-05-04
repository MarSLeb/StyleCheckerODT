from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, \
    QLineEdit, QListView, QStackedWidget, QDialog, QLabel, QFrame, \
    QVBoxLayout, QWidget, QScrollArea
import sys
import checker

class ScrollLabel(QScrollArea):
    def __init__(self):
        QScrollArea.__init__(self)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class MainWindow(QMainWindow):
    scrollArea: ScrollLabel
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Style checker")
        self.setFixedSize(QSize(700, 800))

        layout = QVBoxLayout()

        button = QPushButton("Выбрать файл для проверки")
        button.setCheckable(True)
        button.clicked.connect(self.push_select_file_buttom)

        self.scrollArea = ScrollLabel()
        self.scrollArea.setText("Файл не выбран")

        layout.addWidget(button)
        layout.addWidget(self.scrollArea)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def push_select_file_buttom(self):
        file = getOpenFilesAndDirs(filter='(*.odt)')
        if (len(file) == 1):
            check = checker.StyleChecker(file[0])
            self.scrollArea.setText('\n'.join(check.run()))
        else: 
            self.scrollArea.setText('Выберете один файл.')


def getOpenFilesAndDirs(parent=None, caption='', directory='', 
                        filter='', initialFilter='', options=None):
    def updateText():
        selected = []
        for index in view.selectionModel().selectedRows():
            selected.append('"{}"'.format(index.data()))
        lineEdit.setText(' '.join(selected))

    dialog = QFileDialog(parent, windowTitle=caption)
    dialog.setFileMode(dialog.ExistingFiles)
    if options:
        dialog.setOptions(options)
    dialog.setOption(dialog.DontUseNativeDialog, True)
    if directory:
        dialog.setDirectory(directory)
    if filter:
        dialog.setNameFilter(filter)
        if initialFilter:
            dialog.selectNameFilter(initialFilter)

    dialog.accept = lambda: QDialog.accept(dialog)
    
    stackedWidget = dialog.findChild(QStackedWidget)
    view = stackedWidget.findChild(QListView)
    view.selectionModel().selectionChanged.connect(updateText)

    lineEdit = dialog.findChild(QLineEdit)
    dialog.directoryEntered.connect(lambda: lineEdit.setText(''))

    dialog.exec_()
    return dialog.selectedFiles()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
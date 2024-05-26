from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, \
    QLineEdit, QListView, QStackedWidget, QDialog, QLabel, QMessageBox, \
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
        self.label.setMaximumWidth(650)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class MainWindow(QMainWindow):
    scrollArea: ScrollLabel
    file: str
    text: str

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Style checker")
        self.setFixedSize(QSize(700, 800))
        self.file = ""
        self.text = ""

        layout = QVBoxLayout()

        select_button = QPushButton("Выбрать файл для проверки.")
        select_button.setCheckable(True)
        select_button.clicked.connect(self.push_select_file_buttom)

        save_button = QPushButton("Сохранить исправления в файл.")
        save_button.setCheckable(True)
        save_button.clicked.connect(self.push_save_file_buttom)

        self.scrollArea = ScrollLabel()
        self.scrollArea.setText("Файл не выбран.")

        layout.addWidget(select_button)
        layout.addWidget(save_button)
        layout.addWidget(self.scrollArea)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def push_select_file_buttom(self):
        file = getOpenFilesAndDirs(filter='(*.odt)')
        if (len(file) == 1):
            self.file = file[0][file[0].rfind("/") + 1 : file[0].find('.odt')]
            check = checker.StyleChecker(file[0])
            errors = check.run()
            if (len(errors) == 0):
                self.text = "все верно"
            else:
                self.text = '\n'.join(errors)
            self.scrollArea.setText(self.text)
            return

        elif (len(file) == 0):
            self.none_file()
        else: 
            self.many_files()

    def none_file(self):
        mess = QMessageBox()
        mess.setText("Выберите файл.")
        mess.exec()
    def many_files(self):
        mess = QMessageBox()
        mess.setText("Выберите один файл.")
        mess.exec()

    def push_save_file_buttom(self):
        if (self.file == ""):
            mess = QMessageBox()
            mess.setText("Файл не сохранен.")
            mess.exec()
            return
        
        f = open(self.file + "_right.txt", "a")
        f.write(self.text)
        f.close()
        mess = QMessageBox()
        mess.setText("Файл сохранен.")
        mess.exec()



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
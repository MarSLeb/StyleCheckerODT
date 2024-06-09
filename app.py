from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, \
    QLineEdit, QListView, QStackedWidget, QDialog, QLabel, QMessageBox, \
    QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem
import sys
import checker
from widgets import CenteredMessageBox

class MainWindow(QMainWindow):
    errorTree: QTreeWidget
    file: str
    text: str

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Style checker")
        self.setFixedSize(QSize(700, 800))
        self.file = ""
        self.text = ""

        layout = QVBoxLayout()

        select_button = QPushButton("Выбрать файл для проверки")
        select_button.setCheckable(True)
        select_button.clicked.connect(self.push_select_file_buttom)

        save_button = QPushButton("Сохранить исправления в файл")
        save_button.setCheckable(True)
        save_button.clicked.connect(self.push_save_file_button)

        self.errorTree = QTreeWidget()
        self.errorTree.setHeaderLabel("Файл не выбран")

        layout.addWidget(select_button)
        layout.addWidget(save_button)
        layout.addWidget(self.errorTree)

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
                self.text = ""
                for error in errors:
                    self.text += error.pretty() + "\n"
            self.errorTree.setHeaderLabel(self.file)
            self.listErrors(errors)
            return

        elif (len(file) == 0):
            popup("Выберите файл")
        else: 
            popup("Выберите один файл")

    def listErrors(self, errors: list[checker.Error]):
        def wordWrapLabel(text: str) -> QLabel:
            label = QLabel(text)
            label.setWordWrap(True)
            return label

        for errorLine in errors:
            lineEntry = QTreeWidgetItem(self.errorTree)
            self.errorTree.setItemWidget(lineEntry, 0, wordWrapLabel(errorLine.text))
            for errorDescription in errorLine.errors:
                errorEntry = QTreeWidgetItem(lineEntry)
                self.errorTree.setItemWidget(errorEntry, 0, wordWrapLabel(errorDescription.pretty()))

    def push_save_file_button(self):
        if (self.file == ""):
            popup("Файл не сохранен")
            return
        
        f = open(self.file + "_corrections.txt", "a")
        f.write(self.text)
        f.close()
        popup("Файл сохранен")

def popup(text):
    messageBox = CenteredMessageBox()
    messageBox.setText(text)
    messageBox.setStyleSheet("QLabel{min-width: 140px;}")
    messageBox.exec()

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
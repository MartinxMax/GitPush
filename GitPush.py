# @Мартин.
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox,QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from GitAction import GitAction
import time

class DialogThread(QThread):
    dialog_selected = pyqtSignal(str)

    def run(self):
        directory = QFileDialog.getExistingDirectory(None, 'Select Directory', '/')
        if directory:
            self.dialog_selected.emit(directory)


class UploadThread(QThread):
    progress_updated = pyqtSignal(int)
    message_box = pyqtSignal(str, str)

    def __init__(self, filepath, remotegit, commit,token,branch):
        super().__init__()
        self.filepath = filepath
        self.remotegit = remotegit
        self.commit = commit
        self.token = token
        self.branch = branch
        self.gits = GitAction(False)
        self.progress_updated.emit(60)


    def run(self):
        self.progress_updated.emit(80)
        if self.gits.push(
          remotegit=self.remotegit,
          path=self.filepath,
          token=self.token,
          branch=self.branch,
          commit=self.commit):
            self.progress_updated.emit(100)
            self.message_box.emit('Success', 'Upload successful')
        else:
            self.progress_updated.emit(0)
            self.message_box.emit('Fail', 'Unreachable server!')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.gitaction = GitAction()
        widget = QtWidgets.QWidget()
        QtWidgets.QVBoxLayout(widget)
        self.setCentralWidget(widget)
        uic.loadUi('Main.ui', self)
        self.load_control()
        self.run()


    def load_control(self):
        self.upload_button = self.findChild(QtWidgets.QPushButton, "upload")
        self.select_button = self.findChild(QtWidgets.QPushButton, "select")
        self.filepath = self.findChild(QtWidgets.QLineEdit,"filepath")
        self.commit = self.findChild(QtWidgets.QLineEdit,"commit")
        self.token = self.findChild(QtWidgets.QLineEdit, "token")
        self.branch = self.findChild(QtWidgets.QLineEdit, "branch")
        self.remotegit = self.findChild(QtWidgets.QLineEdit, "remotegit")
        self.process = self.findChild(QtWidgets.QProgressBar, "process")
        try:
            with open('./token.conf','r',encoding='utf-8')as f:
                self.token.setText(f.read())
        except Exception as e:
            pass


    def upload_clicked(self):
        self.upload_thread = UploadThread( self.filepath.text(), self.remotegit.text(), self.commit.text(),self.token.text(),self.branch.text())
        self.upload_thread.progress_updated.connect(self.update_progress_bar) # 连接进度更新信号
        self.upload_thread.message_box.connect(self.message_boxs)
        self.upload_thread.start()


    def update_progress_bar(self, progress):
        self.process.setValue(progress)

    def message_boxs(self,title,note):
        QMessageBox.information(self, title,note)


    def showDialog(self):
        self.showDialog_thread = DialogThread()
        self.showDialog_thread.dialog_selected.connect(self.showDialog_handleSelected)
        self.showDialog_thread.start()


    def showDialog_handleSelected(self, directory):
        self.filepath.setText(directory)


    def run(self):
        self.upload_button.clicked.connect(self.upload_clicked)
        self.select_button.clicked.connect(self.showDialog)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
# Importing the necessary libraries
import socket
from time import sleep

from gui import Ui_Python_Labview
from sys import argv

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Check variable used for controlling the worker thread
check = True


class Worker1(QObject):
    finished1 = pyqtSignal()
    progress1 = pyqtSignal(int)

    def run(self):
        while check:
            self.progress1.emit(1)
            sleep(1)
        self.finished1.emit()


class ApplicationController(Worker1):
    def __init__(self):
        super().__init__()
        app = QtWidgets.QApplication(argv)
        self.application_window = QtWidgets.QMainWindow()
        self.ui = Ui_Python_Labview()
        self.ui.setupUi(self.application_window)
        self.application_window.show()

        # The functions of the start and stop buttons
        self.ui.start_button.clicked.connect(self.start)
        self.ui.stop_button.clicked.connect(self.stop)

        exit(app.exec_())

    # When the start button has been clicked, def start(self): will execute
    def start(self):
        global check
        check = True
        self.reset = True

        self.thread1 = QThread()
        self.worker1 = Worker1()
        self.worker1.moveToThread(self.thread1)
        self.thread1.started.connect(self.worker1.run)
        self.worker1.finished1.connect(self.thread1.quit)
        self.worker1.finished1.connect(self.worker1.deleteLater)
        self.thread1.finished.connect(self.thread1.deleteLater)

        # The Worker1 class will call upon the def update(self): for every sleep(1)
        self.worker1.progress1.connect(self.update)
        self.thread1.start()

    # The update function, checking the random data from Labview
    def update(self):
        global check
        try:
            self.reset = False
            # Connecting to the TCP listen (Labview)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 6340)
            client.connect(server_address)

            # Sending message 'start'
            client.send('start'.encode('utf-8'))
            client.close()

        except Exception as e:
            print(e)

        try:
            # Connecting to the TCP open connection (Labview)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('localhost', 6350))
            server.listen(1)

            receive, adr = server.accept()
            cmnd = receive.recv(12).decode('utf-8')
            print(cmnd[4:])
            self.ui.data_line.setText(cmnd[4:])
            server.close()

        except Exception as e:
            check = False
            server.close()
            print(e)

    # When the stop button is clicked, the def stop(self): will set the Worker1 class to terminate itself and updating will cease
    def stop(self):
        global check
        check = False
        self.reset = True

        try:
            # Connecting to the TCP listen (Labview)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 6340)
            client.connect(server_address)

            # Sending message 'stop'
            client.send('stop'.encode('utf-8'))
            client.close()

        except Exception as e:
            print(e)


# This will run the script and is necessary because something to do with Windows operating system
if __name__ == '__main__':
    runner = ApplicationController()

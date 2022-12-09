# Importing the necessary libraries
import socket
from time import sleep

from gui import Ui_Python_Labview
from sys import argv

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Check variable used for controlling the worker thread
# check = True


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

        try:
            # Connecting to the TCP listen (Labview)
            client_start = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 6330)
            client_start.connect(server_address)

            # Sending message 'start'
            client_start.send('start'.encode('utf-8'))
            client_start.close()
            self.ui.start_button.setEnabled(False)

        except Exception as e:
            print(e)

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
            # Connecting to the TCP open connection (Labview)
            server_update = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_update.bind(('localhost', 6350))
            server_update.listen(1)

            receive, adr = server_update.accept()
            cmnd = receive.recv(12).decode('utf-8')
            print(cmnd[4:])
            self.ui.data_line.setText(cmnd[4:])
            server_update.close()

        except Exception as e:
            print(e)

    # When the stop button is clicked, the def stop(self): will set the Worker1 class to terminate itself and updating will cease
    def stop(self):
        global check
        check = False

        try:
            # Connecting to the TCP listen (Labview)
            client_stop = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 6340)
            client_stop.connect(server_address)

            # Sending message 'stop'
            client_stop.send('stop'.encode('utf-8'))
            client_stop.close()
            self.ui.start_button.setEnabled(True)

        except Exception as e:
            print(e)


# This will run the script and is necessary because something to do with Windows operating system
if __name__ == '__main__':
    runner = ApplicationController()

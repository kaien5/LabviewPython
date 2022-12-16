# Importing the necessary libraries
import socket
import struct

from time import sleep
from sys import argv
from PyQt5 import QtWidgets
from gui import Ui_Python_Labview
from PyQt5.QtCore import QObject, pyqtSignal, QThread


def ascii_message(text):
    if len(text) < 32:
        amount_null = 32 - len(text)
        message = text + amount_null * ' '
        message = message.encode('ascii')
        return message
    else:
        print('The text is too long, maximum of 32 characters')


# For more information on what format to use in pack: https://docs.python.org/3/library/struct.html
def pack_payload(value):
    """
    Packing the value to the corresponding bytes type and size
    """
    if isinstance(value, float):
        value = struct.pack('!d', value)
    elif isinstance(value, int):
        value = struct.pack('!i', value)
    elif isinstance(value, bool):
        value = struct.pack('!?', value)
    return value


def unpack_payload(value, sort):
    """
    Unpacking the byte(s) to their corresponding value
    """
    if isinstance(sort, float):
        value = struct.unpack('!d', value)
    elif isinstance(sort, int):
        value = struct.unpack('!i', value)
    elif isinstance(sort, bool):
        value = struct.unpack('!?', value)
    return value


# Check variable used for controlling the worker thread
check = False


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
        self.ui.send_button.clicked.connect(self.send_message)
        self.ui.start_button.clicked.connect(self.start)
        self.ui.stop_button.clicked.connect(self.stop)

        # self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_message = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        exit(app.exec_())

    # When the start button has been clicked, def start(self): will execute
    def start(self):
        global check

        try:
            # Connecting to the TCP listen (Labview)
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(('localhost', 6340))

            # Sending message 'start'
            self.client.sendall('START'.encode('utf-8'))
            self.client.close()

            self.ui.start_button.setEnabled(False)
            self.ui.stop_button.setEnabled(True)
            self.ui.send_button.setEnabled(True)

            self.wait = True
            check = True

            # self.thread1 = QThread()
            # self.worker1 = Worker1()
            # self.worker1.moveToThread(self.thread1)
            # self.thread1.started.connect(self.worker1.run)
            # self.worker1.finished1.connect(self.thread1.quit)
            # self.worker1.finished1.connect(self.worker1.deleteLater)
            # self.thread1.finished.connect(self.thread1.deleteLater)
            # self.worker1.progress1.connect(self.update)
            # self.thread1.start()

        except Exception as e:
            print(e)

    def send_message(self):
        global check

        self.client_message = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_message.connect(('localhost', 6340))

        indicator = self.ui.indicator_line.text()
        command = self.ui.command_line.text()
        payload = self.ui.payload_double.value()

        indicator_message = ascii_message(indicator)
        command_message = ascii_message(command)
        payload_message = pack_payload(payload)

        message = indicator_message + command_message + payload_message
        print(message)

        self.client_message.sendall(message)
        self.client_message.close()

        if command == 'STOP':
            self.stop()

    # The update function, checking the random data from Labview
    def update(self):

        # Connecting to the TCP open connection (Labview)
        self.server_update = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_update.bind(('localhost', 6350))
        self.server_update.listen(1)

        try:
            receive, adr = self.server_update.accept()
            cmnd = receive.recv(12).decode('utf-8')
            print(cmnd[4:])
            self.ui.data_line.setText(cmnd[4:])
            self.server_update.close()

        except Exception as e:
            print(e)

    # When the stop button is clicked, the def stop(self): will set the Worker1 class to terminate itself and updating will cease
    def stop(self):
        print('Stopping program')
        global check
        check = False

        try:
            self.ui.start_button.setEnabled(True)
            self.ui.stop_button.setEnabled(False)
            self.ui.send_button.setEnabled(False)

        except Exception as e:
            print(e)


# This will run the script and is necessary because something to do with Windows operating system
if __name__ == '__main__':
    runner = ApplicationController()

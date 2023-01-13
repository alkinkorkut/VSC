
import socket  # Import socket module in order to create socket instances and handle connections
import threading  # Import threading module in order to create threads and handle multiple connections
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys  # Import sys module in order to handle system arguments

# Global variables
userName = ""
password = ""

#SERVER_ADDRESS = "127.0.0.1"  # local server ip
SERVER_ADDRESS = 'ec2-100-26-169-209.compute-1.amazonaws.com'   # prod server ip
SERVER_PORT = 7550  # listen port

""" Initiate client and connect to server """
socketInstance = socket.socket()
socketInstance.connect((SERVER_ADDRESS, SERVER_PORT))


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create the GUI widgets
        self.setWindowTitle("Very Simple Chat")
        self.welcomeLabel = QLabel("Welcome to Very Simple Chat", self)
        self.welcomeLabel.setStyleSheet("font-size: 24px")
        self.welcomeLabel.setTextFormat(Qt.RichText)

        self.loginLabel = QLabel("Please enter the fields to login", self)
        self.loginLabel.setStyleSheet("font-size: 18px")
        self.usernameLineEdit = QLineEdit(self)
        self.usernameLineEdit.setPlaceholderText("Username: ")
        self.usernameLineEdit.setTextMargins(10, 0, 0, 0)
        self.passwordLineEdit = QLineEdit(self)
        # -------
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        # -------
        self.passwordLineEdit.setPlaceholderText("Password: ")
        self.passwordLineEdit.setTextMargins(10, 0, 0, 0)
        self.loginButton = QPushButton("Login", self)

        self.serverPasswordLineEdit = QLineEdit(self)
        self.serverPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.serverPasswordLineEdit.setPlaceholderText("Server Password:")
        self.serverPasswordLineEdit.setTextMargins(10, 0, 0, 0)

        # Set up the layout
        linearLayout = QVBoxLayout(self)
        linearLayout.setSpacing(10)
        layout = QVBoxLayout(self)
        layout.addWidget(self.welcomeLabel)
        layout.addWidget(self.loginLabel)
        layout2 = QVBoxLayout(self)
        layout2.addWidget(self.serverPasswordLineEdit)
        layout2.addWidget(self.usernameLineEdit)
        layout2.addWidget(self.passwordLineEdit)
        linearLayout.addLayout(layout)
        linearLayout.addLayout(layout2)
        linearLayout.addWidget(self.loginButton)

        # Connect the login button to the login function
        self.loginButton.clicked.connect(self.login)

    def login(self):
        """Login to server"""
        # Send username to server

        response = socketInstance.recv(2048)
        name = self.usernameLineEdit.text()
        socketInstance.send(str.encode(name))
        response = socketInstance.recv(2048)
        password = self.passwordLineEdit.text()
        socketInstance.send(str.encode(password))
        swPass = self.serverPasswordLineEdit.text()
        socketInstance.send(str.encode(swPass))

        response = socketInstance.recv(2048).decode()
        print("Response from server:", response)

        """ 
        R : Status of Connection     :
	    1 : Registeration successful :
	    2 : Connection Successful    :
	    3 : Login Failed             :
        """

        if response != 3:
            self.close()  # close LoginWindow
            time.sleep(1)  # wait for 1 second
            chat_window = ChatWindow()  # create ChatWindow
            chat_window.show()  # show ChatWindow
        else:
            self.close()  # close LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()  # show again
            print("Username or password is incorrect. Please try again.")


# inherit from QWidget and LoginWindow class to get socket_instance
class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create the GUI widgets
        self.setWindowTitle("Very Simple Chat Window")
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.lineEdit = QLineEdit(self)
        self.sendButton = QPushButton("Send", self)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.textEdit)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.lineEdit)
        h_layout.addWidget(self.sendButton)
        layout.addLayout(h_layout)

        # Connect the send button to the send_message function
        self.sendButton.clicked.connect(self.sendMessage)

        # Print connection information and wait for user's input to send to server
        print(
            "\nConnected to VSC Server! \nServer IP:",
            SERVER_ADDRESS,
            "\nServer PORT:",
            SERVER_PORT,
        )
        print(
            "\nSockname: ",
            socketInstance.getsockname()[0],
            "\nClient PORT:",
            socketInstance.getsockname()[1],
        )
        print(
            "\nPeername: ",
            socketInstance.getpeername()[0],
            "\nServer PORT:",
            socketInstance.getpeername()[1],
        )

        # Create the send and receive threads
        self.sendThread = threading.Thread(target=self.sendMessage)
        self.receiveThread = threading.Thread(target=self.receiveMessage)

        # Start the send and receive threads
        self.sendThread.start()
        self.receiveThread.start()

    def sendMessage(self):
        """Send message to server"""
        message = self.lineEdit.text()
        self.lineEdit.clear()
        socketInstance.send(message.encode())  # Parse message to utf-8 and send to server

    def receiveMessage(self):
        """Receive messages sent by the server and display them to user"""
        print("\nWaiting from server...\n")
        while True:  # Keep receiving messages
            try:  # Try to receive message from server and print it to user
                message = socketInstance.recv(1024)  # parse it to utf-8 format (bytes)
                if message:  # If there is a message, print it to user
                    print(
                        "Message from: ", message.decode("utf-8")
                    )  # Print message to user
                    self.textEdit.append(message.decode("utf-8"))
                else:  # If there is no message, close connection
                    socketInstance.close()  # Close connection
                    break  # Break loop in order to stop receiving messages from server

            except Exception as e:  # If there is an error, print it and close connection
                print(f"Error handling message from server: {e}")
                self.textEdit.append(f"Error handling message from server: {e}")
                socketInstance.close()  # Close connection
                break  # Break loop in order to stop receiving messages from server


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.setFixedHeight(300)
    window.setFixedWidth(400)
    window.setWindowTitle("Very Simple Chat")
    window.show()
    sys.exit(app.exec_())

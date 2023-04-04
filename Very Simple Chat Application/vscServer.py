
import socket  
import threading  
import hashlib  # To hash password
import time

connectionList = []  # For all client's connections
hashTable = {}  # For client's username and password (Hashtable is used in Registration section)

#LISTENER_IP = "127.0.0.1"  # local server
LISTENER_IP = '172.31.53.221'   # private server ip
LISTENING_PORT = 7550         # listening_port for connections

generalServerPassword = "cs447" # general server password for authentication



def startServer() -> None:
    """Start server and keep accepting connections"""
    # -> None means that this function doesn't return anything
    try:
        # Create server and specifying that it can only handle 4 connections
        socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketInstance.bind((LISTENER_IP, LISTENING_PORT))  # Bind socket to port
        socketInstance.listen(6)  # Listen for connections and specify max
        print("Server is running...")
        print("IP:", socketInstance.getsockname()[0]) # private ipv4 server address # TEST*********************************
        print("PORT:", LISTENING_PORT)

        while True:  # Keep accepting connections
            socketConnection, address = socketInstance.accept()
            connectionList.append(socketConnection)  # Add client
            # Start a new thread to handle client connection
            # in order to send to others connections
            threading.Thread(
                target=handleClientConnection, args=(socketConnection, address)
            ).start()

    except Exception as e:  # If there is any problem, print error message
        print(f"An error has occurred when instanciating socket: {e}")

    finally:  # In case of any problem we clean all connections
        if len(connectionList) > 0:  # if there is any connection
            for conn in connectionList:  # iterate on connections
                removeConnection(conn)  # remove connection
        socketInstance.close()  # close socket instance
        



# Function : For each client connection, create a thread and handle the connection
def handleClientConnection(connection: socket.socket, address: str) -> None:

    """Handle user connection and receive messages sent by the user"""
    # Request Username
    connection.send(str.encode("LOGIN\n\nEnter username: "))
    # time.sleep(60)  # sleep for 60 seconds
    userName = connection.recv(2048)
    userName = userName.decode()
    # Request Password
    connection.send(str.encode("Enter password: "))
    userPassword = connection.recv(2048)
    userPassword = userPassword.decode()
    # Password hash using SHA256
    userPassword = hashlib.sha256(str.encode(userPassword)).hexdigest()

    serverPassword = connection.recv(2048)
    print(serverPassword)
    serverPassword = serverPassword.decode()
    print(serverPassword)
    if serverPassword != generalServerPassword:
        connection.send(str.encode("Login Failed, Invalid Server Password"))
        print("Connection denied [Invalid Server Password] : ", serverPassword)
        removeConnection(connection)
    else:
        # REGISTRATION PHASE
        # If new user,  register in Hashtable Dictionary
        if userName not in hashTable:
            hashTable[userName] = userPassword
            connection.send(str.encode("Registration Successful"))
            print("Registered: ", userName)
            print("{:<8} {:<20}".format("USER", "PASSWORD"))
            for key, value in hashTable.items():
                label, num = key, value
                print("{:<8} {:<20}".format(label, num))
            print("-------------------------------------------")

        if userName in hashTable:
            # If already existing user, check if the entered password is correct
            if hashTable[userName] == userPassword:
                # Response Code for Connected Client
                print(
                    "Name: ",
                    userName,
                    " Password: ",
                    userPassword,
                    "HashTable[Name]: ",
                    hashTable[userName],
                )
                connection.send(str.encode("Connection Successful\n"))
                print("Connected : ", userName)
                # new !!
                broadcast(f"{userName} has joined the chat", connection)
                # Add connection to connections list
                while True:  # Keep receiving messages
                    try:  # Get client message
                        message = connection.recv(2048)
                        if message:
                            print(f"{address[0]}:{address[1]} - {message.decode()}")
                            # Build message format and broadcast users connected on server
                            # -------
                            # msg_to_send = f'{address[0]}:{address[1]} - {msg.decode()}'
                            messageToSend = f"{userName} - {message.decode()}"
                            # -------
                            broadcast(messageToSend, connection)

                        else:  # Remove connection from connections list
                            removeConnection(connection)
                            break  # Break in order to stop receiving messages from client

                    except Exception as e:
                        print(f"Error to handle user connection: {e}")
                        print(f"{address[0]}:{address[1]} - has left the chat")
                        # -------
                        messageToSend = f"{userName} - has left the chat"
                        broadcast(messageToSend, connection)
                        # -------
                        removeConnection(connection)
                        break

            else:
                # Response code for login failed
                connection.send(str.encode("Login Failed"))
                print("Connection denied : ", userName)
        while True:
            break
        connection.close()


def broadcast(message: str, connection: socket.socket) -> None:
    """Broadcast message to all users connected to the server"""
    # print(f'\nBroadcasting message: {message}')
    for clientConnection in connectionList:  # iterate on connections
        # if client_conn != connection:  # if it not the connection of who's send
        try:  # Try to send message to client connection
            clientConnection.send(message.encode())
            # print(f'Broadcast: {client_conn.getpeername()}')

        except Exception as e:  # There is a chance of socket has died
            print(f"Error broadcasting message: {e}")
            removeConnection(clientConnection)  # Remove


def removeConnection(conn: socket.socket) -> None:
    """Remove specified connection from connections list"""

    if conn in connectionList:  # Check if connection exists on connections list
        conn.close()  # Close socket connection
        connectionList.remove(conn)  # Remove connection from connections list

if __name__ == "__main__":
    startServer()


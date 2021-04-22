import socket
import os
from _thread import *

# files present in the server storage
files = {'file1':'Contents of file1.','file2':'Contents of file2.','file3':'Contents of file3.'}
clients = {}
# lists to maintain the list of readers and writers
currently_reading = []
currently_writing = []

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection,client_id):
    connection.send(str.encode('Functionalities : read "filename" | write "filename" | StopRead "filename" | StopWrite "filename"'))
    while True:
        data = connection.recv(2048)
        from_client = data.decode('utf-8')
        # client closes connection 
        # exit the loop
        if from_client == 'exit':
            print('Connection with client ',client_id,' closed')
            connection.close()
            break
        # message from client
        from_client = from_client.split(" ")
        print("Request from client ",client_id," :",from_client)
        # read file
        if from_client[0] == 'read':
            # filename is not provided. send error
            if len(from_client) !=2:
                print("Client ",client_id,' did not provide filename to read')
                reply = "Error : Invalid command. Please enter filename"
                connection.send(str.encode(reply))
            else:
                if client_id in clients and clients[client_id] == filename:
                    print("Client ",client_id,' already has a read access')
                    reply = "You already have the read access"
                else :
                    filename = from_client[1]
                    # check if file is present in the storage of server
                    if filename in files:
                        # check if file is being currently written
                        if filename in currently_writing:
                            print("Client ",client_id,' not granted read access')
                            reply = "Access denied. " + filename + " currently being written"
                        # check if file is being read already
                        elif filename in currently_reading:
                            # send contents of file to client
                            clients[client_id] = filename
                            print("Client ",client_id,' has been granted a Read access')
                            reply = "Read access only!!\nContents of "+filename+" are : \n***************************************************************\n"+files[filename]+"\n***************************************************************\n"
                            # Add file to reading list. we need to keep track of all the reader as simultaneous reading and writing is not allowed
                            currently_reading.append(filename) 
                        elif filename not in currently_reading:
                            # send contents of file to client
                            clients[client_id] = filename
                            print("Client ",client_id,' has been granted a Read access')
                            reply = "Contents of "+filename+" are : \n***************************************************************\n"+files[filename]+"\n***************************************************************\n"
                            # Add file to reading list.
                            currently_reading.append(filename)
                    # file not present in the server. send error
                    else:
                        print("Client ",client_id,' provided invalid filename to Read')
                        reply = "File not found! Enter valid filename"
                connection.send(str.encode(reply))
        # stop reading
        elif from_client[0] == 'StopRead':
            # filename not provided to stop reading
            if len(from_client) !=2:
                print("Client ",client_id,' did not provide filename to StopRead')
                reply = "Error : Invalid command. Please enter filename"
                connection.send(str.encode(reply))
            else:
                # check if client has read access
                if client_id in clients and clients[client_id] == filename:
                    # check if file is present in the server storage
                    if filename in files:
                        filename = from_client[1]
                        # file is not present in currently_reading then incorrect filename is previded. send error
                        if filename not in currently_reading:
                            print("Client ",client_id,' provided invalid filename to StopRead')
                            reply = "Error : File not found. Please enter valid filename"
                        else:
                        # revoke reading access for file from the client
                            removed_client = clients.pop(client_id)
                            print('Reading access of Client',client_id,' revoked')
                            reply = "Reading access revoked"
                            currently_reading.remove(filename)
                    else:
                    # file not present in the server storage
                        print("Client ",client_id,' provided invalid filename to StopRead')
                        reply = "No such file not found! Enter valid filename"
                else:
                        print("Client ",client_id,' did not have read access to the requested StopRead file')
                        reply = "You have not read this file before"
            connection.send(str.encode(reply))
        # write to file
        elif from_client[0] == 'write':
            # filename is not provided. send error
            if len(from_client) !=2:
                print("Client ",client_id,' did not provide filename to write')
                reply = "Error : Invalid command. Please enter filename"
                connection.send(str.encode(reply))
            else:
                filename = from_client[1]
                # check if file is present in the server storage
                if filename in files:
                    # if file is currenlt being written send access denied
                    if filename in currently_writing:
                        print("Client ",client_id,' not granted write access')
                        reply = "Access denied. " + filename + " currently being written"
                        connection.send(str.encode(reply))
                    # if file is currenlt being read send access denied
                    elif filename in currently_reading:
                        print("Client ",client_id,' not granted write access')
                        reply = "Access denied. " + filename + " currently being read"
                        connection.send(str.encode(reply))
                    else:
                        print("Client ",client_id,' granted write access')
                        reply = "Enter what you want to write in "+filename
                        connection.send(str.encode(reply))
                        currently_writing.append(filename)

                        from_client_to_write = (connection.recv(2048)).decode('utf-8')
                        # uupdate file
                        updated_file = files[filename] + "\n------------------------------------------------\n"+from_client_to_write+"."
                        files[filename] = updated_file 
                        reply = filename + " updated successfully"
                        connection.send(str.encode(reply))
                # file not present in the server storage
                else:
                    print("Client ",client_id,' entered invalid filename for write access')
                    reply = "File not found! Enter valid filename"
                    connection.send(str.encode(reply))
        elif from_client[0] == 'StopWrite':
            # filename is not provided. send error
            if len(from_client) !=2:
                print("Client ",client_id,' did not enter filename for StopWrite access')
                reply = "Error : Invalid command. Please enter filename"
                connection.send(str.encode(reply))
            else:
                # check if file is present in the server storage
                if filename in files:
                    filename = from_client[1]
                    # file is not present in currently_writing then incorrect filename is previded. send error
                    if filename not in currently_writing:
                        print("Client ",client_id,' entered invalid filename for write access')
                        reply = "Error : File not found. Please enter valid filename"
                    # remove writing access from the client
                    else:
                        print('Writing access of Client ',client_id,' revoked')
                        reply = "Writing access revoked"
                        currently_writing.remove(filename)
                # file not present in the server storage
                else:
                    print("Client ",client_id,' entered invalid filename for write access')
                    reply = "No such file not found! Enter valid filename"
                connection.send(str.encode(reply))    
        else :
            print("Invalid command from Client ",client_id)
            reply = "Enter valid command"
            connection.send(str.encode(reply))
                
# client connections
while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client,  ThreadCount+1))
    ThreadCount += 1
    print('Client Number: ' + str(ThreadCount))
ServerSocket.close()

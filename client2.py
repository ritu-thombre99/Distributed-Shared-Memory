import socket

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)
print(Response.decode('utf-8'))
while True:
    Input = input('Input: ')
    ClientSocket.send(str.encode(Input))
    if Input == "EXIT" or Input == "exit":
        print("Connection closed")
        ClientSocket.close()
        break
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))

ClientSocket.close()
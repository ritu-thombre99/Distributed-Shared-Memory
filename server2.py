import socket
import os
from _thread import *

# resources present in the server
current_resources = {'a':2,'b':5,'c':4}
allocated_resources = {}
# lists to maintain the list of client requests
client_queue = [] #FIFO
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
    connection.send(str.encode('Functionalities : alloc resource_ name resource_requirement and dealloc resource_name resources_to_be_freed\nAvailable resources :'+str(current_resources)))
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
        # alloc
        if from_client[0] == 'alloc':
            # resources not provided properly. send error
            if len(from_client) !=3:
                print("Client ",client_id,' did not provide resources correctly')
                reply = "Error : Invalid command. Please enter valid resources and requirements\nAvailable resources :"+str(current_resources)
                connection.send(str.encode(reply))
            else:
                # one client can get only one resource at a time. Check if client already has access to some resource
                if client_id in allocated_resources:
                    already_allocated = allocated_resources[client_id]
                    reply = "Client "+str(client_id)+" is already allocated "+str(already_allocated)
                    print(reply)
                    connection.send(str.encode(reply))
                else :
                    resource_name = from_client[1]
                    resource_requirement = int(from_client[2])
                    # resources are available for client requirement
                    if resource_requirement <= current_resources[resource_name]:
                        current_resources[resource_name] = current_resources[resource_name] - resource_requirement
                        reply = 'allocated '+resource_name+' '+str(resource_requirement)+"\nAvailable resources :"+str(current_resources)
                        # add client to allocated_resources with its allotted resoure list to prevent the same client for requesting multiple resources
                        allocated_resources[client_id] = (resource_name,resource_requirement)
                        print('For client ',client_id,':',reply)
                        connection.send(str.encode(reply))
                    # resources are not available for client requirement
                    else:
                        reply = 'Not enough resources available : '+str(current_resources)+'\nType:\n1. "get" to get the available resources\n2. "abort" to abort the request\n3. "wait" to wait for the resources\n'
                        connection.send(str.encode(reply))
                        client_reply_for_res = connection.recv(2048)
                        client_reply_for_res = client_reply_for_res.decode('utf-8')
                        # no available reource for the client
                        while client_reply_for_res == "get" and  current_resources[resource_name] == 0:
                            reply = 'No Available resources for:'+resource_name+'. Enter other choice'
                            connection.send(str.encode(reply))
                            client_reply_for_res = connection.recv(2048)
                            client_reply_for_res = client_reply_for_res.decode('utf-8')
                        # client is ready to adjust with the avaiable limited resources
                        if client_reply_for_res == "get":
                            # add client to allocated_resources with its allotted resoure list to prevent the same client for requesting multiple resources
                            allocated_resources[client_id] = (resource_name,current_resources[resource_name])
                            current_resources[resource_name] = 0
                            reply = 'allocated '+str(allocated_resources[client_id])+'\nAvailable resources :'+str(current_resources)
                            print('For client ',client_id,':',reply)
                            connection.send(str.encode(reply))
                        # client neither wants to ait nor wants limited resources
                        if client_reply_for_res == "abort":
                            reply = 'request aborted'+"\nAvailable resources :"+str(current_resources)
                            print('request for resources aborted by client ',client_id)
                            connection.send(str.encode(reply))
                        # client waits for resource to get freed
                        if client_reply_for_res == "wait":
                            print("Client ",client_id,' waiting for: ',resource_name,resource_requirement)
                            # add client to the waiting queue
                            client_queue.append((client_id,resource_name,resource_requirement))
                            while True:
                                current_state = current_resources[resource_name]
                                top_client = client_queue[0][0]
                                # check if client is at the top of the queue and its requirement for resource is satisfied
                                if top_client == client_id and current_state >= resource_requirement:
                                    current_resources[resource_name] = current_resources[resource_name] - resource_requirement
                                    # add client to allocated_resources with its allotted resoure list to prevent the same 
                                    # client for requesting multiple resources
                                    allocated_resources[client_id] = (resource_name,resource_requirement)
                                    reply = 'allocated '+str(allocated_resources[client_id])+"\nAvailable resources :"+str(current_resources)
                                    # remove client from the queue
                                    print('For client ',client_id,':',reply)
                                    client_queue.pop(0)
                                    connection.send(str.encode(reply))
                                    break
        elif from_client[0] == 'dealloc':
            # resources not provided properly. send error
            if len(from_client) !=3:
                print("Client ",client_id,' did not provide resources correctly')
                reply = "Error : Invalid command. Please enter valid resources and requirements\nAvailable resources :"+str(current_resources)
                connection.send(str.encode(reply))
            else:
                resource_name = from_client[1]
                resource_to_be_freed = int(from_client[2])
                # cleint trying to return resources that are not allotted to them
                if client_id not in allocated_resources:
                    print(resource_name," not alloted to client ",client_id)
                    reply = "Error: "+resource_name+" not was allotted to client\nAvailable resources :"+str(current_resources)
                    connection.send(str.encode(reply))
                else:
                    actually_alloted_resources = allocated_resources[client_id]
                    if resource_name != actually_alloted_resources[0]:
                        print(resource_name," not alloted to client ",client_id)
                        reply = "Error: "+resource_name+" not was allotted to client\nAvailable resources :"+str(current_resources)
                        connection.send(str.encode(reply))
                    elif actually_alloted_resources[1] != resource_to_be_freed:
                        print("Client ",client_id," is trying to return resources more or less than allocated")
                        reply = "Error: client is trying to return resources that are moe or less than alloted\nReturn the exact resources that were alocated\nAvailable resources :"+str(current_resources)
                        connection.send(str.encode(reply))
                    else:
                        # add back the resources
                        current_resources[resource_name] = current_resources[resource_name] + resource_to_be_freed
                        # remove client from allocated_resources list so that it can access other resources
                        allocated_resources.pop(client_id)
                        print("Client ",client_id," deallocated the resources")
                        reply = "Resources successfully deallocated\nAvailable resources :"+str(current_resources)
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

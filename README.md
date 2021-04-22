# Distributed-Server-Management
File reading/writing and resource allocation for multiple clients handled by centralized serve, implemented using multithreading in python

# 1. File reading/writing (code files - client1.py and server1.py)

• A storage at Server side, where multiple clients can access the storage. 
• Whenever a client requests a file check whether it is present or not:
  • if present, check whether it is being read or write by another client or not, 
  • if not process the request. 
• Notify the operations in the form of messages
  •	When a file being read by client notify the read only operation to requesting client.
  •	When a file being write by client notify the no access to the requesting client. 

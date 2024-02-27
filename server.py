from socket import *
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

def main():
    active_clients = {}
    files_permissions_dict = {} # A dictionary that contains (filename, clients allowed to view) pairs
    while True:
        connectionSocket, addr = serverSocket.accept()

        # The request received from the client
        request = connectionSocket.recv(1024).decode()
        request_list = request.split("-")

        # These is the implementation of all the [REQ] commands that we defined. 
        if request_list[0] == "REQ":

            if request_list[1] == "CONNECTION":
                # We have a request for connection
                if request_list[2] not in active_clients.keys():
                    active_clients[request_list[2]] = ("CONNECTED", addr[0])
                    print("Currently Active Clients: ", active_clients)
                    connectionSocket.send("RET-CONNSUCCESS".encode())
                else:
                    connectionSocket.send("RET-CONNFAIL".encode())
                

            # Returns the current client list from the server, (only available clients are returned) the list returned is a space seperated list of names with the headers RET-CLIENTLIST prepended
            if request_list[1] == "CLIENT_LIST":
                available_clients = "RETURN-CLIENTLIST-" + get_available_clients(active_clients)
                connectionSocket.send(available_clients.encode())

            # Returns the IP address and listening port of a client requested, the string sent back is just the ip and port seperated by a space with the headers RET-CLIENTINFO prepended
            if request_list[1] == "CLIENT":
                client_id = request_list[2]
                if client_id in active_clients.keys():
                    udp_ip_of_client_requested = active_clients[client_id][1]
                    udp_ip_port = active_clients[client_id][2]
                    connectionSocket.send(("RET-CLIENTINFO-" + udp_ip_of_client_requested + " " +  udp_ip_port).encode())

            if request_list[1] == "FILES":
                connectionSocket.send("RET-FILELIST" + "-".join(files_permissions_dict.keys()))

        elif request_list[0] == "COMMAND":
            if request_list[1] == "AVAIL":
                # This command changes the status of a client to available on the server's list.
                if (request_list[2] in active_clients.keys()):
                    active_clients[request_list[2]] = ("AVAILABLE", ) + (active_clients[request_list[2]][1],) + (request_list[3],)
                    print(f"Added a new user: {request_list[2]} to the server.")
                    print("Currently Active Clients: ", active_clients)
                else:
                    print("ERROR: An availability check without prior connection attempted")

            if request_list[1] == "NAVAIL":
                # This command removes a client from the list of connected clients
                if (request_list[2] in active_clients.keys()):
                    del active_clients[request_list[2]]
                    print(f"Removed {request_list[2]} from the server.")
                    print("Currently Active Clients: ", active_clients)
                else:
                    print("ERROR: Invalid operation involving NAVAIL command")

            if request_list[1] == "CHANGEVIS":
                # This command will change visibility on the server from available to only connected 
                if (request_list[2] in active_clients.keys()):
                    active_clients[request_list[2]] = ("CONNECTED", ) + (active_clients[request_list[2]][1],)
                    print(f"Changed the visibility of {request_list[2]} from CONNECTED to AVAILABLE")
                    print("Currently Active Clients: ", active_clients)
                else:
                    print("ERROR: Invalid operation involving CHANGEVIS")
            
            if request_list[1] == "UPLOAD":
                # Client is trying to upload a file to the server
                if request_list[2] == "ALL":
                    # The file is suitable for all to see
                    filename = request_list[3] + " " + request_list[5] # this ensures the names are unique
                    if filename not in files_permissions_dict.keys(): 
                        files_permissions_dict[filename] = "ALL"
                        # Write the file to disk locally on the server
                        with open(f"{filename.split(" ")[0]}", "w") as file:
                            # Write the string data to the file
                            file.write(request_list[6]) # will write the file to disk locally
                    
                else:
                    filename = request_list[3] + " " + request_list[5]
                    if filename not in files_permissions_dict.keys():
                        files_permissions_dict[filename] = request_list[2]
                        with open(f"{filename}", "w") as file:
                            # Write the string data to the file
                            file.write(request_list[6]) # will write the file to disk locally
                    # Only one client is allowed to see the file
                            
                # Now what do we return? Probably a message saying file was received
                connectionSocket.send("CONFIRM_FILE_RECEIVED")

            

            if request_list[1] == "DOWNLOAD":
                # Need to ensure the client who sent the message has access
                file_name = request_list[2]
                if file_name in files_permissions_dict.keys():
                    # should be since it would be checked for on the client side
                    if files_permissions_dict[filename] == "ALL":
                        # it's fine to just transmit it back to the client that sent the request
                        with open("example.txt", "r") as file:
                            # Read the entire contents of the file
                            file_contents = file.read()
                            connectionSocket.send(file_contents.encode()) # Send the file to the client that requested it

                    elif files_permissions_dict[filename] == request_list[3]: # if the only allowed user has requested it allow the download
                        with open("example.txt", "r") as file:
                            # Read the entire contents of the file
                            file_contents = file.read()
                            connectionSocket.send(file_contents.encode())

                    else: # happens if we try to access a document we don't have permission to access
                        # Access denied 
                        connectionSocket.send("RET-ACCESSDENIED")

        connectionSocket.close()


def get_available_clients(d):
    out = ''
    for client in d.keys():
        if d[client][0] == "AVAILABLE":
            out += client + " "
    return out

main()

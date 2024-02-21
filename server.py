from socket import *
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

def main():
    active_clients = {}
    while True:
        connectionSocket, addr = serverSocket.accept()

        # The request received from the client
        request = connectionSocket.recv(1024).decode()
        request_list = request.split("-")
        if request_list[0] == "REQ":

            if request_list[1] == "CONNECTION":
                # We have a request for connection
                if request_list[2] not in active_clients.keys():
                    active_clients[request_list[2]] = ("CONNECTED", addr[0])
                    print("Currently Active Clients: ", active_clients)

            if request_list[1] == "CLIENT_LIST":
                available_clients = get_available_clients(active_clients)
                connectionSocket.send(available_clients.encode())

            if request_list[1] == "CLIENT":
                client_id = request_list[2]
                if client_id in active_clients.keys():
                    udp_ip_of_client_requested = active_clients[client_id][1]
                    udp_ip_port = active_clients[client_id][2]
                    connectionSocket.send((udp_ip_of_client_requested + " " +  udp_ip_port).encode())


        elif request_list[0] == "COMMAND":
            if request_list[1] == "AVAIL":
                if (request_list[2] in active_clients.keys()):
                    active_clients[request_list[2]] = ("AVAILABLE", ) + (active_clients[request_list[2]][1],) + (request_list[3],)
                    print("Currently Active Clients: ", active_clients)
                else:
                    print("ERROR: An availability check without prior connection attempted")


        connectionSocket.close()

def get_available_clients(d):
    out = ''
    for client in d.keys():
        if d[client][0] == "AVAILABLE":
            out += client
    return out

main()

from socket import *

client_id = ""
connectedToServer = False
connectedToPeer = False
client_connected = ""

def main():
    print("Welcome to Shit WhatsApp")
    showMainMenu()

def showMainMenu():
    global connectedToServer
    global client_id
    global connectedToPeer
    global client_connected

    if not connectedToServer:
        n = input("1: Connect to server, 2: See list of active users:\n")
        if n == '1':
            # we connect to the server 
            name = input("Enter your name:\n")
            client_id = name
            sendMessageToTCPServer(CreateRequestConnectionMessage(name))
            connectedToServer = True # We have now established a connection to the server
            showMainMenu()

        if n == '2':
            response = sendMessageToTCPServer(CreateRequestClientListMessage())
            if response == "":
                print("No available clients at this moment")
                showMainMenu()
            else:
                print("Current online users:", response, sep = "\n")
                userToConnectTo = input("Please select a user you wish to connect to:\n")
                # Can do some input validation here
                client_ip_and_port = sendMessageToTCPServer(CreateRequestClientInfoMessage(userToConnectTo))
                print(f"{userToConnectTo}'s ip is:", client_ip_and_port)
                ip = client_ip_and_port.split(" ")[0]
                port = client_ip_and_port.split(" ")[1]
                SendOpeningUDPMessage(ip, port)
                # Now we can send a message to the client waiting


    else:
        n = input("1: Wait for connection from a peer, 2: Change Visibility Level:\n")
        if n == '1':
            udp_port = input("Enter the udp port number you will be listening on:\n")
            sendMessageToTCPServer(CreateAssertAvaialbleMessage(client_id, udp_port))
        
            # Now we are listed as available on the server
            # now we can just wait for direct communication?
            serverPort = 12000
            serverSocket = socket(AF_INET, SOCK_DGRAM)
            serverSocket.bind(('', serverPort))

            while True: # Wait for communication from a client
                message, clientAddress = serverSocket.recvfrom(2048)
                global connectedToPeer
                global client_connected
                print("Message Received:", message)
                if message.decode() == "REQ-COMMUNICATION":
                    print("Request to communicate received")

                    # Three of these because UDP is unreliable as fuck
                    serverSocket.sendto("OKAY".encode(), clientAddress)
                    serverSocket.sendto("OKAY".encode(), clientAddress)
                    serverSocket.sendto("OKAY".encode(), clientAddress)
                    
                    connectedToPeer = True
                    break
                else:
                    continue

            if connectedToPeer:
                ConnectionAchievedRendezvous()

def SendOpeningUDPMessage(ip, port):
    print("Trying to send opening message to", ip, port)
    PeerName = ip
    PeerPort = int(port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(CreateRequestPeerToPeerCommunication().encode(),(PeerName, PeerPort))

    Message_Received, serverAddress = clientSocket.recvfrom(2048)
    if Message_Received.decode() == "OKAY":
        global connectedToPeer
        global client_connected
        connectedToPeer = True
        client_connected = serverAddress
    clientSocket.close()
    if connectedToPeer:
        ConnectionAchievedRendezvous()

def ConnectionAchievedRendezvous():
    print("Connected")

def sendMessageToTCPServer(message):
    serverName = "196.24.173.238"
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    clientSocket.send(message.encode())
    modifiedSentence = clientSocket.recv(1024)
    clientSocket.close()
    return modifiedSentence.decode()


def CreateRequestConnectionMessage(name):
    return f"REQ-CONNECTION-{name}"

def CreateAssertAvaialbleMessage(name, udp_port):
    return f"COMMAND-AVAIL-{name}-{udp_port}"

def CreateRequestClientListMessage():
    return f"REQ-CLIENT_LIST"

def CreateRequestClientInfoMessage(user):
    return f"REQ-CLIENT-{user}"

def CreateRequestPeerToPeerCommunication():
    return f"REQ-COMMUNICATION"
main()

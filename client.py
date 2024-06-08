# programmers: Adam Beck, Thanh Nguyen
#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime
import sys

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message
message = "DISCOVER " + MAC
print("client: This is the message: " + message)
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Parse the client messages
def parse_message(message):
    parsed_message = message.split()
    return parsed_message

# checks if a timestamp is expired
# returns true if it is expired
# false if not
def isExpired(timestamp):
    if(datetime.fromisoformat(timestamp) <= datetime.fromisoformat(datetime.now().isoformat())):
        return True
    return False

def matchesMAC(sent_mac):
    if (sent_mac == MAC):
        return True
    return False

def displayMenu():
    print("client: Please select option 1, 2, or 3..")
    print("client: 1: release")
    print("client: 2: renew")
    print("client: 3: quit")
    option = input()
    if (option == "1"):
        release_msg = "RELEASE " + MAC + " " + msg[2] + " " + msg[3]
        print("client: This is the RELEASE message: " + release_msg)
        clientSocket.sendto(release_msg.encode(), (SERVER_IP, SERVER_PORT))
        displayMenu()
    elif (option == "2"):
        # checks if the record is expired
        if (isExpired(msg[3])):
            # record is expired, sending discover message
            print("client: Expired..")
            discover_msg = "DISCOVER " + MAC
            print("client: This is the DISCOVER message: " + discover_msg)
            clientSocket.sendto(discover_msg.encode(), (SERVER_IP, SERVER_PORT))
        else:
            # record is not expired, sending renew message
            print("client: Not expired..")
            renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
            print("client: This is the RENEW message: " + renew_msg)
            clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
    elif (option == "3"):
        print("client: Now terminating...")
        sys.exit()
    else:
        print("client: Error")
        displayMenu()

# LISTENING FOR RESPONSE
while True:
    message, addr = clientSocket.recvfrom(4096)
    msg = parse_message(message.decode())
    if(msg[0] == "OFFER"):
        print("client: Recieved an OFFER message")
        if (matchesMAC(msg[1])):
            print("client: MAC address matches")
            if(isExpired(msg[3]) == False):
                print("client: Not Expired")
                reqmsg = "REQUEST " + MAC + " " + msg[2] + " " + msg[3]
                print("client: This is the REQUEST message: " + reqmsg)
                clientSocket.sendto(reqmsg.encode(), (SERVER_IP, SERVER_PORT))
            else:
                print("client: Expired")
                renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
                print("client: This is the RENEW message: " + renew_msg)
                clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
        else:
            print("client: MAC address does not match, Now terminating")
            sys.exit()
    elif(msg[0] == "ACKNOWLEDGE"):
        print("client: Recieved an ACKNOWLEDGE message")
        if (matchesMAC(msg[1])):
            print("client: MAC address matches")
            if(isExpired(msg[3]) == False):
                print("client: Not Expired")
                print("client: IP address " + msg[2] + " was assgined to this client and will expire at time " + msg[3])
                displayMenu()
            else:
                print("client: Expired")
                renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
                print("client: This is the RENEW message: " + renew_msg)
                clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
        else:
            print("client: MAC address does not match, Now terminating")
            sys.exit()
    elif(msg[0] == "DECLINE"):
        print("client: DECLINE message recieved from server, Now terminating")
        sys.exit()
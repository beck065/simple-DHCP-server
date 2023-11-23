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
print("This is the message: " + message)
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Parse the client messages
def parse_message(message):
    parsed_message = message.split()
    print(parsed_message)
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
    print("Please select option 1, 2, or 3..")
    print("1: release")
    print("2: renew")
    print("3: quit")
    option = input()
    if (option == "1"):
        release_msg = "RELEASE " + MAC + " " + msg[2] + " " + msg[3]
        print("This is the RELEASE message: " + renew_msg)
        clientSocket.sendto(release_msg.encode(), (SERVER_IP, SERVER_PORT))
    elif (option == "2"):
        renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
        print("This is the RENEW message: " + renew_msg)
        clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
    elif (option == "3"):
        print("Now terminating...")
        sys.exit()
    else:
        print("Error")
        displayMenu()

# LISTENING FOR RESPONSE
while True:
    message, addr = clientSocket.recvfrom(4096)
    msg = parse_message(message.decode())
    if(msg[0] == "OFFER"):
        print("Recieved an OFFER message")
        if (matchesMAC(msg[1])):
            print("MAC address matches")
            if(isExpired(msg[3]) == False):
                print("Not Expired")
                reqmsg = "REQUEST " + MAC + " " + msg[2] + " " + msg[3]
                print("This is the REQUEST message: " + reqmsg)
                clientSocket.sendto(reqmsg.encode(), (SERVER_IP, SERVER_PORT))
            else:
                print("Expired")
                renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
                print("This is the RENEW message: " + renew_msg)
                clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
        else:
            print("MAC address does not match, Now terminating")
            sys.exit()
    elif(msg[0] == "ACKNOWLEDGE"):
        print("Recieved an ACKNOWLEDGE message")
        if (matchesMAC(msg[1])):
            print("MAC address matches")
            if(isExpired(msg[3]) == False):
                print("Not Expired")
                print("IP address " + msg[2] + " was assgined to this client and will expire at time " + msg[3])
                displayMenu()
            else:
                print("Expired")
                renew_msg = "RENEW " + MAC + " " + msg[2] + " " + msg[3]
                print("This is the RENEW message: " + renew_msg)
                clientSocket.sendto(renew_msg.encode(), (SERVER_IP, SERVER_PORT))
        else:
            print("MAC address does not match, Now terminating")
            sys.exit()
    elif(msg[0] == "DECLINE"):
        print("DECLINE message recieved from server, Now terminating")
        sys.exit()
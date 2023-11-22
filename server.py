#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

# records class
class Records:
    def __init__(self):
        self.__max_records = 20
        self.__records = []

    # searches records for an entry with the given mac address
    def searchMac(self, mac_address):
        for record in records:
            if record.mac == mac_address:
                return record
        return None

    def isFull(self):
        if len(self.__records) < self.__max_records:
            return False
        return True

    # finds the first expired record
    # if none are expired, returns None
    def firstExpired(self):
        for record in records:
            if record.isExpired:
                return record
        return None

    # creates a new record for an ip address
    def createRecord(self, mac_address):
        if records.isFull() == False and records.searchMac(mac_address) == None:
            new_record = Record(len(self.__records), mac_address)
            self.__records.append(new_record)
            return new_record
        return None

# record class
class Record:
    def __init__(self, record_num, mac_address):
        self.num = record_num
        self.mac = mac_address
        self.ip = ip_addresses[record_num-1]
        self.timestamp = datetime.fromisoformat(datetime.now().isoformat()) + timedelta(seconds=60) # expiration date
        self.acked = False

    def isExpired(self):
        if self.timestamp < datetime.fromisoformat(datetime.now().isoformat()):
            return True
        return False

    def updateTimestamp(self):
        self.timestamp = datetime.fromisoformat(datetime.now().isoformat()) + timedelta(seconds=60) # expiration date

    # for use in ACK and OFFER messages
    def formatted(self):
        return self.mac + " " + self.ip + " " + self.timestamp

    # for use in LIST
    def string(self):
        return None

    # updates the record with a new mac
    # also sets ack to false
    # and updates the timestamp
    def updateMac(self, mac_address):
        self.mac = mac_address
        self.acked = False
        self.updateTimestamp()

# Choose a data structure to store your records
records = Records()

# Parse the client messages
def parse_message(message):
    parsed_message = message.split()
    print(parsed_message)
    return parsed_message


# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0]
    print(request)
    if request == "LIST":
        print("This is a LIST message")
    elif request == "DISCOVER":
        print("This is a DISCOVER message")
        # search records for MAC
        record = records.searchMac(parsed_message[1])
        if record != None:
            # mac address has a record in records
            # check if timestamp is valid
            if record.isExpired():
                # record is expired
                # send OFFER message to client
                record.updateTimestamp()
                record.acked = False
                return "OFFER " + record.formatted()
            else:
                # record is not expired
                # send ACK message
                record.acked = True
                return "ACKNOWLEDGE " + record.formatted()
        else:
            # no record found for mac address
            # check if records is full
            if records.isFull():
                # list of records is full
                # check if any records are expired
                expired_record = records.firstExpired()
                if expired_record != None:
                    # found an expired record
                    # update mac and send offer
                    expired_record.updateMac(parsed_message[1])
                    return "OFFER " + expired_record.formatted()
                else:
                    # no expired records
                    # send DECLINED message
                    return "DECLINED"
            else:
                # list of records is not full
                # create a new record for the mac address
                new_record = records.createRecord(parsed_message[1])
                # send OFFER message
                return "OFFER " + new_record.formatted()

    elif request == "REQUEST":
        print("This is a REQUEST message")
    elif request == "RELEASE":
        print("This is a RELEASE message")
    elif request == "RENEW":
        print("This is a RENEW message")


# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)

        parsed_message = parse_message(message.decode())

        response = dhcp_operation(parsed_message)

        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
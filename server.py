# programmers: Adam Beck, Thanh Nguyen
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
        self.__max_records = 14
        self.__records = []

    # searches records for an entry with the given mac address
    def searchMac(self, mac_address):
        for record in self.__records:
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
        for record in self.__records:
            if record.isExpired():
                return record
        return None

    # creates a new record for an ip address
    def createRecord(self, mac_address):
        if records.isFull() == False and records.searchMac(mac_address) == None:
            new_record = Record(len(self.__records), mac_address)
            self.__records.append(new_record)
            return new_record
        return None
    
    def createList(self):
        list = ""
        for record in self.__records:
            # only returns non-expired records
            if record.isExpired() == False:
                list = list + "[" + record.formatted() + "]\n"
        return list

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
        return self.mac + " " + self.ip + " " + self.timestamp.isoformat()

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
    return parsed_message


# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0]
    print("server: " + request)
    if request == "LIST":
        print("server: Received a LIST message")
        return records.createList()
    elif request == "DISCOVER":
        print("server: Received a DISCOVER message")
        # search records for MAC
        print("server: Searching for record: " + parsed_message[1])
        record = records.searchMac(parsed_message[1])
        if record != None:
            # mac address has a record in records
            # check if timestamp is valid
            print("server: Found record for " + record.formatted())
            if record.isExpired():
                # record is expired
                # send OFFER message to client
                print("server: Record expired..")
                record.updateTimestamp()
                record.acked = False
                message = "OFFER " + record.formatted()
                print("server: Sending " + message + " message")
                return message
            else:
                # record is not expired
                # send ACK message
                print("server: Record not expired..")
                record.acked = True
                message = "ACKNOWLEDGE " + record.formatted()
                print("server: Sending " + message + " message")
                return message
        else:
            # no record found for mac address
            print("server: No record found..")
            # check if records is full
            if records.isFull():
                # list of records is full
                print("server: List of records is full..")
                # check if any records are expired
                expired_record = records.firstExpired()
                if expired_record != None:
                    # found an expired record
                    print("server: Found expired record " + expired_record.formatted() + " updating MAC address to " + parsed_message[1])
                    # update mac and send offer
                    expired_record.updateMac(parsed_message[1])
                    message = "OFFER " + expired_record.formatted()
                    print("server: Sending " + message)
                    return message
                else:
                    # no expired records
                    print("server: No expired records..")
                    # send DECLINE message
                    message = "DECLINE"
                    print("server: Sending " + message)
                    return message
            else:
                # list of records is not full
                print("server: List of records not full..")
                # create a new record for the mac address
                print("server: Creating a new record for " + parsed_message[1])
                new_record = records.createRecord(parsed_message[1])
                # send OFFER message
                message = "OFFER " + new_record.formatted()
                print("server: Sending " + message)
                return message
    elif request == "REQUEST":
        print("server: Received a REQUEST message")
        record = records.searchMac(parsed_message[1])
        msgip = parsed_message[2]
        if record != None:
            if record.ip == msgip:
                if record.isExpired():
                    print("server: Record expired..")
                    message = "DECLINE " + record.formatted()
                    print("server: Sending " + message)
                    return message
                else:
                    print("server: Record not expired..")
                    record.acked = True
                    message = "ACKNOWLEDGE " + record.formatted()
                    print("server: Sending " + message)
                    return message  
            else:
                print("server: IP does not match record..")
                message = "DECLINE " + record.formatted()
                print("server: Sending " + message)
                return message
        else:
            # no record found for mac address
            print("server: No record found..")
            message = "DECLINE " + record.formatted()
            print("server: Sending " + message)
            return message
    elif request == "RELEASE":
        print("server: Received a RELEASE message")
        record = records.searchMac(parsed_message[1])
        if record != None:
            # see if record is expired
            if record.isExpired() == False:
                # record is not expired, release as normal
                record.timestamp = datetime.fromisoformat(datetime.now().isoformat())
                record.acked = False
                print("server: Releasing " + record.mac + " for IP " + record.ip)
            else:
                # record is expired, do not need to release
                print("server: Already released")
        return None
    elif request == "RENEW":
        print("server: Received a RENEW message")
        record = records.searchMac(parsed_message[1])
        if record != None:
            print("server: Renewing timestamp for " + record.mac)
            record.updateTimestamp()
            record.acked = True
            msg = "ACKNOWLEDGE " + record.formatted()
            print("server: Sending " + msg)
            return msg
        else:
            # no record found for mac address
            print("server: No record found..")
            # check if records is full
            if records.isFull():
                # list of records is full
                print("server: List of records is full..")
                # check if any records are expired
                expired_record = records.firstExpired()
                if expired_record != None:
                    # found an expired record
                    print("server: Found expired record " + expired_record.formatted() + " updating MAC address to " + parsed_message[1])
                    # update mac and send offer
                    expired_record.updateMac(parsed_message[1])
                    message = "OFFER " + expired_record.formatted()
                    print("server: Sending " + message)
                    return message
                else:
                    # no expired records
                    print("server: No expired records..")
                    # send DECLINE message
                    message = "DECLINE"
                    print("server: Sending " + message)
                    return message
            else:
                # list of records is not full
                print("server: List of records not full..")
                # create a new record for the mac address
                print("server: Creating a new record for " + parsed_message[1])
                new_record = records.createRecord(parsed_message[1])
                # send OFFER message
                message = "OFFER " + new_record.formatted()
                print("server: Sending " + message)
                return message


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

        if response != None:
            server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
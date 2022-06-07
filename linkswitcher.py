from socket import *
import threading
import time
import random
import subprocess

active_link_num = 0


def main():
    rflink = Link("rflink1", "d6:6b:92:86:80:c0")
    oplink = Link("rflink2", "ca:7e:68:a4:c3:17")
    threading.Thread(target=send_data, args=(rflink, oplink)).start()

    global active_link_num
    print("press enter to switch active link")
    while True:
        input()
        active_link_num = 1 if active_link_num == 0 else 0
        print(f"link {active_link_num} active")


def send_data(rf, optic):
    global active_link_num

    while True:
        data = getdata()
        if active_link_num == 0:
            rf.send(data)
        else:
            optic.send(data)
        time.sleep(0.1)


class Link:
    def __init__(self, interface, mac_addr):
        execute(f"ip link set {interface} up")
        self.interface = interface
        self.s = socket(AF_PACKET, SOCK_RAW)
        self.s.bind((interface, 0))
        self.mac_bytearr = bytearray.fromhex(mac_addr.replace(":", ""))

    def send(self, payload):
        # src=fe:ed:fa:ce:be:ef, dst=52:54:00:12:35:02, type=0x0800 (IP)
        ethernet_header = bytearray()
        ethernet_header += bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])  # dst
        ethernet_header += self.mac_bytearr
        ethernet_header += bytearray([0x08, 0x00])
        self.s.send(ethernet_header + payload)


def getdata():
    return bytearray(random.getrandbits(8) for _ in range(1500))

def execute(command):
    print(f"Executing command: '{command}'")
    cmdarr = command.split()
    result = subprocess.run(cmdarr, text=True, capture_output=True)

    return result.stdout

main()

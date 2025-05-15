import arp
import constants
import multiprocessing
import os
import subprocess
from Dns_Server import DNSServer


os.chdir(os.path.dirname(__file__))

class NetworkManager:
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.current_mode = None  # Track the current mode
        self.user_ip = ""   # if the parent want to set specific ip
        
        # initilaize values to store later
        self.arp_instance = None
        self.flask_process = None  
        self.dns_Server = None
        
        self.dns_Server = DNSServer(constants.this_pc_ip)
    
    def deactivate_sniffer(self):
        self.arp_instance.stop_poisoning()
        # Kill the Flask server process
        if self.flask_process:
            print("kill")
            self.flask_process.kill()
            self.flask_process = None
        self.dns_Server.stop()
        print("ARP and DNS spoofing stopped")


    def sniffer(self,list_type):
        if self.user_ip == "":
            self.arp_instance = arp.Arp(constants.broadcast_ip, constants.dns_server_ip)
        else:
            self.arp_instance = arp.Arp(self.user_ip, constants.dns_server_ip)
        self.arp_instance.start_poisoning()
        print(self.user_ip)
        # Start Flask server in a separate process
        self.flask_process = subprocess.Popen(["python", "Flask_Server.py"])
        self.dns_Server.start(list_type)
        print(f"Network closure for black list started")



    def network_closure(self):
        if self.user_ip == "":
            self.arp_instance = arp.Arp(constants.broadcast_ip, constants.gateway_ip)
            print("Network closed")
        else:
            self.arp_instance = arp.Arp(self.user_ip, constants.gateway_ip)
            print(f"Network closed for user with IP: {self.user_ip}")
        self.arp_instance.start_poisoning()

    def deactivate_network_closure(self):
        self.arp_instance.stop_poisoning()
        print("Network reopened")

    def deactivate_current_mode(self):
        if self.current_mode == "No access to blacklisted sites" or self.current_mode == "Access to whitelisted sites only":
            self.deactivate_sniffer()
        elif self.current_mode == "Network closure":
            self.deactivate_network_closure()


    def activate_mode(self, selected_mode, app_status, user_ip, callback=None):
        if self.current_mode is not None:
            self.deactivate_current_mode()  
        if app_status == "Off":
            print("Application status is off. No action will be taken.")
            self.current_mode = None
            return
        self.user_ip = user_ip
        if selected_mode == "No access to blacklisted sites":
            self.sniffer("B")
        elif selected_mode == "Access to whitelisted sites only":
            self.sniffer("W")
        elif selected_mode == "Network closure":
            self.network_closure()
        self.current_mode = selected_mode


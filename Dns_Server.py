import constants
import socket
import threading
import time
from dnslib import DNSHeader, DNSQuestion, DNSRecord, A, QTYPE, RCODE, RR
from scapy.all import DNS, IP, UDP, conf, get_if_hwaddr, send, sniff
import utils


class DNSServer:
    DNS_PORT = 53
    BUFFER_SIZE = 1024

    def __init__(self, bind_address='0.0.0.0'):
        self.bind_address = bind_address
        self.redirect_ip = bind_address  # Set redirect IP to the bind address
        self.stop_event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.bind_address, self.DNS_PORT))
        
        self.local_mac = get_if_hwaddr(conf.iface)

        self.real_dns_ip = constants.dns_server_ip

        self.white_list = utils.load_sites_from_file(constants.whitelisted_sites_path)
        self.black_list = utils.load_sites_from_file(constants.blocked_sites_path)
        self.list_type = "B" #black list(B) or white list(B)

    def handle_dns_request(self, data):
        request = DNSRecord.parse(data)
        qname = str(request.q.qname)
        qtype = request.q.qtype
        transaction_id = request.header.id
        response_data = None
        if self.list_type == "B":  # No access to specific websites (Blacklist mode)
            if self.search_qname(qname.lower(), self.black_list):
                response_data = self.handle_special_packet(transaction_id, qname, qtype)
            else:
                response_data = self.forward_dns_request(data)
        else:  # Access only to specific websites (Whitelist mode)
            if self.search_qname(qname.lower(), self.white_list):
                response_data = self.forward_dns_request(data)
            else:
                response_data = self.handle_special_packet(transaction_id, qname, qtype)
        return response_data
    
    def handle_special_packet(self, transaction_id, qname, qtype):
        if qtype == QTYPE.A:
            print(f"Redirecting {qname} to IPv4 address {self.redirect_ip}")
            packet = self.build_dns_response(transaction_id, qname, self.redirect_ip, QTYPE.A)
        elif qtype == QTYPE.AAAA:
            print(f"Received AAAA query for {qname}, returning NOERROR with no answers")
            packet = self.build_dns_response_no_ipv6(transaction_id, qname)
        else:
            print(f"Can't handle {qname} packet. fuck the packet")
            packet = None
        return packet

    def search_qname(self, qname, sites_list):
        for site in sites_list:
            if site in qname:
                return True
        return False

    def forward_dns_request(self, request_data):
        try:
            self.sock.sendto(request_data, ('8.8.8.8', self.DNS_PORT))
            self.sock.settimeout(5)  # Set a timeout for the upstream request
            response_data, _ = self.sock.recvfrom(self.BUFFER_SIZE)
            return response_data
        except Exception as e:
            print(f"Error forwarding DNS request: {e}")
            return None
    
    def build_dns_response_no_ipv6(self, transaction_id, qname):
        response = DNSRecord(
            DNSHeader(id=transaction_id, qr=1, aa=1, ra=1, rcode=RCODE.NOERROR),
            q=DNSQuestion(qname, QTYPE.AAAA)
        )
        print(f"DNS Response for {qname} -> No AAAA record available")
        return response.pack()

    def build_dns_response(self, transaction_id, qname, ip_address, qtype):
        response = DNSRecord(
            DNSHeader(id=transaction_id, qr=1, aa=1, ra=1),
            q=DNSQuestion(qname, qtype)
        )
        if qtype == QTYPE.A:
            response.add_answer(RR(qname, QTYPE.A, rdata=A(ip_address), ttl=60))
        print(f"DNS Response for {qname} -> {ip_address}")
        return response.pack()

    def run_dns_server(self):
        try:
            print(f"DNS server started on {self.bind_address}:{self.DNS_PORT}")
            while not self.stop_event.is_set():
                print("Waiting for DNS packets...")
                try:
                    packets = sniff(filter="udp and port 53", count=1, timeout=4)
                    packet = packets[0]
                    if packet:
                        if packet.dst == self.local_mac and packet[IP].dst == self.real_dns_ip:
                            data = bytes(packet[UDP].payload)
                            addr = (packet[IP].src, packet[UDP].sport)
                            response_data = self.handle_dns_request(data)
                            if response_data:
                                ip_packet = IP(src=self.real_dns_ip, dst=packet[IP].src) / \
                                            UDP(sport=53, dport=packet[UDP].sport) / \
                                            DNS(response_data)
                                send(ip_packet, verbose=False)
                                print(f"Sent response to {addr}")
                except IndexError:
                    print("Index error occurred, skipping packet processing.")
        except OSError as e:
            print(f"Failed to bind to address {self.bind_address}:{self.DNS_PORT} - {e}")
        except Exception as e:
            print(f"Server error: {e}")


    def start(self, list_type):
        self.stop_event.clear()
        self.list_type = list_type
        
        self.white_list = utils.load_sites_from_file(constants.whitelisted_sites_path)
        self.black_list = utils.load_sites_from_file(constants.blocked_sites_path)

        self.server_thread = threading.Thread(target=self.run_dns_server)
        self.server_thread.start()
        
    def stop(self):
        self.stop_event.set()
        self.server_thread.join()

def main():
    dns_server = DNSServer()
    dns_server.start("B")  # Start the DNS server with the black list mode initially

    while True:
        try:
            # Reload the white and black lists every 10 seconds
            time.sleep(10)
            dns_server.white_list = utils.load_sites_from_file(constants.whitelisted_sites_path)
            dns_server.black_list = utils.load_sites_from_file(constants.blocked_sites_path)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            dns_server.stop()  # Stop the DNS server
            break

if __name__ == "__main__":
    pass


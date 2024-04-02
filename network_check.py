import os
import netifaces
import socket
import ipaddress

def get_this_pc_ip():
    # Use socket library to get the IP address of this PC
    return socket.gethostbyname(socket.gethostname())

def get_gateway_ip():
    # Get default gateway information
    gateways = netifaces.gateways()

    default_gateway_info = gateways.get('default', {})
    if netifaces.AF_INET in default_gateway_info:
        return default_gateway_info[netifaces.AF_INET][0]
    return None

def get_broadcast_ip(ip_address, subnet_mask):
    # Convert IP address and subnet mask to IPv4Address objects
    ip_address = ipaddress.IPv4Address(ip_address)
    subnet_mask = ipaddress.IPv4Address(subnet_mask)

    # Calculate network address
    network_address = ipaddress.IPv4Network(ip_address, subnet_mask)

    # Calculate broadcast IP address
    broadcast_ip = network_address.broadcast_address

    return str(broadcast_ip)

def get_subnet_mask():
    # Use netifaces to get the subnet mask
    addresses = netifaces.ifaddresses(netifaces.interfaces()[0])
    if netifaces.AF_INET in addresses:
        return addresses[netifaces.AF_INET][0]['netmask']
    return None

def update_constants_file(this_pc_ip, gateway_ip, broadcast_ip, subnet_mask):
    # Check if constants.py exists
    if not os.path.exists("constants.py"):
        # If the file doesn't exist, create it and write the lines
        with open("constants.py", "w") as file:
            file.write(f"this_pc_ip = '{this_pc_ip}'\n")
            file.write(f"GATEWAY_IP = '{gateway_ip}'\n")
            file.write(f"broadcast_ip = '{broadcast_ip}'\n")
            file.write(f"subnet_mask = '{subnet_mask}'\n")
        return

    # Read the content of constants.py
    with open("constants.py", "r") as file:
        lines = file.readlines()

    # Check if lines exist in the file
    lines_exist = {
        "this_pc_ip": False,
        "GATEWAY_IP": False,
        "broadcast_ip": False,
        "subnet_mask": False
    }

    for line in lines:
        for key in lines_exist:
            if line.startswith(key):
                lines_exist[key] = True

    # Append missing lines to the file
    with open("constants.py", "a") as file:
        for key, exists in lines_exist.items():
            if not exists:
                if key == "GATEWAY_IP":
                    value = gateway_ip
                else:
                    value = locals()[key]
                file.write(f"{key} = '{value}'\n")

def main():
    # Get values from network check functions
    this_pc_ip = get_this_pc_ip()
    gateway_ip = get_gateway_ip()
    subnet_mask = get_subnet_mask()
    broadcast_ip = get_broadcast_ip(this_pc_ip, subnet_mask)

    # Update constants.py with new values
    update_constants_file(this_pc_ip, gateway_ip, broadcast_ip, subnet_mask)

if __name__ == '__main__':
    main()

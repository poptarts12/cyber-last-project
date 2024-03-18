import netifaces
import socket

def get_this_pc_ip():
    # Use socket library to get the IP address of this PC
    return socket.gethostbyname(socket.gethostname())

def get_gateway_ip():
    # Get default gateway information
    gateways = netifaces.gateways()

    default_gateway_info = gateways.get('default', {})
    print(default_gateway_info)
    if netifaces.AF_INET in default_gateway_info:
        return default_gateway_info[netifaces.AF_INET][0]
    return None

def get_active_ips(subnet):
    # Use netifaces to get the active IPs in the subnet
    active_ips = []
    for address in netifaces.interfaces():
        addresses = netifaces.ifaddresses(address)
        if netifaces.AF_INET in addresses:
            for interface in addresses[netifaces.AF_INET]:
                ip = interface['addr']
                if ip.startswith(subnet):
                    active_ips.append(ip)
    return active_ips

def get_broadcast_ip(subnet):
    # Calculate broadcast IP from subnet
    parts = subnet.split(".")
    parts[-1] = "255"
    return ".".join(parts)

def get_subnet_mask():
    # Use netifaces to get the subnet mask
    addresses = netifaces.ifaddresses(netifaces.interfaces()[0])
    if netifaces.AF_INET in addresses:
        return addresses[netifaces.AF_INET][0]['netmask']
    return None

def update_constants_file(this_pc_ip, gateway_ip, active_ips, broadcast_ip, subnet_mask):
    # Read the content of constants.py
    with open("constants.py", "r") as file:
        lines = file.readlines()

    # Modify the content as needed
    for i, line in enumerate(lines):
        if line.startswith("this_pc_ip"):
            lines[i] = f"this_pc_ip = '{this_pc_ip}'\n"
        elif line.startswith("GATEWAY_IP"):
            lines[i] = f"GATEWAY_IP = '{gateway_ip}'\n"
        elif line.startswith("ACTIVE_IPS"):
            lines[i] = f"ACTIVE_IPS = {active_ips}\n"
        elif line.startswith("broadcast_ip"):
            lines[i] = f"broadcast_ip = '{broadcast_ip}'\n"
        elif line.startswith("subnet_mask"):
            lines[i] = f"subnet_mask = '{subnet_mask}'\n"

    # Write the modified content back to the file
    with open("constants.py", "w") as file:
        file.writelines(lines)

def main():
    # Get values from network check functions
    this_pc_ip = get_this_pc_ip()
    gateway_ip = get_gateway_ip()
    subnet_mask = get_subnet_mask()
    subnet = ".".join(this_pc_ip.split(".")[:3])  # Use the first three parts of this PC's IP as subnet
    active_ips = get_active_ips(subnet)
    broadcast_ip = get_broadcast_ip(subnet)

    # Update constants.py with new values
    update_constants_file(this_pc_ip, gateway_ip, active_ips, broadcast_ip, subnet_mask)

if __name__ == '__main__':
    main()

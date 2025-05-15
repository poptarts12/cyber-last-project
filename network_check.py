import os
import re
import subprocess


# Change the current working directory to the directory of the script
os.chdir(os.path.dirname(__file__))

class ConstantsUpdater:
    def update_constants_file(self, this_pc_ip, broadcast_ip, subnet_mask, gateway_ip):
        constants_path = "constants.py"
        
        lines = [
            f"this_pc_ip = '{this_pc_ip}'\n",
            f"broadcast_ip = '{broadcast_ip}'\n",
            f"subnet_mask = '{subnet_mask}'\n",
            f"gateway_ip = '{gateway_ip}'\n"
        ]
        
        if os.path.exists(constants_path):
            with open(constants_path, "r") as file:
                existing_lines = file.readlines()
            
            updated_lines = []
            keys_found = {key: False for key in ["this_pc_ip", "broadcast_ip", "subnet_mask", "gateway_ip"]}
            
            for line in existing_lines:
                key = line.split(" = ")[0]
                if key in keys_found:
                    keys_found[key] = True
                    if key == "this_pc_ip":
                        updated_lines.append(lines[0])
                    elif key == "broadcast_ip":
                        updated_lines.append(lines[1])
                    elif key == "subnet_mask":
                        updated_lines.append(lines[2])
                    elif key == "gateway_ip":
                        updated_lines.append(lines[3])
                else:
                    updated_lines.append(line)
            
            for i, (key, found) in enumerate(keys_found.items()):
                if not found:
                    updated_lines.append(lines[i])
            
            with open(constants_path, "w") as file:
                file.writelines(updated_lines)
        else:
            with open(constants_path, "w") as file:
                file.writelines(lines)

class IPConfigParser:
    def __init__(self):
        self.ip_pattern = re.compile(r"IPv4 Address[^\:]*: (\d+\.\d+\.\d+\.\d+)")
        self.subnet_pattern = re.compile(r"Subnet Mask[^\:]*: (\d+\.\d+\.\d+\.\d+)")
        self.ipv4_pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
        self.gateway_pattern_ipv4 = re.compile(r"Default Gateway[^\:]*: (\d+\.\d+\.\d+\.\d+)")
        self.gateway_pattern = re.compile(r"Default Gateway[^\:]*: ((\d{1,3}\.){3}\d{1,3}|([a-fA-F0-9:]+))") #or ipv6 or ipv6
        self.constants_updater = ConstantsUpdater()

    def get_ipconfig_output(self):
        result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, encoding='latin-1')
        return result.stdout

    def parse_ipconfig(self, output):
        ip_address = None
        subnet_mask = None
        gateway_ip = None
        
        sections = output.split("\n\n")
        for section in sections:
            if "Default Gateway" in section:
                lines = section.splitlines()
                gateway_present = any(self.gateway_pattern.search(line) for line in lines)
                if gateway_present:
                    for i, line in enumerate(lines):
                        if not ip_address:
                            ip_match = self.ip_pattern.search(line)
                            if ip_match:
                                ip_address = ip_match.group(1)
                        
                        if not subnet_mask:
                            subnet_match = self.subnet_pattern.search(line)
                            if subnet_match:
                                subnet_mask = subnet_match.group(1)
                        
                        if "Default Gateway" in line:
                            gateway_match = self.gateway_pattern_ipv4.search(line)
                            if gateway_match:
                                gateway_ip = gateway_match.group(1)
                            elif i + 1 < len(lines):
                                # check if it is the line under that(somtimes the first is ipv6)
                                next_line = lines[i + 1].strip()
                                if self.ipv4_pattern.match(next_line):
                                    gateway_ip = next_line
                        
                        if ip_address and subnet_mask and gateway_ip:
                            break

        return ip_address, subnet_mask, gateway_ip

    def get_broadcast_ip(self, ip, subnet):
        ip_parts = list(map(int, ip.split('.')))
        subnet_parts = list(map(int, subnet.split('.')))
        
        broadcast_parts = [ip | (~subnet & 255) for ip, subnet in zip(ip_parts, subnet_parts)]
        broadcast_ip = '.'.join(map(str, broadcast_parts))
        return broadcast_ip

    def main(self):
        output = self.get_ipconfig_output()
        this_pc_ip, subnet_mask, gateway_ip = self.parse_ipconfig(output)
        if this_pc_ip and subnet_mask and gateway_ip:
            broadcast_ip = self.get_broadcast_ip(this_pc_ip, subnet_mask)
            self.constants_updater.update_constants_file(this_pc_ip, broadcast_ip, subnet_mask, gateway_ip)

def run():
    parser = IPConfigParser()
    parser.main()
run()
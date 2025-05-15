import hashlib
import os
import base64

os.chdir(os.path.dirname(__file__))

def hash_password(password):
    # Hash the password using SHA-1
    return hashlib.sha1(password.encode()).hexdigest()

def load_sites_from_file(filename):
    sites_list = []
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:  # Check if line is not empty
                        # Decode Base64-encoded data
                        decoded_site = base64.b64decode(line).decode('utf-8')
                        sites_list.append(decoded_site)
    except Exception as e:
        print(f"Error loading sites from file: {e}")
    return sites_list

def save_sites_to_file(filename, sites_dict):
    with open(filename, 'w') as f:
        for site in sites_dict:
            # Encode as Base64 before writing to file
            encoded_site = base64.b64encode(site.encode('utf-8')).decode('utf-8')
            f.write(encoded_site + '\n')


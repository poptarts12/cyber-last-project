import constants
import ipaddress
import threading
import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET
from network_manager import NetworkManager  # Import the NetworkManager class
from sites_manager import SitesManager
from utils import hash_password, load_sites_from_file, save_sites_to_file



class SettingsWindow:
    def __init__(self, username):
        self.username = username
        self.network_manager = NetworkManager()  # Initialize the NetworkManager

        self.blocked_sites_path = constants.blocked_sites_path
        self.whitelisted_sites_path = constants.whitelisted_sites_path

        self.blocked_sites = load_sites_from_file(constants.blocked_sites_path)
        self.whitelisted_sites = load_sites_from_file(constants.whitelisted_sites_path)

        self.settings_window = tk.Tk()  # Create a new Tk instance for the settings window
        self.settings_window.title(f"Settings - {username}")
        self.settings_window.geometry("500x600")
        self.settings_window.iconbitmap("Data\logo.ico")
        self.settings_window.resizable(False, False)  # Make the window non-resizable

        self.heading_font = ("Helvetica", 16, "bold")
        self.label_font = ("Helvetica", 12)
        self.button_font = ("Helvetica", 12, "bold")
        self.entry_font = ("Helvetica", 12)

        self.modes_frame = tk.Frame(self.settings_window, bg="lightblue")
        self.modes_frame.pack(pady=10)

        tk.Label(self.modes_frame, text="Choose Mode:", font=self.heading_font, bg="lightblue").pack()

        modes = ["No access to blacklisted sites", "Access to whitelisted sites only", "Network closure"]
        self.mode_var = tk.StringVar(value=modes[0])

        for mode in modes:
            tk.Radiobutton(self.modes_frame, text=mode, variable=self.mode_var, value=mode, font=self.label_font, bg="lightblue").pack(side="top", anchor="center")

        self.ip_frame = tk.Frame(self.settings_window, bg="lightblue")
        self.ip_frame.pack(pady=10, anchor="center")
        self.ip_label = tk.Label(self.ip_frame, text="Enter User IP (for customized restrictions)", font=self.label_font, underline=6, bg="lightblue")
        self.ip_entry = tk.Entry(self.ip_frame, width=30, font=self.entry_font)
        self.toggle_ip_entry()  # Call the function here to ensure it's present from the start

        self.personalization_frame = tk.Frame(self.settings_window, bg="lightblue")
        self.personalization_frame.pack(pady=10, anchor="center")

        tk.Label(self.personalization_frame, text="Personalize Settings:", font=self.heading_font, bg="lightblue").pack(anchor="center")

        tk.Button(self.personalization_frame, text="Manage Blocked Sites", command=lambda: SitesManager(self.blocked_sites_path, self.blocked_sites, "Manage Blocked Sites"), font=self.button_font, bg="lightgrey").pack(anchor="center", pady=5)
        tk.Button(self.personalization_frame, text="Manage Whitelisted Sites", command=lambda: SitesManager(self.whitelisted_sites_path, self.whitelisted_sites, "Manage Whitelisted Sites"), font=self.button_font, bg="lightgrey").pack(anchor="center", pady=5)

        tk.Button(self.personalization_frame, text="Change Username", command=self.change_username, font=self.button_font, bg="lightgrey").pack(anchor="center", pady=5)
        tk.Button(self.personalization_frame, text="Change Password", command=self.change_password, font=self.button_font, bg="lightgrey").pack(anchor="center", pady=5)

        self.app_status_var = tk.StringVar(value="On")

        def toggle_app_status():
            current_status = self.app_status_var.get()
            self.app_status_var.set("Off" if current_status == "On" else "On")

        self.app_status_frame = tk.Frame(self.settings_window, bg="lightblue")
        self.app_status_frame.pack(pady=10)

        tk.Label(self.app_status_frame, text="Application Status:", font=self.heading_font, bg="lightblue").pack(anchor="center", pady=5)
        app_status_button = tk.Button(self.app_status_frame, textvariable=self.app_status_var, command=toggle_app_status, font=self.button_font, bg="lightgrey")
        app_status_button.pack(anchor="center", pady=5)

        self.save_button = tk.Button(self.settings_window, text="Save Settings", command=self.save_settings_threaded, font=self.button_font, bg="lightgreen")
        self.save_button.pack(pady=10)

        self.settings_window.mainloop()

    def toggle_ip_entry(self):
        self.ip_label.pack()
        self.ip_entry.pack()

    def save_settings_threaded(self):
        # Disable the save button while saving settings
        self.save_button.config(state="disabled")

        # Run the save_settings function in a separate thread
        threading.Thread(target=self.save_settings).start()

    def save_settings(self):
        selected_mode = self.mode_var.get()
        app_status = self.app_status_var.get()

        # Save the site lists
        save_sites_to_file(self.blocked_sites_path, self.blocked_sites)
        save_sites_to_file(self.whitelisted_sites_path, self.whitelisted_sites)

        user_ip = self.ip_entry.get()

        if not self.ip_in_subnet(user_ip, constants.this_pc_ip, constants.subnet_mask) and user_ip != "":
            messagebox.showinfo("user ip cofiguration", "this ip can't be in the network")
            app_status = "Off"

        self.network_manager.activate_mode(selected_mode, app_status,user_ip)

        # Enable the save button after saving settings
        self.save_button.config(state="normal")

        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
    
    def ip_in_subnet(self, user_ip: str, network_ip: str, subnet_mask: str) -> bool:
        try:
            # Convert IP addresses and subnet mask to IPv4Address objects
            ip = ipaddress.IPv4Address(user_ip)
            network_ip = ipaddress.IPv4Address(network_ip)
            netmask = ipaddress.IPv4Address(subnet_mask)
            
            # Calculate network addresses
            ip_network_address = int(ip) & int(netmask)
            subnet_network_address = int(network_ip) & int(netmask)
            
            # Check if both network addresses are the same
            return ip_network_address == subnet_network_address
        except ValueError:
            # The IP address or subnet mask is not valid
            return False
        
    def change_username(self):
        change_window = tk.Toplevel()
        change_window.title("Change Username")
        change_window.geometry("300x150")
        change_window.resizable(False, False)

        tk.Label(change_window, text="New Username:").pack(pady=5)
        new_username_entry = tk.Entry(change_window, width=30)
        new_username_entry.pack(pady=5)

        def save_new_username():
            new_username = new_username_entry.get()

            if not new_username:
                messagebox.showerror("Error", "Username cannot be empty")
                return

            try:
                tree = ET.parse(r'Data/credentials.xml')
                root = tree.getroot()

                for user in root.findall('user'):
                    xml_username = user.find('username').text
                    if xml_username == self.username:
                        user.find('username').text = new_username

                tree.write(r'Data/credentials.xml')
                self.settings_window.title(f"Settings - {new_username}")
                messagebox.showinfo("Success", "Username changed successfully!")
                change_window.destroy()
            except ET.ParseError:
                messagebox.showerror("Error", "Error parsing XML file")
            except FileNotFoundError:
                messagebox.showerror("Error", "credentials.xml file not found")
        tk.Button(change_window, text="Save", command=save_new_username).pack(pady=5)

    def change_password(self):
        change_window = tk.Toplevel()
        change_window.title("Change Password")
        change_window.geometry("300x150")
        change_window.resizable(False, False)

        tk.Label(change_window, text="New Password:").pack(pady=5)
        new_password_entry = tk.Entry(change_window, width=30, show="*")
        new_password_entry.pack(pady=5)

        def save_new_password():
            new_password = new_password_entry.get()

            if not new_password:
                messagebox.showerror("Error", "Password cannot be empty")
                return

            try:
                tree = ET.parse(r'Data/credentials.xml')
                root = tree.getroot()

                hashed_password = hash_password(new_password)
                for user in root.findall('user'):
                    xml_username = user.find('username').text
                    if xml_username == self.username:
                        user.find('password').text = hashed_password

                tree.write(r'Data/credentials.xml')
                messagebox.showinfo("Success", "Password changed successfully!")
                change_window.destroy()
            except ET.ParseError:
                messagebox.showerror("Error", "Error parsing XML file")
            except FileNotFoundError:
                messagebox.showerror("Error", "credentials.xml file not found")


        tk.Button(change_window, text="Save", command=save_new_password).pack(pady=5)

if __name__ == "__main__":
    SettingsWindow("TestUser")

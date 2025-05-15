import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET
from settings import SettingsWindow
from utils import hash_password


class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")

        # Set the fixed window size
        window_width = 300
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.root.resizable(False, False)

        self.root.iconbitmap("Data\logo.ico")

        # Create a frame to hold the widgets
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        # Create labels and entry widgets for username and password
        self.username_label = tk.Label(self.frame, text="Username:")
        self.username_label.grid(row=0, column=0, pady=5)

        self.username_entry = tk.Entry(self.frame, width=20)
        self.username_entry.grid(row=0, column=1, pady=5)

        self.password_label = tk.Label(self.frame, text="Password:")
        self.password_label.grid(row=1, column=0, pady=5)

        self.password_entry = tk.Entry(self.frame, show="*", width=20)
        self.password_entry.grid(row=1, column=1, pady=5)

        # Create a login button
        self.login_button = tk.Button(self.frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=10)

        # Bind the Enter key to the login function
        self.root.bind('<Return>', self.login)

        # Run the application
        self.root.mainloop()

    def check_credentials(self, username, password):
        try:
            # Parse the XML file
            tree = ET.parse(r'Data/credentials.xml')
            root = tree.getroot()

            # Iterate through each user in the XML file
            for user in root.findall('user'):
                xml_username = user.find('username').text
                xml_password = user.find('password').text

                # Check if the provided username and hashed password match
                if xml_username == username and xml_password == hash_password(password):
                    return True
        except ET.ParseError:
            messagebox.showerror("Error", "Error parsing XML file")
        except FileNotFoundError:
            messagebox.showerror("Error", "credentials.xml file not found")

        return False

    def login(self, event=None):
        # Get the username and password entered by the user
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password are correct
        if self.check_credentials(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.root.destroy()  # Close the login window
            SettingsWindow(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

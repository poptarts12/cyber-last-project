import tkinter as tk
from tkinter import simpledialog
import utils

class SitesManager:

    def __init__(self, file_path, sites_list, title):
        self.file_path = file_path
        self.sites_list = sites_list

        self.sites_window = tk.Toplevel()
        self.sites_window.title(title)
        self.sites_window.geometry("500x400")
        self.sites_window.resizable(False, False)  # Make the window non-resizable

        self.sites_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.listbox = tk.Listbox(self.sites_window, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        for site in self.sites_list:
            self.listbox.insert(tk.END, site)

        button_frame = tk.Frame(self.sites_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Add", command=self.add_site).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit", command=self.edit_site).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_site).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save", command=self.save_sites).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.on_closing).pack(side=tk.LEFT, padx=5)

        self.sites_window.bind('<Control-s>', self.save_sites)  # Bind Ctrl+S to save_sites function

    def add_site(self):
        site = simpledialog.askstring("Add Site", "Enter the site:")
        if site:
            self.sites_list.append(site)
            self.listbox.insert(tk.END, site)

    def edit_site(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            old_site = self.listbox.get(selected_index)
            new_site = simpledialog.askstring("Edit Site", "Edit the site:", initialvalue=old_site)
            if new_site:
                self.sites_list[selected_index[0]] = new_site
                self.listbox.delete(selected_index)
                self.listbox.insert(selected_index, new_site)

    def delete_site(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.sites_list.pop(selected_index[0])
            self.listbox.delete(selected_index)

    def save_sites(self):
        utils.save_sites_to_file(self.file_path, self.sites_list)

    def on_closing(self):
        self.save_sites()
        self.sites_window.destroy()

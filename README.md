# Web Blocker

Web Blocker is a Python-based desktop application for **network website filtering and access control**.
It allows network administrators to block unauthorized websites or only allow access to a predefined list of safe websites.
The application is designed to provide fine-grained network control through a user-friendly graphical interface.

## Features

* **Three operating modes:**

  * **No access to blacklisted sites** – Block access to sites in a custom blacklist.
  * **Access to whitelisted sites only** – Allow access only to approved sites (whitelist).
  * **Network closure** – Block all external network access.
* **User-based restrictions:**

  * Apply restrictions to specific user IP addresses.
* **Dynamic site management:**

  * Edit blocked and whitelisted sites directly from the UI.
* **User management:**

  * Change username and password from the application.
* **Network-layer filtering:**

  * Uses ARP/DNS spoofing for effective control.
* **Simple application status toggle** (On/Off).

## Screenshots

> *(Example UI: Settings window)*

![Web Blocker Settings](relative/path/to/your/screenshot.png)

<!-- Replace the path with your uploaded image, e.g. "images/settings.png" -->

## Getting Started

### Prerequisites

* Python 3.10 or newer (recommended 3.11+)
* `pip` (Python package manager)
* Windows OS (for best compatibility, due to the use of tkinter and some network features)
* **Two computers on the same LAN**
  OR
  **A dedicated DNS server machine (not your home router!)**
  (see Environment Planning below)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/poptarts12/cyber-last-project.git
   cd cyber-last-project
   ```

2. **Install required Python packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure your network settings:**

   * Edit the `constants.py` file and update:

     * `this_pc_ip` – The IP address of the computer running the app.
     * `broadcast_ip`, `subnet_mask`, `gateway_ip`, `dns_server_ip` – According to your local network.
   * Make sure your firewall and antivirus do not block ARP/DNS spoofing or Flask server ports.

4. **Run the application:**

   ```sh
   python app.py
   ```

## Environment & Deployment Planning

This application is designed to **intercept and filter network traffic on a LAN**.
To achieve effective filtering, **you must deploy it in one of the following ways:**

### Option 1: Two Machines (Admin + Client)

* **Machine 1:** Runs Web Blocker (acts as DNS/ARP/DNS interceptor).
* **Machine 2:** The client/user machine(s) whose access you wish to restrict.

**Requirements:**

* Both machines must be on the **same local network/subnet**.
* Set the DNS server on Machine 2 to the IP address of Machine 1.

### Option 2: Dedicated DNS Server

* Run the application on a dedicated server (not your home router).
* Set the DNS configuration of all target machines to use this server as their DNS.
* Do **NOT** install on a home router!
  (Routers generally don’t support this level of Python integration.)

### Notes & Best Practices

* **Do not run as administrator/root unless required.**
* This tool is for educational and authorized network administration use only.
* ARP and DNS spoofing techniques may trigger network security alerts.
* Use on networks where you have permission to test and filter traffic.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.



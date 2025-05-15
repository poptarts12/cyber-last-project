from login import LoginWindow
import network_check
import os

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    network_check.run()
    app = LoginWindow()


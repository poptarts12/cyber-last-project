import importlib
import constants


def main():
    # Change the value of the variable within the constants module
    new_gateway_ip = "22222"
    constants.GATEWAY_IP = new_gateway_ip

    # Write the updated value to the module file
    with open("constants.py", "r") as file:
        lines = file.readlines()

    with open("constants.py", "w") as file:
        for line in lines:
            if line.startswith("GATEWAY_IP"):
                line = f"GATEWAY_IP = '{new_gateway_ip}'\n"
            file.write(line)


    # Now the changes made to the constants module will be reflected
    print(constants.GATEWAY_IP)


if __name__ == '__main__':
    main()


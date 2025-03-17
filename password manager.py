import sys
import os
import re
from cryptography.fernet import Fernet

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python password_manager.py <file_path> <key_path>")
    sys.exit(1)  # Exit with status code 1 (error)

file_path = sys.argv[1]
key_path = sys.argv[2]
accounts_info = []

try:
    if os.path.exists(key_path):
        with open(key_path, "r") as key_file:
            key = key_file.read().strip()  # Read the key and remove any extra whitespace
            if not key:  # Check if the key file is empty
                sys.exit("Error: Key file is empty.")
            key = key.encode()  # Convert the key from string to bytes
    else:
        create_key = input("Key not found. Would you like to create one? (Y/N): ").upper()
        if create_key == "Y":
            key = Fernet.generate_key()  # Generate a new key (in bytes)
            with open(key_path, "w") as key_file:
                key_file.write(key.decode())  # Decode the key to a string before writing
            print(f"New key generated and saved to {key_path}.")
        else:
            sys.exit("Exiting...")

except Exception as e:
    sys.exit(f"Error loading or generating key: {e}")

fernet = Fernet(key)  # Create the Fernet object using the key

try:
    file_path = sys.argv[1]
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith("Acc"):
                    # Initialize a dictionary to store the current account
                    account = {}
                elif line.startswith("- Account name:"):
                    account["Account name"] = line.split(":")[1].strip()
                elif line.startswith("- Username:"):
                    account["Username"] = line.split(":")[1].strip()
                elif line.startswith("- Password:"):
                    account["Password"] = line.split(":")[1].strip()
                    # Add the account to the list
                    accounts_info.append(account)
    else:
        create_file = input("File not found. Would you like to create one? (Y/N): ").upper()
        if create_file == "Y":
            with open(file_path, "w"):
                print("File created.")
        else:
            sys.exit("Exiting...")
except Exception as e:
    print(f"Error: {e}")
    sys.exit("File not found.")

while True:
    try:
        option = int(input("""
                Choose an option from the list below:
                    1. Add Password
                    2. Delete Password
                    3. Retrieve Password
                    4. View All Accounts
                    5. Exit
                """))
    
        match option:
            case 1:
                while True:
                    account_name = input("Enter a name for the account: ")
                    accname = re.findall(r"(\w{1,})", account_name)
                    if not accname:
                        print("account name cannot be empty.")
                        continue
                    break
                while True:
                    username = input("Enter a username: ")
                    uname = re.findall(r"(\w{6,})", username)
                    if not uname:
                        print("username cannot be empty or contains less than 6 characters.")
                        continue
                    break
                while True:
                    password = input("Enter a password: ")
                    if not password or len(password) < 8:
                        print("password cannot be empty or contains less than 8 characters.")
                        continue
                    break
                # Encode the password into bytes
                password_bytes = password.encode()
                # Encrypt the password using the Fernet object
                encrypted = fernet.encrypt(password_bytes)
                # Decode the encrypted password into a string for storage
                encrypted_str = encrypted.decode()
                accounts_info.append({"Account name":account_name, "Username":username, "Password":encrypted_str})
            
            case 2:
                account_name = input("Enter the name of the account to be deleted: ")
                for account in accounts_info:
                    if account_name in account.values():
                        accounts_info.remove(account)
                        break
                else:
                    print("Account name not found.")

            case 3:
                account_name = input("Enter an account name: ")
                for account in accounts_info:
                    if account_name in account.values():
                         # Encode the encrypted password into bytes
                        encoded = account["Password"].encode()
                        # Decrypt the password using the Fernet object
                        decrypted = fernet.decrypt(encoded)
                        # Decode the decrypted password into a string
                        decrypted_str = decrypted.decode()
                        print(f"The password linked to this account is: {decrypted_str}")
            
            case 4:
                for i, account in enumerate(accounts_info):
                    print(f"Acc {i+1}")
                    print(f"- Account name: {account['Account name']}")
                    print(f"- Username: {account['Username']}")
                    print(f"- Password: {account['Password']}")
            
            case 5:
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        for i, item in enumerate(accounts_info):
                            file.write(f"Acc {i+1}" + "\n")
                            file.write(f"- Account name:{item['Account name']}" + "\n")
                            file.write(f"- Username:{item['Username']}" + "\n")
                            file.write(f"- Password:{item['Password']}" + "\n")
                    print("Data saved successfully. Exiting...")
                    sys.exit(0)  # Exit with status code 0 (success)
                except Exception as e:
                    print(f"Error saving data: {e}")
                    sys.exit(1)  # Exit with status code 1 (error)

            case _:
                print("Invalid input. Choose an option from the list.")
                continue

    except ValueError:
        print("Invalid input. Please enter a number.")
        continue
    except Exception as e:
        print(f"An error occurred: {e}")
        continue
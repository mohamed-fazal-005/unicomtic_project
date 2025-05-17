import datetime

def does_user_exist(username):
    try:
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.split("|")
                if len(parts) >= 2 and parts[0] == username:
                    return True
    except FileNotFoundError:
        pass
    return False

def get_next_account_number():
    try:
        with open("accounts.txt", "r") as file:
            accounts = [line for line in file if line.startswith("ACCOUNT:")]
            if not accounts:
                return 1001
            last = accounts[-1]
            last_num = int(last.split(":")[1].split("|")[0])
            return last_num + 1
    except FileNotFoundError:
        return 1001

def get_account_data(username):
    try:
        with open("accounts.txt", "r") as file:
            account_data = {}
            lines = file.readlines()
            for i in range(len(lines)):
                line = lines[i]
                if line.startswith("ACCOUNT:") and f"|{username}|" in line:
                    account_details = line.split("|")
                    account_number = account_details[0].split(":")[1]
                    balance = float(account_details[3])
                    account_data['account_number'] = account_number
                    account_data['balance'] = balance
                    account_data['transactions'] = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith("TRANSACTION:"):
                        account_data['transactions'].append(lines[j])
                        j += 1
                    return account_data
    except FileNotFoundError:
        pass
    return None

def update_account_data(account_data, username):
    try:
        with open("accounts.txt", "r") as file:
            lines = file.readlines()

        updated_lines = []
        i = 0
        found = False

        while i < len(lines):
            if lines[i].startswith("ACCOUNT:") and f"|{username}|" in lines[i]:
                found = True
                # Replace account line
                updated_lines.append(f"ACCOUNT:{account_data['account_number']}|{username}|{account_data['balance']}\n")
                # Replace transaction lines
                for txn in account_data['transactions']:
                    updated_lines.append(f"{txn.strip()}\n")
                # Skip old transaction lines
                i += 1
                while i < len(lines) and lines[i].startswith("TRANSACTION:"):
                    i += 1
                # Skip any blank line after transaction
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
                updated_lines.append("\n")  # Add new separator
            else:
                updated_lines.append(lines[i])
                i += 1

        if not found:
            updated_lines.append("=========================================================\n")
            updated_lines.append(f"ACCOUNT:{account_data['account_number']}|{username}|{account_data['balance']}\n")
            for txn in account_data['transactions']:
                updated_lines.append(f"{txn.strip()}\n")
            updated_lines.append("\n")

        with open("accounts.txt", "w") as file:
            file.writelines(updated_lines)

    except FileNotFoundError:
        print("Accounts file not found.")

def create_user_account():
    username = input("Enter new username: ")
    if does_user_exist(username):
        print("User already exists.")
        return

    password = input("Enter password: ")
    with open("users.txt", "a") as file:
        file.write("========================\n")
        file.write(f"{username}|{password}\n")
    print(f"User {username} created successfully.")

    try:
        initial_balance = float(input("Enter initial balance: "))
        if initial_balance < 0:
            print("Initial balance cannot be negative.")
            return
    except ValueError:
        print("Invalid balance.")
        return

    account_number = get_next_account_number()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("accounts.txt", "a") as file:
        file.write("=========================================================\n")
        file.write(f"ACCOUNT:{account_number}|{username}||{initial_balance}\n")
        file.write(f"TRANSACTION:[{now}] Initial deposit: {initial_balance}\n")
        file.write("\n")

    print(f"Account created for {username} with account number {account_number} and initial balance {initial_balance}.")

def users_deta():
    print("\nRegistered Users:")
    try:
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.split("|")
                if len(parts) >= 1:
                    print(f"{parts[0]}")
    except FileNotFoundError:
        print("No users found.")

def view_all_accounts():
    print("\n-------All Accounts-----------")
    
    try:
        with open("accounts.txt", "r") as file:
            
            print(file.read())

    except FileNotFoundError:
        print("No accounts found.")



def deposit(username):
    try:
        amount = float(input("Enter amount to deposit: "))
        if amount <= 0:
            print("Deposit amount must be greater than zero.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    account_data = get_account_data(username)
    if account_data:
        account_data['balance'] += amount
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        account_data['transactions'].append(f"TRANSACTION:[{now}] Deposited: {amount}")
        update_account_data(account_data, username)
        print(f"Deposited {amount}. New balance: {account_data['balance']}")
    else:
        print("Account not found.")

def withdraw(username):
    try:
        amount = float(input("Enter amount to withdraw: "))
        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    account_data = get_account_data(username)
    if account_data:
        if account_data['balance'] >= amount:
            account_data['balance'] -= amount
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            account_data['transactions'].append(f"TRANSACTION:[{now}] Withdrawn: {amount}")
            update_account_data(account_data, username)
            print(f"Withdrawn {amount}. New balance: {account_data['balance']}")
        else:
            print("Insufficient funds.")
    else:
        print("Account not found.")

def check_balance(username):
    account_data = get_account_data(username)
    if account_data:
        print(f"Your balance is: {account_data['balance']}")
    else:
        print("Account not found.")

def transfer_funds(username):
    recipient = input("Enter recipient's username: ").strip()
    try:
        amount = float(input("Enter amount to transfer: "))
        if amount <= 0:
            print("Transfer amount must be greater than zero.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    sender_account = get_account_data(username)
    recipient_account = get_account_data(recipient)

    if sender_account and recipient_account:
        if sender_account['balance'] >= amount:
            sender_account['balance'] -= amount
            recipient_account['balance'] += amount
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sender_account['transactions'].append(f"TRANSACTION:[{now}] Transferred to {recipient}: {amount}")
            recipient_account['transactions'].append(f"TRANSACTION:[{now}] Received from {username}: {amount}")
            update_account_data(sender_account, username)
            update_account_data(recipient_account, recipient)
            print(f"Transferred {amount} to {recipient}. New balance: {sender_account['balance']}")
        else:
            print("Insufficient funds.")
    else:
        print("Sender or recipient account not found.")

def view_transactions(username):
    account_data = get_account_data(username)
    if account_data:
        print("\n--- Transaction History ---")
        for txn in account_data['transactions']:
            print(txn)
    else:
        print("Account not found.")

def login():
    print("\n==========login==========")
    admin_username = 'admin'
    admin_password = 'admin123'

    username = input("Username: ")
    password = input("Password: ")

    if username == admin_username and password == admin_password:
        admin_menu()
        return None
        

    try:
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    u, p = parts[0], parts[1]
                    if u == username and p == password:
                        return username
    except FileNotFoundError:
        print("User database not found.")
        return None
    print("Invalid username or password.")
    return None
                        


def admin_menu():
    while True:
        print("\n wellcom admin ")
        print("\n=========Admin Menu===========")
        print("1. Create User Account")
        print("2. View All Accounts")
        print("3. View Registered Users")
        print("4. Logout")
        print("===============================")
        choice = input("Enter choice: ")
        if choice == "1":
            create_user_account()
        elif choice == "2":
            view_all_accounts()
        elif choice == "3":
            users_deta()
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid option.")

def user_menu(username):
    while True:
        print("\n=========user menu===========")
        print(f"\nWelcome, {username}")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. Transfer Funds")
        print("5. View Transaction History")
        print("6. Logout")
        print("===============================")
        choice = input("Enter choice: ")

        if choice == "1":
            deposit(username)
        elif choice == "2":
            withdraw(username)
        elif choice == "3":
            check_balance(username)
        elif choice == "4":
            transfer_funds(username)
        elif choice == "5":
            view_transactions(username)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid option.")

def main():
    while True:
        print("\n--- Welcome to Our Banking System ---")
        print("===============================")
        print("1. Login")
        print("2. Exit")
        print("===============================")
        choice = input("Enter choice: ")
        if choice == "1":
            username = login()
            if username:
                user_menu(username)
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "_main_":
    main()


main()

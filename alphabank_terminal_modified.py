import socket
import threading
import json
import hashlib
import os
import random

# Constants for server configuration and data file
HOST = '0.0.0.0'
PORT = 6201
DATA_FILE = 'alpha_bank_data.json'
ROLE = ['null', 'USER', 'TELLER', 'ADMIN']
logged_in_user = None

# Role definitions for different user types
#class Role:
#    USER = 'USER'
#    TELLER = 'TELLER'
#    ADMIN = 'ADMIN'
    
# Replacing Roles with permission levels: 1(User), 2(Teller), 3(Admin)
class Role:
    USER = 1
    TELLER = 2
    ADMIN = 3

# User class to manage user details and roles

class User:
    def __init__(self, username, password_hash, role=Role.USER, balance=0):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.balance = balance
        self.is_logged_in = False

    def __str__(self):
        return f"{self.username} ({self.role})"

# Bank system to manage users, roles, and transactions
class AlphaBank:
    def __init__(self):
        self.users = {}
        self.transactions = {}
        self.load_data()
        if "admin" not in self.users:
            # Add a default admin if not present
            self.users["admin"] = User("admin", self.hash_password("Spookytus"), Role.ADMIN)
            self.save_data()

    def load_data(self):
        # Load user data from JSON file if it exists
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                for username, details in data["users"].items():
                    self.users[username] = User(
                        username=username,
                        password_hash=details["password_hash"],
                        role=details["role"],
                        balance=details["balance"]
                    )
                self.transactions = data.get("transactions", {})

    def save_data(self):
        # Save user data to JSON file
        data = {
            "users": {
                username: {
                    "password_hash": user.password_hash,
                    "role": user.role,
                    "balance": user.balance
                } for username, user in self.users.items()
            },
            "transactions": self.transactions
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
        

    def hash_password(self, password):
        # Hash the password using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        # Login a user by verifying the password hash
        user = self.users.get(username)
        if user and user.password_hash == self.hash_password(password):
            user.is_logged_in = True
            role_name = ROLE[user.role]
            return f"SUCCESS: {username} logged in as {role_name}"
        return "FAIL: Incorrect username or password"
    
    def logout(self, username):
        # Logout a user
        user = self.users.get(username)
        if user and user.is_logged_in:
            user.is_logged_in = False
            return f"SUCCESS: {username} logged out"
        return "FAIL: User not logged in or not found"
    
    def enroll(self, username, password, role_name):
        # Create a new user with the specified role
        print(f"Attempting to create user: {username}, Role: {role_name}")
        if username in self.users:
            print("Username already exists")
            return "FAIL: Username already exists"
        role = ROLE.index(role_name) if role_name in ROLE else None
        if role is None:
            print("Invalid role")
            return "FAIL: Invalid role"
        self.users[username] = User(username=username, password_hash=self.hash_password(password), role=role)
        self.save_data()
        print(f"User {username} created successfully")
        return f"SUCCESS: {username} created as {role_name}"

    def deposit(self, teller, username, amount):
        # Deposit money into a user's account (only tellers can do this)
        user = self.users.get(username)
        if teller.role >= Role.TELLER and user:
            user.balance += amount
            self.save_data()
            return f"SUCCESS: Deposited ${amount} to {username}"
        return "FAIL: Unauthorized or user not found"

    def withdraw(self, teller, username, amount):
        # Withdraw money from a user's account (only tellers can do this)
        user = self.users.get(username)
        if teller.role >= Role.TELLER and user and user.balance >= amount:
            user.balance -= amount
            self.save_data()
            return f"SUCCESS: Withdrawn ${amount} from {username}"
        return "FAIL: Unauthorized, insufficient funds, or user not found"

    def send(self, sender, target_username, amount):
        # Send money from one user to another
        target = self.users.get(target_username)
        if sender.balance >= amount and target:
            tx_id = str(random.randint(1000, 9999))
            self.transactions[tx_id] = {
                "from": sender.username,
                "to": target_username,
                "amount": amount,
                "status": "PENDING",
                "initiator": sender.username
            }
            self.save_data()
            return f"SUCCESS: Created send transaction with TXID {tx_id}"
        return "FAIL: Insufficient funds or user not found"

    def request(self, requester, target_username, amount):
        # Request money from another user
        target = self.users.get(target_username)
        if target:
            tx_id = str(random.randint(1000, 9999))
            self.transactions[tx_id] = {
                "from": target_username,
                "to": requester.username,
                "amount": amount,
                "status": "PENDING",
                "initiator": requester.username
            }
            self.save_data()
            return f"SUCCESS: Created request transaction with TXID {tx_id}"
        return "FAIL: User not found"

    def approve(self, user, tx_id):
        # Approve a pending transaction
        transaction = self.transactions.get(tx_id)
        if transaction and transaction["status"] == "PENDING":
            if transaction["to"] == user.username and transaction["initiator"] != user.username:
                sender = self.users[transaction["from"]]
                if sender.balance >= transaction["amount"]:
                    sender.balance -= transaction["amount"]
                    user.balance += transaction["amount"]
                    transaction["status"] = "APPROVED"
                    self.save_data()
                    return f"SUCCESS: Transaction {tx_id} approved"
            elif transaction["from"] == user.username and transaction["initiator"] != user.username:
                sender = self.users[transaction["from"]]
                if sender.balance >= transaction["amount"]:
                    sender.balance -= transaction["amount"]
                    user.balance += transaction["amount"]
                    transaction["status"] = "APPROVED"
                    self.save_data()
                    return f"SUCCESS: Transaction {tx_id} approved"
            elif transaction["initiator"] == user.username:
                return "FAIL: Cannot approve your own request"
        return "FAIL: Transaction not found, unauthorized, or insufficient funds"

    def promote(self, admin, username):
        # Promote a user to a higher role (only admins can do this)
        user = self.users.get(username)
        if admin.role == Role.ADMIN and user:
            if user.role == Role.USER:
                user.role = Role.TELLER
            elif user.role == Role.TELLER:
                user.role = Role.ADMIN
            self.save_data()
            return f"SUCCESS: {username} promoted to {ROLE[user.role]}"
        return "FAIL: Unauthorized or user not found"

    def demote(self, admin, username):
        # Demote a user to a lower role (only admins can do this)
        user = self.users.get(username)
        if admin.role == Role.ADMIN and user:
            if user.role == Role.ADMIN:
                user.role = Role.TELLER
            elif user.role == Role.TELLER:
                user.role = Role.USER
            self.save_data()
            return f"SUCCESS: {username} demoted to {ROLE[user.role]}"
        return "FAIL: Unauthorized or user not found"

    def balance(self, user):
        # Return the balance of the currently logged-in user
        if user:
            return f"SUCCESS: {user.username}'s balance is ${user.balance}"
        return "FAIL: User not logged in"

# Dictionary to track logged-in users by connection address
logged_in_users = {}

# Command handler to process client commands
def handle_commands(bank, conn, addr):
    def get_prompt():
        user = logged_in_users.get(addr)
        if user:
            role_name = ROLE[user.role]
            return f"AlphaBank({user.username}:{role_name})> "
        return "AlphaBank> "

    conn.sendall(get_prompt().encode())

    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        command = data.split()
        response = ""
        user = logged_in_users.get(addr)

        # Handle each command based on logged-in user's role and command input
        if command[0].lower() == "login" and len(command) == 3:
            if any(u.username == command[1] and u.is_logged_in for u in logged_in_users.values()):
                response = "FAIL: User already logged in"
            else:
                response = bank.login(command[1], command[2])
                if "SUCCESS" in response:
                    logged_in_users[addr] = bank.users[command[1]]

        elif command[0].lower() == "logout" and user:
            response = bank.logout(user.username)
            if "SUCCESS" in response:
                del logged_in_users[addr]

        elif command[0].lower() == "enroll" and len(command) == 4 and user:
            response = bank.enroll(command[1], command[2], command[3].upper())

        elif command[0].lower() == "deposit" and len(command) == 3 and user:
            response = bank.deposit(user, command[1], int(command[2]))

        elif command[0].lower() == "withdraw" and len(command) == 3 and user:
            response = bank.withdraw(user, command[1], int(command[2]))

        elif command[0].lower() == "send" and len(command) == 3 and user:
            response = bank.send(user, command[1], int(command[2]))

        elif command[0].lower() == "request" and len(command) == 3 and user:
            response = bank.request(user, command[1], int(command[2]))

        elif command[0].lower() == "approve" and len(command) == 2 and user:
            response = bank.approve(user, command[1])

        elif command[0].lower() == "balance" and user:
            response = bank.balance(user)

        elif command[0].lower() == "promote" and len(command) == 2 and user:
            response = bank.promote(user, command[1])

        elif command[0].lower() == "demote" and len(command) == 2 and user:
            response = bank.demote(user, command[1])

        else:
            response = "FAIL: Invalid command or insufficient permissions"
        
        conn.sendall(f"{response}\n{get_prompt()}".encode())

# Start the server to listen for client connections
def start_server():
    bank = AlphaBank()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"AlphaBank server running on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=handle_commands, args=(bank, conn, addr)).start()

# Entry point to start the server
if __name__ == "__main__":
    start_server()

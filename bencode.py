import socket
import threading
import json
import hashlib
import os
import random

# Constants for server configuration and data file
HOST = '127.0.0.1'
PORT = 6201
DATA_FILE = 'alpha_bank_data.json'

# Role definitions for different user types
class Role:
    USER = 'USER'
    TELLER = 'TELLER'
    ADMIN = 'ADMIN'

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
            return f"SUCCESS: {username} logged in as {user.role}"
        return "FAIL: Incorrect username or password"

    def create_user(self, username, password, role):
        # Create a new user with the specified role
        if username in self.users:
            return "FAIL: Username already exists"
        self.users[username] = User(username=username, password_hash=self.hash_password(password), role=role)
        self.save_data()
        return f"SUCCESS: {username} created as {role}"

    def deposit(self, teller, username, amount):
        # Deposit money into a user's account (only tellers can do this)
        user = self.users.get(username)
        if teller.role == Role.TELLER and user:
            user.balance += amount
            self.save_data()
            return f"SUCCESS: Deposited ${amount} to {username}"
        return "FAIL: Unauthorized or user not found"

    def withdraw(self, teller, username, amount):
        # Withdraw money from a user's account (only tellers can do this)
        user = self.users.get(username)
        if teller.role == Role.TELLER and user and user.balance >= amount:
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
                "status": "PENDING"
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
                "status": "PENDING"
            }
            self.save_data()
            return f"SUCCESS: Created request transaction with TXID {tx_id}"
        return "FAIL: User not found"

    def approve(self, user, tx_id):
        # Approve a pending transaction
        transaction = self.transactions.get(tx_id)
        if transaction and transaction["status"] == "PENDING" and transaction["to"] == user.username:
            sender = self.users[transaction["from"]]
            if sender.balance >= transaction["amount"]:
                sender.balance -= transaction["amount"]
                user.balance += transaction["amount"]
                transaction["status"] = "APPROVED"
                self.save_data()
                return f"SUCCESS: Transaction {tx_id} approved"
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
            return f"SUCCESS: {username} promoted to {user.role}"
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
            return f"SUCCESS: {username} demoted to {user.role}"
        return "FAIL: Unauthorized or user not found"

# Command handler to process client commands
def handle_commands(bank, conn, addr):
    conn.sendall(b"AlphaBank> ")
    logged_in_user = None

    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        command = data.split()
        response = ""

        # Handle each command based on logged-in user's role and command input
        if command[0].lower() == "login" and len(command) == 3:
            response = bank.login(command[1], command[2])

        elif command[0].lower() == "deposit" and len(command) == 3 and logged_in_user and logged_in_user.role == Role.TELLER:
            response = bank.deposit(logged_in_user, command[1], int(command[2]))

        # Add additional command checks and responses here...
        
        conn.sendall(f"{response}\nAlphaBank> ".encode())

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

# Define the User class
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = 0
        self.role = 'user'
        self.pending_transactions = []

    # Method to login the user
    def login(self, password):
        if self.password == password:
            return "SUCCESS"
        return "FAIL"

    # Method to send money to another user
    def send(self, recipient, amount):
        if self.balance >= amount:
            txid = f"TX{len(self.pending_transactions) + 1}"
            recipient.pending_transactions.append({'txid': txid, 'from': self.username, 'amount': amount})
            return txid
        return "FAIL"

    # Method to request money from another user
    def request(self, sender, amount):
        txid = f"TX{len(self.pending_transactions) + 1}"
        sender.pending_transactions.append({'txid': txid, 'from': sender.username, 'amount': amount, 'type': 'request'})
        return txid

    # Method to approve a pending transaction
    def approve(self, txid):
        for tx in self.pending_transactions:
            if tx['txid'] == txid:
                if tx.get('type') == 'request':
                    if tx['from'].balance >= tx['amount']:
                        tx['from'].balance -= tx['amount']
                        self.balance += tx['amount']
                        self.pending_transactions.remove(tx)
                        return "SUCCESS"
                else:
                    self.balance -= tx['amount']
                    tx['from'].balance += tx['amount']
                    self.pending_transactions.remove(tx)
                    return "SUCCESS"
        return "FAIL"

# Define the Teller class, inheriting from User
class Teller(User):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.role = 'teller'

    # Method to deposit money into a user's account
    def deposit(self, user, amount):
        txid = f"TX{len(self.pending_transactions) + 1}"
        user.balance += amount
        return txid

    # Method to withdraw money from a user's account
    def withdraw(self, user, amount):
        if user.balance >= amount:
            txid = f"TX{len(self.pending_transactions) + 1}"
            user.balance -= amount
            return txid
        return "FAIL"

    # Method to enroll a new user
    def enroll(self, username, password):
        return User(username, password)

# Define the Admin class, inheriting from Teller
class Admin(Teller):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.role = 'admin'

    # Method to promote a user to a higher role
    def promote(self, user):
        if user.role == 'user':
            user.role = 'teller'
            return "SUCCESS"
        elif user.role == 'teller':
            user.role = 'admin'
            return "SUCCESS"
        return "FAIL"

    # Method to demote a user to a lower role
    def demote(self, user):
        if user.role == 'admin':
            user.role = 'teller'
            return "SUCCESS"
        elif user.role == 'teller':
            user.role = 'user'
            return "SUCCESS"
        return "FAIL"

# Main function to handle user commands
def main():
    users = {}
    current_user = None

    while True:
        command = input("Enter command: ").strip().split()

        if command[0] == "login":
            username, password = command[1], command[2]
            if username in users and users[username].login(password) == "SUCCESS":
                current_user = users[username]
                print("SUCCESS")
            else:
                print("FAIL")

        elif command[0] == "enroll" and current_user and current_user.role in ['teller', 'admin']:
            username, password = command[1], command[2]
            if username not in users:
                users[username] = User(username, password)
                print("SUCCESS")
            else:
                print("FAIL")

        elif command[0] == "send" and current_user:
            recipient, amount = command[1], float(command[2])
            if recipient in users:
                txid = current_user.send(users[recipient], amount)
                print(txid)
            else:
                print("FAIL")

        elif command[0] == "request" and current_user:
            sender, amount = command[1], float(command[2])
            if sender in users:
                txid = current_user.request(users[sender], amount)
                print(txid)
            else:
                print("FAIL")

        elif command[0] == "approve" and current_user:
            txid = command[1]
            result = current_user.approve(txid)
            print(result)

        elif command[0] == "deposit" and current_user and current_user.role in ['teller', 'admin']:
            username, amount = command[1], float(command[2])
            if username in users:
                txid = current_user.deposit(users[username], amount)
                print(txid)
            else:
                print("FAIL")

        elif command[0] == "withdraw" and current_user and current_user.role in ['teller', 'admin']:
            username, amount = command[1], float(command[2])
            if username in users:
                txid = current_user.withdraw(users[username], amount)
                print(txid)
            else:
                print("FAIL")

        elif command[0] == "promote" and current_user and current_user.role == 'admin':
            username = command[1]
            if username in users:
                result = current_user.promote(users[username])
                print(result)
            else:
                print("FAIL")

        elif command[0] == "demote" and current_user and current_user.role == 'admin':
            username = command[1]
            if username in users:
                result = current_user.demote(users[username])
                print(result)
            else:
                print("FAIL")

        elif command[0] == "logout":
            current_user = None
            print("Logged out.")

        elif command[0] == "exit":
            break

        else:
            print("Invalid command or insufficient permissions.")

# Initialize the admin user and start the main function
if __name__ == "__main__":
    admin = Admin("admin", "Spookytus")
    users = {"admin": admin}
    main()

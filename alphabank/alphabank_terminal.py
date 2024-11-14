class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = 0
        self.role = 'user'
        self.pending_transactions = []

    def login(self, password):
        if self.password == password:
            return "SUCCESS"
        return "FAIL"

    def send(self, recipient, amount):
        if self.balance >= amount:
            txid = f"TX{len(self.pending_transactions) + 1}"
            recipient.pending_transactions.append({'txid': txid, 'from': self.username, 'amount': amount})
            return txid
        return "FAIL"

    def request(self, sender, amount):
        txid = f"TX{len(self.pending_transactions) + 1}"
        sender.pending_transactions.append({'txid': txid, 'from': sender.username, 'amount': amount, 'type': 'request'})
        return txid

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


class Teller(User):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.role = 'teller'

    def deposit(self, user, amount):
        txid = f"TX{len(self.pending_transactions) + 1}"
        user.balance += amount
        return txid

    def withdraw(self, user, amount):
        if user.balance >= amount:
            txid = f"TX{len(self.pending_transactions) + 1}"
            user.balance -= amount
            return txid
        return "FAIL"

    def enroll(self, username, password):
        return User(username, password)


class Admin(Teller):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.role = 'admin'

    def promote(self, user):
        if user.role == 'user':
            user.role = 'teller'
            return "SUCCESS"
        elif user.role == 'teller':
            user.role = 'admin'
            return "SUCCESS"
        return "FAIL"

    def demote(self, user):
        if user.role == 'admin':
            user.role = 'teller'
            return "SUCCESS"
        elif user.role == 'teller':
            user.role = 'user'
            return "SUCCESS"
        return "FAIL"


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

if __name__ == "__main__":
    admin = Admin("admin", "Spookytus")
    users = {"admin": admin}
    main()

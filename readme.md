# AlphaBank System
Team: Nick Cavanah, Ben Dawes, Isaac Krosschell
Purdue University, ECE 56401, Fall 2024
## Overview
The AlphaBank system is a simple banking application that allows users to perform various banking operations such as creating accounts, depositing and withdrawing money, sending and requesting funds, and managing user roles. The system supports three types of users: regular users, tellers, and administrators.

## Features
- User authentication (login and logout)
- Create new users with specific roles
- Deposit and withdraw money (tellers only)
- Send and request money between users
- Approve pending transactions
- Promote and demote users (admins only)
- Check account balance
- View pending transactions

## User Roles
- **USER**: Regular user with basic permissions.
- **TELLER**: User with permissions to handle deposits and withdrawals.
- **ADMIN**: User with full permissions, including user management.

## Commands
- `login <username> <password>`: Log in as a user.
- `logout`: Log out the current user.
- `deposit <username> <amount>`: Deposit money into a user's account (tellers only).
- `withdraw <username> <amount>`: Withdraw money from a user's account (tellers only).
- `send <username> <amount>`: Send money to another user.
- `request <username> <amount>`: Request money from another user.
- `approve <transaction_id>`: Approve a pending transaction.
- `promote <username>`: Promote a user to a higher role (admin only).
- `demote <username>`: Demote a user to a lower role (admin only, cannot demote self).
- `balance`: Check the balance of the logged-in user.
- `enroll <username> <password> <role>`: Create a new user with the specified role (admin only).
- `pending`: View pending transactions involving the logged-in user.

## To Log In
- Build the Dockerfile in the directory
- Execute the following in a Linux terminal: docker run --rm -p 6201:6201 --name alphabank-test compsecproject
- In a separate terminal, execute the client.py python script. Then login with 'admin' and 'Spookytus' for admin access, or log in with user credentials created via 'enroll'
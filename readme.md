# AlphaBank System

## Overview
The AlphaBank system is a simple banking application that allows users to perform various banking operations such as creating accounts, depositing and withdrawing money, sending and requesting funds, and managing user roles. The system supports three types of users: regular users, tellers, and administrators.

## Features
- User authentication (login and logout)
- Create new users with specific roles
- Deposit and withdraw money (tellers only)
- Send and request money between users
- Approve pending transactions
- Promote and demote users (admins only)

## User Roles
- **USER**: Regular user with basic permissions.
- **TELLER**: User with permissions to handle deposits and withdrawals.
- **ADMIN**: User with full permissions, including user management.

## Commands
- `login <username> <password>`: Log in as a user.
- `logout`: Log out the current user.
- `create_user <username> <password> <role>`: Create a new user with the specified role (admin only).
- `deposit <username> <amount>`: Deposit money into a user's account (tellers only).
- `withdraw <username> <amount>`: Withdraw money from a user's account (tellers only).
- `send <username> <amount>`: Send money to another user.
- `request <username> <amount>`: Request money from another user.
- `approve <transaction_id>`: Approve a pending transaction.
- `promote <username>`: Promote a user to a higher role (admin only).
- `demote <username>`: Demote a user to a lower role (admin only).

## Running the Server
To start the AlphaBank server, run the following command:

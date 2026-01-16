# 🏦 ATM Management System (Python + MySQL)

A **console-based ATM Management System** developed using **Python** and **MySQL**.  
This project simulates real-world ATM and banking operations, including secure account handling, transactions, and admin monitoring.

---

## 🚀 Features

### 👤 User Functions
- Create and close bank accounts
- Secure login using **Account Number & PIN**
- Check account balance
- Deposit money
- Withdraw money with **daily withdrawal limit**
- Transfer funds between accounts
- Change ATM PIN
- View **Mini Statement (last 5 transactions)**
- Search transactions by **date range**
- Export transaction history to **CSV file**
- Interest crediting feature

---

### 🛠 Admin Functions
- Secure admin login
- View all customer accounts
- View all system transactions

---

## 🗄 Database Schema

### `ac_details`
| Column | Type | Description |
|------|------|------------|
| ac_no | VARCHAR | Account Number (Primary Key) |
| c_name | VARCHAR | Customer Name |
| pin | VARCHAR | Account PIN |
| opening_balance | DECIMAL | Current Balance |

### `transition_table`
| Column | Type | Description |
|------|------|------------|
| id | INT | Transaction ID |
| ac_no | VARCHAR | Account Number |
| type | ENUM | deposit, withdraw, transfer, interest |
| amount | DECIMAL | Transaction Amount |
| date | DATETIME | Transaction Date |

---

## 🧰 Technologies Used
- Python 3
- MySQL
- mysql-connector-python
- CSV Module
- Datetime Module

---

## ⚙️ Installation & Setup

### 1️⃣ Install Dependencies
```bash
pip install mysql-connector-python

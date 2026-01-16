import mysql.connector
import csv
from datetime import datetime, date

# ========= Database Connection =========
def connect_db(database=True):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password = "12345",
        database="atm" if database else None
    )
                                    #use password = "12345" 
# ========= Database Setup =========
def create_database():
    conn = connect_db(False)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS atm")
    conn.commit()
    conn.close()

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ac_details (
        ac_no VARCHAR(20) PRIMARY KEY,
        c_name VARCHAR(100) NOT NULL,
        pin VARCHAR(10) NOT NULL,
        opening_balance DECIMAL(15, 2) DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transition_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ac_no VARCHAR(20),
        type ENUM('deposit', 'withdraw', 'transfer_in', 'transfer_out', 'interest') NOT NULL,
        amount DECIMAL(15, 2) NOT NULL,
        date DATETIME NOT NULL,
        FOREIGN KEY (ac_no) REFERENCES ac_details(ac_no) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# ========= Account Management =========
def create_account():
    conn = connect_db()
    cur = conn.cursor()
    ac_no = input("Enter new account number: ")
    name = input("Enter account holder name: ")
    pin = input("Set a 4-digit PIN: ")
    bal = float(input("Enter opening balance: "))
    cur.execute("INSERT INTO ac_details VALUES (%s, %s, %s, %s)", (ac_no, name, pin, bal))
    conn.commit()
    conn.close()
    print("✅ New account created successfully!")

def close_account(ac_no):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM ac_details WHERE ac_no=%s", (ac_no,))
    conn.commit()
    conn.close()
    print("❌ Account closed successfully!")
            # ========= Login  =========
def login(ac_no, pin):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ac_details WHERE ac_no=%s AND pin=%s", (ac_no, pin))
    account = cur.fetchone()
    conn.close()
    return account
            # ========= Pin Change =========
def change_pin(ac_no):
    conn = connect_db()
    cur = conn.cursor()
    current_pin = input("Enter current PIN: ")
    cur.execute("SELECT pin FROM ac_details WHERE ac_no=%s", (ac_no,))
    result = cur.fetchone()
    if result and result[0] == current_pin:
        new_pin = input("Enter new 4-digit PIN: ")
        confirm_pin = input("Confirm new PIN: ")
        if new_pin == confirm_pin:
            cur.execute("UPDATE ac_details SET pin=%s WHERE ac_no=%s", (new_pin, ac_no))
            conn.commit()
            print("🔑 PIN changed successfully.")
        else:
            print("❌ PINs do not match.")
    else:
        print("❌ Incorrect current PIN.")
    conn.close()

# ========= Transactions =========
def check_balance(ac_no):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT opening_balance FROM ac_details WHERE ac_no=%s", (ac_no,))
    bal = cur.fetchone()
    conn.close()
    print(f"💰 Current Balance: {bal[0]}" if bal else "Account not found.")

def deposit(ac_no, amount, t_type="deposit"):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE ac_details SET opening_balance=opening_balance+%s WHERE ac_no=%s", (amount, ac_no))
    cur.execute("INSERT INTO transition_table (ac_no, type, amount, date) VALUES (%s, %s, %s, %s)",
                (ac_no, t_type, amount, datetime.now()))
    conn.commit()
    conn.close()
    print(f"✅ {amount} deposited successfully.")

def withdraw(ac_no, amount, daily_limit=20000):
    conn = connect_db()
    cur = conn.cursor()

    # Check today's withdrawal total
    today = date.today()
    cur.execute("""
        SELECT SUM(amount) FROM transition_table 
        WHERE ac_no=%s AND type='withdraw' AND DATE(date)=%s
    """, (ac_no, today))
    total_today = cur.fetchone()[0] or 0

    if total_today + amount > daily_limit:
        print(f"⚠ Daily withdrawal limit of {daily_limit} exceeded.")
        conn.close()
        return

    cur.execute("SELECT opening_balance FROM ac_details WHERE ac_no=%s", (ac_no,))
    bal = cur.fetchone()
    if not bal or bal[0] < amount:
        print("❌ Insufficient funds.")
    else:
        cur.execute("UPDATE ac_details SET opening_balance=opening_balance-%s WHERE ac_no=%s", (amount, ac_no))
        cur.execute("INSERT INTO transition_table (ac_no, type, amount, date) VALUES (%s, 'withdraw', %s, %s)",
                    (ac_no, amount, datetime.now()))
        conn.commit()
        print(f"✅ {amount} withdrawn successfully.")
    conn.close()

def transfer_funds(sender, receiver, amount):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT opening_balance FROM ac_details WHERE ac_no=%s", (sender,))
    bal = cur.fetchone()
    if not bal or bal[0] < amount:
        print("❌ Insufficient funds.")
        conn.close()
        return
    cur.execute("UPDATE ac_details SET opening_balance=opening_balance-%s WHERE ac_no=%s", (amount, sender))
    cur.execute("UPDATE ac_details SET opening_balance=opening_balance+%s WHERE ac_no=%s", (amount, receiver))
    cur.execute("INSERT INTO transition_table (ac_no, type, amount, date) VALUES (%s, 'transfer_out', %s, %s)",
                (sender, amount, datetime.now()))
    cur.execute("INSERT INTO transition_table (ac_no, type, amount, date) VALUES (%s, 'transfer_in', %s, %s)",
                (receiver, amount, datetime.now()))
    conn.commit()
    conn.close()
    print(f"💸 {amount} transferred successfully.")

def credit_interest(ac_no, rate=2.5):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT opening_balance FROM ac_details WHERE ac_no=%s", (ac_no,))
    bal = cur.fetchone()
    if bal:
        interest = bal[0] * rate / 100
        deposit(ac_no, interest, "interest")
        print(f"💰 Interest of {interest} credited.")
    else:
        print("❌ Account not found.")
    conn.close()

def mini_statement(ac_no):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT type, amount, date FROM transition_table WHERE ac_no=%s ORDER BY date DESC LIMIT 5", (ac_no,))
    rows = cur.fetchall()
    conn.close()
    print("\n📜 Last 5 Transactions:")
    for r in rows:
        print(f"{r[2]} | {r[0]} | {r[1]}")

def transaction_by_date(ac_no, start, end):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT type, amount, date FROM transition_table
        WHERE ac_no=%s AND DATE(date) BETWEEN %s AND %s ORDER BY date DESC
    """, (ac_no, start, end))
    rows = cur.fetchall()
    conn.close()
    print(f"\n🔍 Transactions from {start} to {end}:")
    for r in rows:
        print(f"{r[2]} | {r[0]} | {r[1]}")

def export_transactions(ac_no):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transition_table WHERE ac_no=%s", (ac_no,))
    rows = cur.fetchall()
    conn.close()
    filename = f"{ac_no}_transactions.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Account No", "Type", "Amount", "Date"])
        writer.writerows(rows)
    print(f"📂 Transactions exported to {filename}")

# ========= Admin Functions =========
def admin_login():
    username = input("Admin username: ")
    password = input("Admin password: ")
    return username == "admin" and password == "admin123"

def view_all_accounts():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ac_details")
    for row in cur.fetchall():
        print(row)
    conn.close()

def view_all_transactions():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transition_table ORDER BY date DESC")
    for row in cur.fetchall():
        print(row)
    conn.close()

# ========= ATM Menu =========
def atm():
    while True:
        print("\n===== ATM System =====")
        print("1. Login & Use ATM")
        print("2. Create New Account")
        print("3. Admin Panel")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            ac = input("Enter Account Number: ")
            pin = input("Enter PIN: ")
            if not login(ac, pin):
                print("❌ Invalid login.")
                continue

            while True:
                print("\n1. Check Balance")
                print("2. Deposit")
                print("3. Withdraw")
                print("4. Mini Statement")
                print("5. Transfer Funds")
                print("6. Credit Interest")
                print("7. Change PIN")
                print("8. Search Transactions by Date")
                print("9. Export Transactions to CSV")
                print("10. Close Account")
                print("11. Logout")
                op = input("Enter choice: ")

                if op == "1": check_balance(ac)
                elif op == "2": deposit(ac, float(input("Amount: ")))
                elif op == "3": withdraw(ac, float(input("Amount: ")))
                elif op == "4": mini_statement(ac)
                elif op == "5": transfer_funds(ac, input("Receiver: "), float(input("Amount: ")))
                elif op == "6": credit_interest(ac)
                elif op == "7": change_pin(ac)
                elif op == "8": transaction_by_date(ac, input("Start date (YYYY-MM-DD): "), input("End date (YYYY-MM-DD): "))
                elif op == "9": export_transactions(ac)
                elif op == "10": close_account(ac); break
                elif op == "11": break
                else: print("❌ Invalid choice.")

        elif choice == "2":
            create_account()

        elif choice == "3":
            if admin_login():
                while True:
                    print("\n*** ADMIN PANEL ***")
                    print("1. View All Accounts")
                    print("2. View All Transactions")
                    print("3. Back")
                    admin_choice = input("Enter choice: ")
                    if admin_choice == "1": view_all_accounts()
                    elif admin_choice == "2": view_all_transactions()
                    elif admin_choice == "3": break
                    else: print("❌ Invalid choice.")
            else:
                print("❌ Access Denied.")

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice.")

# ========= Start =========
if __name__ == "__main__":
    create_database()
    create_tables()
    atm()

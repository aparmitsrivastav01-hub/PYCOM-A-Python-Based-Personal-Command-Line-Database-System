# e_commerce_app.py
import mysql.connector as m
from mysql.connector import Error
from datetime import date,time,datetime
import sys
import getpass
import random
import winsound

'''(input hidden)'''

# ---------- CONFIG ----------
DB_CONFIG = dict(host='localhost', user='root', password='NewPassword123', database='e_commerce')
# ----------------------------


banner = r"""
#                                       
#    ______ ___.__. ____  ____   _____  
#    \____ <   |  |/ ___\/  _ \ /     \ 
#    |  |_> >___  \  \__(  <_> )  Y Y  \
#    |   __// ____|\___  >____/|__|_|  /
#    |__|   \/         \/            \/ 
"""


# Global session
session = {
    "role": None,       # "customer" or "seller"
    "id": None,         # customer_id or seller_id
    "username": None
}

def get_db_connection():
    try:
        conn = m.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print("Error connecting to database:", e)
        return None

def safe_input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print("Value too small. Try again.")
                continue
            if max_val is not None and val > max_val:
                print("Value too large. Try again.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")

def safe_input_str(prompt, allow_empty=False):
    while True:
        s = input(prompt).strip()
        if not allow_empty and s == "":
            print("Input cannot be empty.")
            continue
        return s

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning ☀️"
    elif hour < 18:
        return "Good Afternoon 🌤️"
    return "Good Evening 🌙"

quotes = [
    "🛍️ Shop smart, save smart!",
    "🤖 Powered by Python. Made for You.",
    "⚡ Fast. Simple. Secure."
] 


def welcome():
    print(banner)
    def slow_print(text, delay=0.05):
        import time
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    print("-"*70)


    slow_print(random.choice(quotes), 0.04)
    slow_print(f"{get_greeting()} and Namaste 🙏", 0.04)
    slow_print(" Welcome to PYCOM — Your Python Based E-Commerce Experience!", 0.04)
    slow_print("  🛒 🛒 🛒", 0.04)

    
    print("-"*70)
    print("1 - SELLER")
    print("2 - CUSTOMER")
    print("0 - EXIT")

    while True:
        choice = safe_input_int("\nEnter 0, 1 or 2: ")
        if choice == 1:
            scheck()
        elif choice == 2:
            identity()
        elif choice == 0:
            slow_print("Thank you for visiting PyCom 🛒", 0.03)
            sys.exit(0)
        else:
            print("Please enter a valid option.")
# ----------------- CUSTOMER FLOW -----------------
def identity():
    while True:
        print('-'*64)
        print('1 - Existing user (Login)')
        print('2 - New user (Create account)')
        print('0 - Back')
        choice = safe_input_int('Enter 0, 1 or 2: ')
        if choice == 1:
            login()
            break
        elif choice == 2:
            create_customer()
            break
        elif choice == 0:
            return
        else:
            print("Enter a valid input.")

def create_customer():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()

    print('-'*64)
    while True:
        name = safe_input_str('Enter your full name: ')
        if any(char.isdigit() for char in name):
            print("Name should not contain digits.")
            continue
        break

    username = safe_input_str('Enter username: ')
    password = getpass.getpass('Enter password : ') 
    address = safe_input_str('Enter address: ')
    while True:
        phone = safe_input_str('Enter phone (10 digits): ')
        if phone.isdigit() and len(phone) == 10:
            break
        print("Phone must be 10 digits.")
    while True:
        email = safe_input_str('Enter email: ')
        if "@" in email and "." in email:
            break
        print("Please enter a valid email containing '@' and '.'")

    try:
        co.execute('SELECT MAX(Customer_ID) FROM Customers')
        row = co.fetchone()
        new_id = 1 if (row is None or row[0] is None) else int(row[0]) + 1

        co.execute(
            "INSERT INTO Customers (Customer_ID, Username, Password, Name, Address, Phone, Email) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (new_id, username, password, name, address, phone, email)
        )
        conn.commit()
        print('-'*64)
        print('Your account is successfully created')
        print('Your customer ID is:', new_id)
        # set session and go to menu
        session['role'] = 'customer'
        session['id'] = new_id
        session['username'] = username
        menu()
    except Error as e:
        print("Database error while creating account:", e)
    finally:
        co.close()
        conn.close()

def login():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        print('-'*64)
        username = safe_input_str('Enter username: ')
        password = getpass.getpass('Enter password: ')
        co.execute('SELECT Customer_ID, Password FROM Customers WHERE Username=%s', (username,))
        row = co.fetchone()
        if row is None:
            print("Invalid username.")
            return
        db_cust_id, db_pass = row
        if password == db_pass:
            print("Login successful.")
            session['role'] = 'customer'
            session['id'] = db_cust_id
            session['username'] = username
            menu()
        else:
            print("Incorrect password.")
    except Error as e:
        print("Database error during login:", e)
    finally:
        co.close()
        conn.close()

# ----------------- CUSTOMER MENU -----------------
def menu():
    if session.get('role') != 'customer':
        print("Please login as a customer to access this menu.")
        return

    while True:
        print('-'*64)
        print('***************************** MENU *****************************')
        print('1 - SEARCH')
        print('2 - VIEW PURCHASE HISTORY')
        print('3 - PLACE ORDER')
        print('4 - RETURN')
        print('5 - CANCEL ORDER')
        print('6 - GIVE FEEDBACK')
        print('7 - LOGOUT')
        print('0 - EXIT')
        ch = safe_input_int('Enter your choice: ')
        if ch == 1:
            search()
        elif ch == 2:
            purchase_history()
        elif ch == 3:
            order()
        elif ch == 4:
            product_return()
        elif ch == 5:
            cancel_order()
        elif ch == 6:
            feedback()
        elif ch == 7:
            print("Logged out.")
            session['role'] = None
            session['id'] = None
            session['username'] = None
            return
        elif ch == 0:
            print("Goodbye.")
            sys.exit(0)
        else:
            print('Please enter valid option.')

# ----------------- SEARCH -----------------
def search():
    while True:
        print('-'*64)
        print('1 - search via categories')
        print('2 - search via brands')
        print('3 - view all products')
        print('0 - back')
        ch = safe_input_int('Enter your choice: ')
        if ch == 1:
            category()
        elif ch == 2:
            brand()
        elif ch == 3:
            allproduct()
        elif ch == 0:
            return
        else:
            print('Please enter valid input.')

def category():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        co.execute('SELECT DISTINCT Category FROM Products')
        rows = co.fetchall()
        print("Available categories:")
        for r in rows:
            print('-', r[0])
        cat = safe_input_str('Enter category to search (partial allowed): ')
        co.execute('SELECT * FROM Products WHERE Category LIKE %s', ('%'+cat+'%',))
        products = co.fetchall()
        if not products:
            print("No products found for that category.")
            return
        show_products_and_offer_order(products)
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def brand():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        co.execute('SELECT DISTINCT Brand_Name FROM Products')
        rows = co.fetchall()
        print("Available brands:")
        for r in rows:
            print('-', r[0])
        br = safe_input_str('Enter brand to search (partial allowed): ')
        co.execute('SELECT * FROM Products WHERE Brand_Name LIKE %s', ('%'+br+'%',))
        products = co.fetchall()
        if not products:
            print("No products found for that brand.")
            return
        show_products_and_offer_order(products)
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def allproduct():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        co.execute('SELECT * FROM Products')
        products = co.fetchall()
        if not products:
            print("No products found.")
            return
        show_products_and_offer_order(products)
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def show_products_and_offer_order(products):
    for idx, p in enumerate(products, start=1):
        print('-'*40)
        print(f'PRODUCT NUMBER {idx}')
        # Assuming columns: Product_ID, Category, Name, Quantity, Price, Brand_Name, Seller_ID
        print('Product ID:', p[0])
        print('Category:', p[1])
        print('Name:', p[2])
        print('Quantity available:', p[3])
        print('Price:', p[4])
        print('Brand Name:', p[5])
        print('Seller ID:', p[6])
    print('-'*40)
    print('1 - Place order')
    print('0 - Back')
    choice = safe_input_int('Enter your choice: ')
    if choice == 1:
        order()
    else:
        return

# ----------------- PURCHASE HISTORY -----------------
def purchase_history():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        cust = session.get('id') or safe_input_int('Enter your customer id to proceed: ')
        co.execute('SELECT * FROM Orders WHERE Customer_ID=%s', (cust,))
        data = co.fetchall()
        if data:
            for idx, i in enumerate(data, start=1):
                print('-'*40)
                print("ORDER NUMBER:", idx)
                # Assuming Orders columns: Transaction_ID, Customer_ID, Product_ID, Date_of_dispatch, Quantity, Price, Total_Amount
                print("Transaction ID:", i[0])
                print("Product ID:", i[2])
                print("Date of dispatch:", i[3])
                print("Quantity placed:", i[4])
                print("Price:", i[5])
                print("Total Amount:", i[6])
                print('-'*40)
        else:
            print('No orders placed.')
        # back to menu automatically
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# ----------------- ORDER -----------------
def order():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        print('TO PLACE ORDER - ENTER DETAILS:')
        cust = session.get('id')
        if not cust:
            cust = safe_input_int('Enter your customer id to proceed: ')
        prd = safe_input_int('Enter the product id: ')
        co.execute('SELECT Quantity, Price FROM Products WHERE Product_ID=%s', (prd,))
        row = co.fetchone()
        if row is None:
            print("Product not found.")
            return
        available_qty, price = row
        if available_qty <= 0:
            print("Out of stock.")
            return
        qty = safe_input_int('Enter quantity of product: ', min_val=1)
        if qty > available_qty:
            print('Sufficient quantity is not available. Quantity available:', available_qty)
            return
        # compute transaction id
        co.execute('SELECT MAX(Transaction_ID) FROM Orders')
        row = co.fetchone()
        trans_id = 1 if (row is None or row[0] is None) else int(row[0]) + 1
        total_amount = price * qty
        print('Your total amount is:', total_amount)
        print('1 - Confirm order')
        print('0 - Cancel')
        ch = safe_input_int('Enter choice: ')
        if ch == 1:
            today = date.today().isoformat()
            co.execute(
                'INSERT INTO Orders (Transaction_ID, Customer_ID, Product_ID, Date_of_dispatch, Quantity, Price, Total_Amount) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                (trans_id, cust, prd, today, qty, price, total_amount)
            )
            co.execute('UPDATE Products SET Quantity = Quantity - %s WHERE Product_ID = %s', (qty, prd))
            conn.commit()
            print('Order placed successfully. Transaction ID:', trans_id)
        else:
            print('Order cancelled.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# ----------------- RETURN / EXCHANGE / CANCEL -----------------
def product_return():
    print('Product Return / Exchange')
    print('1 - Damaged')
    print('2 - Broken')
    print('3 - Wrong item')
    print('4 - Wrong fitting')
    print('5 - Other')
    print('0 - Back')
    choice = safe_input_int('Enter choice: ')
    if choice == 0:
        return
    if choice in (1, 2):
        print("We'll process cancellation/refund.")
        cancel_order()
    elif choice in (3, 4):
        print("You may choose to exchange or cancel.")
        print("1 - Exchange")
        print("2 - Cancel")
        a = safe_input_int('Enter choice: ')
        if a == 1:
            exchange()
        else:
            cancel_order()
    elif choice == 5:
        reason = safe_input_str("Please enter your reason: ")
        print("1 - Exchange")
        print("2 - Cancel")
        a = safe_input_int('Enter choice: ')
        if a == 1:
            exchange()
        else:
            cancel_order()
    else:
        print('Invalid choice.')

def exchange():
    print('Exchange flow:')
    cust = session.get('id') or safe_input_int('Enter your customer id: ')
    pro = safe_input_int('Enter product id to exchange: ')
    print("1 - Rebuy same product")
    print("2 - Buy something else")
    a = safe_input_int('Enter your choice: ')
    if a == 1:
        order()
    elif a == 2:
        search()
    else:
        print('Invalid choice.')

def cancel_order():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        print('Cancel order:')
        cust = session.get('id') or safe_input_int('Enter your customer id: ')
        pro = safe_input_int('Enter product id: ')
        tra = safe_input_int('Enter transaction id: ')
        co.execute('SELECT * FROM Orders WHERE Transaction_ID=%s', (tra,))
        data = co.fetchone()
        if data is None:
            print("Transaction not found.")
            return
        # data columns assumed: Transaction_ID, Customer_ID, Product_ID, Date_of_dispatch, Quantity, Price, Total_Amount
        if data[1] == cust and data[2] == pro:
            qty = data[4]
            co.execute('DELETE FROM Orders WHERE Transaction_ID=%s', (tra,))
            co.execute('UPDATE Products SET Quantity = Quantity + %s WHERE Product_ID = %s', (qty, pro))
            conn.commit()
            print('Your order has been successfully cancelled.')
        else:
            print('Customer ID or Product ID does not match the transaction.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# ----------------- FEEDBACK -----------------
def feedback():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        print('Feedback')
        print('1 - About app')
        print('2 - About product')
        ch = safe_input_int('Enter your choice: ')
        if ch == 1:
            feed = safe_input_str('Type your suggestions: ')
            cust = session.get('id') or safe_input_int('Enter your customer id: ')
            co.execute('INSERT INTO Feedbacks (Customer_ID, Feedback) VALUES (%s, %s)', (cust, feed))
            conn.commit()
            print('Thank you for your feedback.')
        elif ch == 2:
            cust = session.get('id') or safe_input_int('Enter your customer id: ')
            pro = safe_input_int('Enter the product id: ')
            co.execute('SELECT Seller_ID FROM Products WHERE Product_ID=%s', (pro,))
            row = co.fetchone()
            if not row:
                print("Product not found.")
                return
            sell = row[0]
            # Try to find seller name if seller table exists
            co.execute('SELECT Seller_Name FROM Seller WHERE Seller_ID=%s', (sell,))
            srow = co.fetchone()
            sname = srow[0] if srow else ''
            feed = safe_input_str('Type your suggestions: ')
            # Insert into a feedbacks table (depending on your schema adjust columns)
            # Example: Feedbacks(Customer_ID, Feedback, Seller_ID, Product_ID, Seller_Name)
            co.execute('INSERT INTO Feedbacks (Customer_ID, Feedback, Seller_ID, Product_ID, Seller_Name) VALUES (%s,%s,%s,%s,%s)', (cust, feed, sell, pro, sname))
            conn.commit()
            print('Thank you for your feedback.')
        else:
            print('Invalid input.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# ----------------- SELLER FLOW -----------------
def scheck():
    while True:
        print('-'*64)
        print('1 - Existing seller (Login)')
        print('2 - New seller (Create account)')
        print('0 - Back')
        x = safe_input_int('Enter 0, 1 or 2: ')
        if x == 1:
            slogin()
            break
        elif x == 2:
            seller_create()
            break
        elif x == 0:
            return
        else:
            print('Please enter valid input.')

def seller_create():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        name = safe_input_str('Enter your full name: ')
        username = safe_input_str('Enter a username: ')
        password = getpass.getpass('Enter a password (hidden): ')
        bname = safe_input_str('Enter a Brand Name: ')
        while True:
            phone = safe_input_str('Enter your Phone No. (10 digits): ')
            if phone.isdigit() and len(phone) == 10:
                break
            print("Enter valid phone.")
        while True:
            email = safe_input_str('Enter your email id: ')
            if "@" in email and "." in email:
                break
            print("Please enter a valid email.")
        co.execute('SELECT MAX(Seller_ID) FROM Seller')
        srow = co.fetchone()
        sid = 1 if (srow is None or srow[0] is None) else int(srow[0]) + 1
        co.execute('INSERT INTO Seller (Seller_ID, Seller_Name, Brand_Name, Username, Password, Phone, Email) VALUES (%s,%s,%s,%s,%s,%s,%s)', (sid, name, bname, username, password, phone, email))
        conn.commit()
        print('Your account is successfully created. Your seller ID is:', sid)
        session['role'] = 'seller'
        session['id'] = sid
        session['username'] = username
        smenu()
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def slogin():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        username = safe_input_str('Enter username: ')
        password = getpass.getpass('Enter password (hidden): ')
        co.execute('SELECT Seller_ID, Password FROM Seller WHERE Username=%s', (username,))
        row = co.fetchone()
        if row is None:
            print("Invalid username.")
            return
        sid, db_pass = row
        if password == db_pass:
            print("Login successful.")
            session['role'] = 'seller'
            session['id'] = sid
            session['username'] = username
            smenu()
        else:
            print("Incorrect password.")
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# ----------------- SELLER MENU -----------------
def smenu():
    if session.get('role') != 'seller':
        print("Please login as seller.")
        return
    while True:
        print('-'*64)
        print('Seller Menu:')
        print('1 - Add Item')
        print('2 - Delete Item')
        print('3 - Update Item')
        print('4 - Give feedback')
        print('5 - View your products')
        print('6 - Logout')
        print('0 - Exit')
        c = safe_input_int('Enter your choice: ')
        if c == 1:
            Adds()
        elif c == 2:
            delete_item()
        elif c == 3:
            update_item()
        elif c == 4:
            sfeedback()
        elif c == 5:
            sview()
        elif c == 6:
            session['role'] = None
            session['id'] = None
            session['username'] = None
            print('Logged out.')
            return
        elif c == 0:
            print('Goodbye.')
            sys.exit(0)
        else:
            print('Enter valid input.')

def Adds():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        cat = safe_input_str('Enter category of product: ')
        name = safe_input_str('Enter name of product: ')
        qyt = safe_input_int('Enter quantity of product: ', min_val=0)
        pri = safe_input_int('Enter price of product: ', min_val=0)
        sid = session.get('id') or safe_input_int('Enter your seller ID: ')
        co.execute('SELECT Seller_Name FROM Seller WHERE Seller_ID=%s', (sid,))
        data1 = co.fetchone()
        if not data1:
            print("Please enter valid seller_id.")
            return
        bname = safe_input_str('Enter your brand name: ')
        co.execute('SELECT MAX(Product_ID) FROM Products')
        data = co.fetchone()
        h = 1 if (data is None or data[0] is None) else int(data[0]) + 1
        co.execute('INSERT INTO Products (Product_ID, Category, Name, Quantity, Price, Brand_Name, Seller_ID) VALUES (%s,%s,%s,%s,%s,%s,%s)', (h, cat, name, qyt, pri, bname, sid))
        conn.commit()
        print('Your product is successfully added. Your product ID is', h)
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def delete_item():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        ch = safe_input_int('Enter product_ID to delete: ')
        co.execute('SELECT Seller_ID FROM Products WHERE Product_ID=%s', (ch,))
        row = co.fetchone()
        if not row:
            print('Product not found.')
            return
        seller_of_product = row[0]
        if session.get('role') == 'seller' and session.get('id') != seller_of_product:
            print('You can only delete your own products.')
            return
        co.execute('DELETE FROM Products WHERE Product_ID=%s', (ch,))
        conn.commit()
        print('Your product is successfully deleted.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def update_item():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        print('1 - Update price')
        print('2 - Update quantity')
        print('3 - Change product name')
        print('4 - Change brand name')
        print('5 - Change category')
        ch = safe_input_int('Enter your choice: ')
        pid1 = safe_input_int('Enter product ID: ')
        co.execute('SELECT Seller_ID FROM Products WHERE Product_ID=%s', (pid1,))
        row = co.fetchone()
        if not row:
            print('Please enter valid Product_ID.')
            return
        seller_of_product = row[0]
        if session.get('role') == 'seller' and session.get('id') != seller_of_product:
            print('You can only update your own products.')
            return
        if ch == 1:
            pri = safe_input_int('Enter price to update: ', min_val=0)
            co.execute('UPDATE Products SET Price=%s WHERE Product_ID=%s', (pri, pid1))
            conn.commit()
            print('Price successfully updated.')
        elif ch == 2:
            qty = safe_input_int('Enter quantity to update: ', min_val=0)
            co.execute('UPDATE Products SET Quantity=%s WHERE Product_ID=%s', (qty, pid1))
            conn.commit()
            print('Quantity successfully updated.')
        elif ch == 3:
            s = safe_input_str('Enter new name of product: ')
            co.execute('UPDATE Products SET Name=%s WHERE Product_ID=%s', (s, pid1))
            conn.commit()
            print('Name successfully updated.')
        elif ch == 4:
            brand = safe_input_str('Enter new brand name: ')
            co.execute('UPDATE Products SET Brand_Name=%s WHERE Product_ID=%s', (brand, pid1))
            conn.commit()
            print('Brand name successfully updated.')
        elif ch == 5:
            cat = safe_input_str('Enter new category: ')
            co.execute('UPDATE Products SET Category=%s WHERE Product_ID=%s', (cat, pid1))
            conn.commit()
            print('Category successfully updated.')
        else:
            print('Please enter valid input.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def sfeedback():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        feed = safe_input_str('Type your suggestions: ')
        sid = session.get('id') or safe_input_int('Enter your seller ID: ')
        rating = safe_input_int('Enter rating out of 5: ', min_val=0, max_val=5)
        # Assuming sfeedback table has columns (Seller_ID, Feedback, Rating)
        co.execute('INSERT INTO SFeedback (Seller_ID, Feedback, Rating) VALUES (%s,%s,%s)', (sid, feed, rating))
        conn.commit()
        print('Thank you for your feedback.')
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

def sview():
    conn = get_db_connection()
    if not conn:
        return
    co = conn.cursor()
    try:
        sell = session.get('id') or safe_input_int('Enter your Seller_ID: ')
        co.execute('SELECT Product_ID, Name FROM Products WHERE Seller_ID=%s', (sell,))
        data = co.fetchall()
        if not data:
            print('No products found for this seller.')
            return
        print('Following are your Product IDs:')
        for i in data:
            print('Product_ID:', i[0], 'Product Name:', i[1])
    except Error as e:
        print("Database error:", e)
    finally:
        co.close()
        conn.close()

# --------------- MAIN ---------------
if __name__ == '__main__':
    try:
        welcome()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        sys.exit(0)

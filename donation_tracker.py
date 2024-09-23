import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import mysql.connector
import json

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="yourpassward",
            database="donationtrackerkhushi"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error connecting to MySQL: {err}")
        return None

# -- Create the database
# CREATE DATABASE IF NOT EXISTS donationtrackerkhushi;

# -- Use the created database
# USE donationtrackerkhushi;

# -- Create the donate1 table
# CREATE TABLE IF NOT EXISTS donate1 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     donor_name VARCHAR(255) NOT NULL,
#     email VARCHAR(255) NOT NULL,
#     phone_number VARCHAR(20) NOT NULL,
#     amount DECIMAL(10, 2) NOT NULL,
#     date DATE NOT NULL,
#     donation_type VARCHAR(50) NOT NULL,
#     payment_method VARCHAR(50) NOT NULL,
#     transaction_id VARCHAR(255)
# );

HEIGHT = 1000
WIDTH = 1000

root = tk.Tk()
root.title("Donation Tracker")

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

bg_img = tk.PhotoImage(file="donate.png")
bg_label = tk.Label(root, image=bg_img)
bg_label.place(relx=0.02, rely=0.02, relwidth=0.2, relheight=0.2)

text_label = tk.Label(root, text="Donation Tracker", font=("Times New Roman", 24), bg='#80c1ff')
text_label.place(relx=0.25, rely=0.05, relwidth=0.7, relheight=0.1)

input_frame = tk.Frame(root, bg='#80c1ff', bd=4)
input_frame.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.5)

labels = ["Donor Name:", "Email:", "Phone Number:", "Amount:", "Date (YYYY-MM-DD):", "Donation Type:", "Payment Method:", "Transaction ID:"]
entries = {}
for i, label in enumerate(labels):
    tk.Label(input_frame, text=label, bg='#80c1ff', font=("Times New Roman", 12)).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
    if label == "Donation Type:":
        donation_types = ["Orphan", "Old Age", "Animal Welfare", "Other"]
        donation_type_var = tk.StringVar(value="Orphan")
        entry = tk.Frame(input_frame, bg='#80c1ff')
        for j, type in enumerate(donation_types):
            rb = tk.Radiobutton(entry, text=type, variable=donation_type_var, value=type, bg='#80c1ff', font=("Times New Roman", 12))
            rb.pack(side=tk.LEFT, padx=5, pady=5)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        entries[label] = donation_type_var  
    elif label == "Payment Method:":
        payment_methods = ["Cash", "Credit Card", "PayPal", "Bank Transfer"]
        payment_method_var = tk.StringVar(value="Cash")  
        entry = tk.Frame(input_frame, bg='#80c1ff')
        for j, method in enumerate(payment_methods):
            rb = tk.Radiobutton(entry, text=method, variable=payment_method_var, value=method, bg='#80c1ff', font=("Times New Roman", 12))
            rb.pack(side=tk.LEFT, padx=5, pady=5)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        entries[label] = payment_method_var  
    else:
        entry = tk.Entry(input_frame, width=45, font=("Times New Roman", 12))  
        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        entries[label] = entry


def execute_non_query(query, params=()):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error executing query: {err}")
        finally:
            cursor.close()
            conn.close()

def execute_query(query, params=()):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error executing query: {err}")
        finally:
            cursor.close()
            conn.close()
    return []

# CRUD operations
def get_next_id():
    query = "SELECT IFNULL(MAX(id), 0) + 1 FROM donate1"
    result = execute_query(query)
    return result[0][0] if result else 1

def add_donation():
    donor_name = entries["Donor Name:"].get()
    email = entries["Email:"].get()
    phone_number = entries["Phone Number:"].get()
    amount = entries["Amount:"].get()
    date = entries["Date (YYYY-MM-DD):"].get()
    donation_type = entries["Donation Type:"].get()
    payment_method = entries["Payment Method:"].get()
    transaction_id = entries["Transaction ID:"].get() if payment_method != "Cash" else None
    
    if any(value == "" for value in [donor_name, email, phone_number, amount, date]) or not (donation_type and payment_method):
        messagebox.showwarning("Input Error", "Please fill in all required fields.")
        return

    if payment_method == "Cash":
        query = """
            INSERT INTO donate1 (donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
        """
        params = (donor_name, email, phone_number, amount, date, donation_type, payment_method)
    else:
        query = """
            INSERT INTO donate1 (donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id)
    
    execute_non_query(query, params)
    messagebox.showinfo("Success", "Donation data added successfully!")
    display_data()
    clear_fields() 

def update_donation():
    donor_name = entries["Donor Name:"].get()
    email = entries["Email:"].get()
    phone_number = entries["Phone Number:"].get()
    amount = entries["Amount:"].get()
    date = entries["Date (YYYY-MM-DD):"].get()
    donation_type = entries["Donation Type:"].get()
    payment_method = entries["Payment Method:"].get()
    transaction_id = entries["Transaction ID:"].get() if payment_method != "Cash" else None

    selected_item = donation_tree.selection()
    if not selected_item:
        messagebox.showwarning("Select Record", "Please select a record to update.")
        return
    
    item_values = donation_tree.item(selected_item, 'values')
    record_id = item_values[0]  
    if any(value == "" for value in [donor_name, email, phone_number, amount, date]) or not (donation_type and payment_method):
        messagebox.showwarning("Input Error", "Please fill in all required fields.")
        return

    query = """
        UPDATE donate1
        SET donor_name=%s, email=%s, phone_number=%s, amount=%s, date=%s, donation_type=%s, payment_method=%s, transaction_id=%s
        WHERE id=%s
    """
    params = (donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id, record_id)
    
    execute_non_query(query, params)

    donation_tree.item(selected_item, values=(record_id, donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id))
    
    messagebox.showinfo("Success", "Donation updated successfully!")
    clear_fields()

def save_to_file():
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM donate1")
            rows = cursor.fetchall()
            with open(filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")]), "w") as file:
                json.dump(rows, file, default=str)
            conn.close()
            messagebox.showinfo("Success", "Data saved to file successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to file: {e}")

def upload_from_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                rows = json.load(file)
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE donate1")  
                for row in rows:
                    cursor.execute("""
                        INSERT INTO donate1 (id, donor_name, email, phone_number, amount, date, donation_type, payment_method, transaction_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, row)
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Data uploaded successfully!")
                display_data() 
    except Exception as e:
        messagebox.showerror("Error", f"Error uploading data from file: {e}")

def reassign_ids():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SET @new_id := 0;")
            cursor.execute("""
                UPDATE donate1
                SET id = (@new_id := @new_id + 1)
                ORDER BY date ASC;
            """)
            conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error reassigning IDs: {err}")
        finally:
            cursor.close()
            conn.close()

def delete_donation():
    selected_item = donation_tree.selection()
    if selected_item:
        item_values = donation_tree.item(selected_item, 'values')
        donation_id = item_values[0]  
        
        query = "DELETE FROM donate1 WHERE id = %s"
        execute_non_query(query, (donation_id,))
        
        reassign_ids()
        
        messagebox.showinfo("Success", "Donation data deleted successfully!")
        display_data()
        clear_fields()  
    else:
        messagebox.showwarning("Select Record", "Please select a record to delete.")

def retrieve_data():
    display_data()
    messagebox.showinfo("Success", "Data retrieved successfully!")

def clear_fields():
    for label in labels:
        if label in ["Donation Type:", "Payment Method:"]:
            entries[label].set("Orphan" if label == "Donation Type:" else "Cash")
        else:
            entries[label].delete(0, tk.END)

def display_data():
    query = """
        SELECT * FROM donate1
        ORDER BY date ASC
    """
    results = execute_query(query)
    for row in donation_tree.get_children():
        donation_tree.delete(row)
    
    for idx, row in enumerate(results, start=1):
        donation_tree.insert("", tk.END, values=(idx, *row[1:]))
    

def on_tree_select(event):
    selected_item = donation_tree.selection()
    if selected_item:
        item_values = donation_tree.item(selected_item, 'values')
        entries["Donor Name:"].delete(0, tk.END)
        entries["Donor Name:"].insert(0, item_values[1])
        
        entries["Email:"].delete(0, tk.END)
        entries["Email:"].insert(0, item_values[2])
        
        entries["Phone Number:"].delete(0, tk.END)
        entries["Phone Number:"].insert(0, item_values[3])
        
        entries["Amount:"].delete(0, tk.END)
        entries["Amount:"].insert(0, item_values[4])
        
        entries["Date (YYYY-MM-DD):"].delete(0, tk.END)
        entries["Date (YYYY-MM-DD):"].insert(0, item_values[5])
        
        entries["Donation Type:"].set(item_values[6])
        entries["Payment Method:"].set(item_values[7])
        
        if item_values[8]:
            entries["Transaction ID:"].delete(0, tk.END)
            entries["Transaction ID:"].insert(0, item_values[8])
        else:
            entries["Transaction ID:"].delete(0, tk.END)

data_frame = tk.Frame(root, bg='#ffffff', bd=2)  
data_frame.place(relx=0.1, rely=0.68, relwidth=0.8, relheight=0.25)  

columns = ("ID", "Donor Name", "Email", "Phone Number", "Amount", "Date", "Donation Type", "Payment Method", "Transaction ID")
donation_tree = ttk.Treeview(data_frame, columns=columns, show="headings")
for col in columns:
    donation_tree.heading(col, text=col)
    donation_tree.column(col, width=100)
donation_tree.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=donation_tree.yview)
donation_tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

donation_tree.bind("<ButtonRelease-1>", on_tree_select)

# Buttons
button_frame = tk.Frame(root, bg='#80c1ff', bd=1, )
button_frame.place(relx=0.1, rely=0.58, relwidth=0.8, relheight=0.1)  

tk.Button(button_frame, text="Add Donation", command=add_donation).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
tk.Button(button_frame, text="Update Donation", command=update_donation).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
tk.Button(button_frame, text="Retrieve list", command=retrieve_data).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
tk.Button(button_frame, text="Delete Donation", command=delete_donation).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
tk.Button(button_frame, text="Clear Fields", command=clear_fields).grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)

tk.Button(button_frame, text="Save to File", command=save_to_file).grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
tk.Button(button_frame, text="Upload File", command=upload_from_file).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

root.mainloop()
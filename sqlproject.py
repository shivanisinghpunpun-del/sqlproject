import sqlite3
from tkinter import *
from tkinter import ttk, messagebox

# ------------------------- Database Setup -------------------------
conn = sqlite3.connect("electricity.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS bills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    units INTEGER,
    total_bill REAL
)
""")
conn.commit()
conn.close()

# ------------------------- Tkinter GUI Setup -------------------------
root = Tk()
root.title("⚡ Electric Bill Management System")
root.geometry("900x600")
root.configure(bg="#EAF6F6")

title = Label(root, text="ELECTRIC BILL MANAGEMENT SYSTEM", font=("Arial Black", 18, "bold"), bg="#009688", fg="white", pady=10)
title.pack(fill=X)

# ------------------------- Frames -------------------------
form_frame = Frame(root, bg="#EAF6F6", pady=15)
form_frame.pack(fill=X)

# ------------------------- Input Fields -------------------------
Label(form_frame, text="Customer Name:", bg="#EAF6F6", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
entry_name = Entry(form_frame, width=30, font=("Arial", 12))
entry_name.grid(row=0, column=1, padx=10, pady=5)

Label(form_frame, text="Address:", bg="#EAF6F6", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
entry_address = Entry(form_frame, width=30, font=("Arial", 12))
entry_address.grid(row=1, column=1, padx=10, pady=5)

Label(form_frame, text="Units Consumed:", bg="#EAF6F6", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
entry_units = Entry(form_frame, width=30, font=("Arial", 12))
entry_units.grid(row=2, column=1, padx=10, pady=5)

# ------------------------- Helper Functions -------------------------
def calculate_bill(units):
    if units <= 100:
        return units * 5
    else:
        return 100 * 5 + (units - 100) * 7

def clear_fields():
    entry_name.delete(0, END)
    entry_address.delete(0, END)
    entry_units.delete(0, END)

# ------------------------- Database Operations -------------------------
def add_record():
    name = entry_name.get().strip()
    address = entry_address.get().strip()
    units = entry_units.get().strip()

    if name == "" or address == "" or units == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        units = int(units)
    except ValueError:
        messagebox.showerror("Error", "Units must be a number!")
        return

    total = calculate_bill(units)

    conn = sqlite3.connect("electricity.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO bills (name, address, units, total_bill) VALUES (?, ?, ?, ?)",
                (name, address, units, total))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Bill Added!\nTotal Bill: ₹{total}")
    clear_fields()
    show_records()
    update_revenue()

def update_record():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "Select a record to update.")
        return

    selected = selected_items[0]
    values = tree.item(selected, "values")
    record_id = values[0]

    new_name = entry_name.get().strip()
    new_address = entry_address.get().strip()
    new_units = entry_units.get().strip()

    if new_name == "" or new_address == "" or new_units == "":
        messagebox.showerror("Error", "All fields (Name, Address, Units) are required to update.")
        return

    try:
        new_units = int(new_units)
        if new_units < 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Units must be a positive number!")
        return

    new_total = calculate_bill(new_units)

    try:
        conn = sqlite3.connect("electricity.db")
        cur = conn.cursor()
        cur.execute("""
            UPDATE bills
            SET name=?, address=?, units=?, total_bill=?
            WHERE id=?
        """, (new_name, new_address, new_units, new_total, record_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", f"Bill Updated!\nNew Total: ₹{new_total}")
    except Exception as e:
        messagebox.showerror("Error", f"Update failed: {e}")

    clear_fields()
    show_records()
    update_revenue()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select a record to delete.")
        return
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
    if confirm:
        record_id = tree.item(selected[0], "values")[0]
        conn = sqlite3.connect("electricity.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM bills WHERE id=?", (record_id,))
        conn.commit()
        conn.close()
        show_records()
        update_revenue()
        messagebox.showinfo("Deleted", "Record deleted successfully!")

def show_records():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("electricity.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM bills")
    for row in cur.fetchall():
        tree.insert("", END, values=row)
    conn.close()

def update_revenue():
    conn = sqlite3.connect("electricity.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(total_bill) FROM bills")
    total = cur.fetchone()[0]
    conn.close()
    if total:
        total_label.config(text=f"💰 Total Revenue: ₹{total}")
    else:
        total_label.config(text="💰 Total Revenue: ₹0")

def on_tree_select(event):
    sel = tree.selection()
    if not sel:
        return
    values = tree.item(sel[0], "values")
    entry_name.delete(0, END)
    entry_name.insert(0, values[1])
    entry_address.delete(0, END)
    entry_address.insert(0, values[2])
    entry_units.delete(0, END)
    entry_units.insert(0, values[3])

# ------------------------- Buttons -------------------------
btn_frame = Frame(root, bg="#EAF6F6")
btn_frame.pack(pady=10)

Button(btn_frame, text="Add Bill", width=12, bg="#009688", fg="white", font=("Arial", 11, "bold"), command=add_record).grid(row=0, column=0, padx=10)
Button(btn_frame, text="Update Bill", width=12, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), command=update_record).grid(row=0, column=1, padx=10)
Button(btn_frame, text="Delete Bill", width=12, bg="#F44336", fg="white", font=("Arial", 11, "bold"), command=delete_record).grid(row=0, column=2, padx=10)
Button(btn_frame, text="Clear", width=12, bg="#9C27B0", fg="white", font=("Arial", 11, "bold"), command=clear_fields).grid(row=0, column=3, padx=10)

# ------------------------- Treeview (Table) -------------------------
tree_frame = Frame(root)
tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
tree = ttk.Treeview(tree_frame, columns=("id", "name", "address", "units", "total_bill"),
                    yscrollcommand=scroll_y.set, show="headings", height=10)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_y.config(command=tree.yview)

tree.heading("id", text="ID")
tree.heading("name", text="Customer Name")
tree.heading("address", text="Address")
tree.heading("units", text="Units")
tree.heading("total_bill", text="Total Bill (₹)")

tree.column("id", width=50, anchor=CENTER)
tree.column("name", width=180)
tree.column("address", width=180)
tree.column("units", width=100, anchor=CENTER)
tree.column("total_bill", width=120, anchor=CENTER)

tree.pack(fill=BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# ------------------------- Total Revenue -------------------------
total_label = Label(root, text="💰 Total Revenue: ₹0", font=("Arial Black", 14), bg="#EAF6F6", fg="#009688")
total_label.pack(pady=10)

# ------------------------- Run Setup -------------------------
show_records()
update_revenue()
root.mainloop()

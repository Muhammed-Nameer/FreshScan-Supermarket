import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import random

# ---------------- CONFIG ----------------
DISCOUNT_PERCENT = 5  # as requested

# ------------------- DB FUNCTIONS -------------------
def fetch_products(name=None, category=None):
    con = sqlite3.connect("supermarket.db")
    cur = con.cursor()
    if name:
        cur.execute("SELECT id, name, price, stock FROM products WHERE name = ?", (name,))
    elif category and category != "All":
        cur.execute("SELECT id, name, price, stock FROM products WHERE category = ?", (category,))
    else:
        cur.execute("SELECT id, name, price, stock FROM products")
    rows = cur.fetchall()
    con.close()
    return rows

def fetch_categories():
    con = sqlite3.connect("supermarket.db")
    cur = con.cursor()
    cur.execute("SELECT DISTINCT category FROM products")
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows

# ------------------- MAIN WINDOW -------------------
root = tk.Tk()
root.title("Supermarket System")
root.geometry("1300x720")
root.configure(bg="white")

# Columns frames
left_col = tk.Frame(root, bg="white", bd=2, relief="groove")
middle_col = tk.Frame(root, bg="white", bd=2, relief="groove")
right_col = tk.Frame(root, bg="white", bd=2, relief="groove")

left_col.pack(side="left", fill="y", padx=8, pady=8)
middle_col.pack(side="left", fill="both", expand=True, padx=8, pady=8)
right_col.pack(side="left", fill="y", padx=8, pady=8)

# ------------------- LEFT COLUMN (All Products) -------------------
title_label = tk.Label(left_col, text="All Products", font=("Arial", 16, "bold"),
                       bg="#1b4f72", fg="white", pady=6)
title_label.pack(fill=tk.X)

search_frame = tk.Frame(left_col, bg="white")
search_frame.pack(fill=tk.X, pady=10)

tk.Label(search_frame, text="Category", bg="white", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=4)
category_var = tk.StringVar()
category_combo = ttk.Combobox(search_frame, textvariable=category_var, width=20, state="readonly")
category_combo.grid(row=0, column=1, padx=6)

def populate_categories():
    cats = fetch_categories()
    category_combo['values'] = ["All"] + cats
    category_combo.current(0)

def filter_by_category(event=None):
    cat = category_var.get()
    rows = fetch_products(category=cat)
    update_table(rows)

category_combo.bind("<<ComboboxSelected>>", filter_by_category)
populate_categories()

btn_show_all = tk.Button(search_frame, text="Show All", font=("Arial", 10, "bold"),
                         bg="#1b4f72", fg="white", width=12, command=lambda: update_table(fetch_products()))
btn_show_all.grid(row=1, column=0, columnspan=2, pady=8)

table_frame = tk.Frame(left_col)
table_frame.pack(fill=tk.BOTH, expand=True)

columns = ("ID", "Name", "Price", "Stock")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110, anchor=tk.W)
tree.pack(fill=tk.BOTH, expand=True)

def update_table(rows):
    tree.delete(*tree.get_children())
    for r in rows:
        tree.insert("", tk.END, values=r)

update_table(fetch_products())

# ------------------- MIDDLE COLUMN (Customer Details + Calculator + Cart) -------------------
# Header
heading = tk.Label(middle_col, text="Customer Details", font=("Arial", 16, "bold"),
                   bg="#1b4f72", fg="white", pady=6)
heading.pack(fill=tk.X, pady=(0,6))

# Customer inputs (Name, Contact)
cust_input_frame = tk.Frame(middle_col, bg="white")
cust_input_frame.pack(fill="x", padx=10, pady=(0,10))

tk.Label(cust_input_frame, text="Name", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=6)
cust_name_var = tk.StringVar()
cust_name = tk.Entry(cust_input_frame, textvariable=cust_name_var, width=28, font=("Arial", 12))
cust_name.grid(row=0, column=1, padx=6)

tk.Label(cust_input_frame, text="Contact No.", bg="white", font=("Arial", 12)).grid(row=0, column=2, sticky="w", padx=6)
cust_phone_var = tk.StringVar()
cust_phone = tk.Entry(cust_input_frame, textvariable=cust_phone_var, width=20, font=("Arial", 12))
cust_phone.grid(row=0, column=3, padx=6)

# Main middle frame
middle_frame = tk.Frame(middle_col, bg="white")
middle_frame.pack(padx=10, pady=0, fill="both", expand=True)

# Calculator
class Calculator:
    def __init__(self, display_label):
        self.expression = ""
        self.display = display_label

    def press(self, value):
        self.expression += str(value)
        self.display.config(text=self.expression)

    def clear(self):
        self.expression = ""
        self.display.config(text="0")

    def evaluate(self):
        try:
            result = str(eval(self.expression))
            self.display.config(text=result)
            self.expression = result
        except:
            self.display.config(text="Error")
            self.expression = ""

calc_frame = tk.LabelFrame(middle_frame, text="Calculator", font=("Arial", 12, "bold"), padx=12, pady=8)
calc_frame.grid(row=0, column=0, sticky="n", padx=(0,10))

display = tk.Label(calc_frame, text="0", font=("Arial", 18), bg="white", width=12, anchor="e")
display.grid(row=0, column=0, columnspan=4, pady=(0,8))
calculator = Calculator(display)

buttons = [
    ('7',1,0), ('8',1,1), ('9',1,2), ('+',1,3),
    ('4',2,0), ('5',2,1), ('6',2,2), ('-',2,3),
    ('1',3,0), ('2',3,1), ('3',3,2), ('*',3,3),
    ('Ans',4,0), ('Clear',4,1), ('0',4,2), ('/',4,3)
]
for (txt,r,c) in buttons:
    if txt == "Ans":
        cmd = calculator.evaluate
    elif txt == "Clear":
        cmd = calculator.clear
    else:
        cmd = lambda x=txt: calculator.press(x)
    tk.Button(calc_frame, text=txt, width=6, height=2, font=("Arial", 12), command=cmd).grid(row=r, column=c, padx=3, pady=3)

# Cart frame
cart_frame = tk.LabelFrame(middle_frame, text="My Cart   Total Products: 0", font=("Arial", 12, "bold"), padx=6, pady=6)
cart_frame.grid(row=0, column=1, sticky="n", padx=(0,10))

cart_tree = ttk.Treeview(cart_frame, columns=("ID","Name","Price","Qty"), show="headings", height=12)
for col in ("ID","Name","Price","Qty"):
    cart_tree.heading(col, text=col)
cart_tree.column("ID", width=40, anchor=tk.CENTER)
cart_tree.column("Name", width=170, anchor=tk.W)
cart_tree.column("Price", width=80, anchor=tk.E)
cart_tree.column("Qty", width=60, anchor=tk.CENTER)
cart_tree.pack(side="left", fill="both", expand=True)

cart_scroll = tk.Scrollbar(cart_frame, orient="vertical", command=cart_tree.yview)
cart_scroll.pack(side="right", fill="y")
cart_tree.configure(yscrollcommand=cart_scroll.set)

# Entry area (Product Name / Price / Quantity) and buttons
entry_frame = tk.Frame(middle_frame, bg="white", pady=6)
entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

tk.Label(entry_frame, text="Product Name", bg="white").grid(row=0, column=0, padx=6, sticky="w")
product_name_var = tk.StringVar()
product_name = tk.Entry(entry_frame, textvariable=product_name_var, width=28)
product_name.grid(row=1, column=0, padx=6)

tk.Label(entry_frame, text="Price", bg="white").grid(row=0, column=1, padx=6, sticky="w")
price_var = tk.StringVar()
price_entry = tk.Entry(entry_frame, textvariable=price_var, width=12)
price_entry.grid(row=1, column=1, padx=6)

tk.Label(entry_frame, text="Quantity", bg="white").grid(row=0, column=2, padx=6, sticky="w")
qty_var = tk.StringVar(value="1")
qty_entry = tk.Entry(entry_frame, textvariable=qty_var, width=8)
qty_entry.grid(row=1, column=2, padx=6)

stock_label_var = tk.StringVar(value="In stock: 0")
stock_label = tk.Label(entry_frame, textvariable=stock_label_var, bg="white")
stock_label.grid(row=2, column=0, pady=6, sticky="w", padx=6)

btn_clear = tk.Button(entry_frame, text="Clear", bg="#1b4f72", fg="white", width=12, command=lambda: clear_product_fields())
btn_clear.grid(row=1, column=3, padx=8)

btn_add_update = tk.Button(entry_frame, text="Add/Update Cart", bg="#1b4f72", fg="white", width=14, command=lambda: add_to_cart())
btn_add_update.grid(row=1, column=4, padx=8)

# Cart data structure
cart_items = {}   # pid -> [pid, name, price, qty]

selected_product_id = tk.StringVar()

def clear_product_fields():
    product_name_var.set("")
    price_var.set("")
    qty_var.set("1")
    stock_label_var.set("In stock: 0")
    selected_product_id.set("")

# When selecting a product from left table, fill product fields
def on_product_select(event):
    sel = tree.focus()
    if not sel:
        return
    pid, name, price, stock = tree.item(sel, "values")
    selected_product_id.set(str(pid))
    product_name_var.set(name)
    price_var.set(str(price))
    stock_label_var.set(f"In stock: {stock}")
    qty_var.set("1")

tree.bind("<ButtonRelease-1>", on_product_select)

def add_to_cart():
    name = product_name_var.get().strip()
    price = price_var.get().strip()
    qty = qty_var.get().strip()
    pid = selected_product_id.get()

    if not name or not price or not qty:
        messagebox.showerror("Error", "Please select product and enter quantity")
        return
    try:
        price_f = float(price)
        qty_i = int(qty)
        if qty_i <= 0: raise ValueError
    except:
        messagebox.showerror("Error", "Invalid price or quantity")
        return
    if not pid:
        # No product id from table: create a temporary unique id (negative to avoid conflict)
        pid = f"temp-{random.randint(10000,99999)}"
    # Add or update
    if pid in cart_items:
        cart_items[pid][3] += qty_i
    else:
        cart_items[pid] = [pid, name, price_f, qty_i]
    refresh_cart()
    clear_product_fields()

def refresh_cart():
    cart_tree.delete(*cart_tree.get_children())
    for item in cart_items.values():
        cart_tree.insert("", tk.END, values=item)
    cart_frame.config(text=f"My Cart   Total Products: {len(cart_items)}")
    update_bill_totals_preview()

def remove_selected_cart_item():
    sel = cart_tree.focus()
    if not sel:
        messagebox.showerror("Error", "Select item in cart to remove")
        return
    pid = cart_tree.item(sel, "values")[0]
    if pid in cart_items:
        del cart_items[pid]
    refresh_cart()

def update_qty_selected():
    sel = cart_tree.focus()
    if not sel:
        messagebox.showerror("Error", "Select item in cart to update")
        return
    pid = cart_tree.item(sel, "values")[0]
    try:
        new_q = int(qty_entry.get())
        if new_q <= 0: raise ValueError
    except:
        messagebox.showerror("Error", "Invalid quantity")
        return
    if pid in cart_items:
        cart_items[pid][3] = new_q
    refresh_cart()

# Buttons under cart
cart_btn_frame = tk.Frame(middle_frame, bg="white")
cart_btn_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")

tk.Button(cart_btn_frame, text="Remove Item", bg="#d9534f", fg="white", width=12, command=remove_selected_cart_item).pack(side="left", padx=6)
tk.Button(cart_btn_frame, text="Update Qty", bg="#1b4f72", fg="white", width=12, command=update_qty_selected).pack(side="left", padx=6)
tk.Button(cart_btn_frame, text="Clear Cart", bg="#777777", fg="white", width=12, command=lambda: clear_cart()).pack(side="left", padx=6)

def clear_cart():
    cart_items.clear()
    refresh_cart()
    clear_bill_area()

# ------------------- RIGHT COLUMN (Billing Area) -------------------
billing_title = tk.Label(right_col, text="Customer Billing Area", font=("Arial", 16, "bold"),
                         bg="#1b4f72", fg="white", pady=6)
billing_title.pack(fill=tk.X, pady=(0,6))

# Billing inner frame (white)
bill_frame = tk.Frame(right_col, bg="white", bd=2, relief="ridge")
bill_frame.pack(fill="both", padx=6, pady=(0,6), expand=False)

# Bill text (like the printed invoice)
bill_text = tk.Text(bill_frame, width=46, height=30, font=("Courier New", 10), padx=8, pady=8)
bill_text.pack(side="left", fill="both", expand=True)

bill_scroll = tk.Scrollbar(bill_frame, orient="vertical", command=bill_text.yview)
bill_scroll.pack(side="right", fill="y")
bill_text.configure(yscrollcommand=bill_scroll.set)

# Totals panel (three panels and buttons below)
totals_frame = tk.Frame(right_col, bg="white")
totals_frame.pack(fill="x", padx=6)

# Totals boxes
box_frame = tk.Frame(totals_frame, bg="white")
box_frame.pack(pady=6)

bill_amount_var = tk.StringVar(value="0.00")
discount_var = tk.StringVar(value=f"{DISCOUNT_PERCENT}%")
net_pay_var = tk.StringVar(value="0.00")

def make_totals_box(parent, title, val_var):
    f = tk.Frame(parent, bg="#2f5a6f", padx=8, pady=10)
    f.pack(side="left", padx=6)
    tk.Label(f, text=title, bg="#2f5a6f", fg="white", font=("Arial", 10)).pack()
    tk.Label(f, textvariable=val_var, bg="#2f5a6f", fg="white", font=("Arial", 12, "bold")).pack()
    return f

make_totals_box(box_frame, "Bill Amount (Rs.)", bill_amount_var)
make_totals_box(box_frame, "Discount", discount_var)
make_totals_box(box_frame, "Net Pay (Rs.)", net_pay_var)

# Buttons under totals
btns_frame = tk.Frame(totals_frame, bg="white")
btns_frame.pack(pady=6, fill="x")

def generate_bill():
    if not cust_name_var.get().strip():
        messagebox.showerror("Error", "Please enter customer name")
        return
    if not cart_items:
        messagebox.showerror("Error", "Cart is empty")
        return

    # Prepare bill header
    bill_text.delete("1.0", tk.END)
    shop_name = "StockApp-Inventory"
    shop_phone = "Phone No. 7905112734, Lucknow,226026"
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    bill_no = random.randint(10000000, 99999999)

    lines = []
    lines.append(f"{shop_name:^42}")
    lines.append(f"{shop_phone:^42}")
    lines.append("="*42)
    lines.append(f"Customer Name: {cust_name_var.get():<18}    Date: {date_str}")
    lines.append(f"Phone no: {cust_phone_var.get():<20}  Bill no: {bill_no}")
    lines.append("="*42)
    lines.append(f"{'Product Name':<22}{'Qty':>6}{'Price':>12}")
    lines.append("-"*42)

    total = 0.0
    for item in cart_items.values():
        name = item[1]
        price = float(item[2])
        qty = int(item[3])
        line_price = price * qty
        total += line_price
        # truncate name if too long
        name_display = (name[:20] + '..') if len(name) > 22 else name
        lines.append(f"{name_display:<22}{qty:>6}{line_price:>12.2f}")

    lines.append("-"*42)
    bill_amount = total
    discount_amount = (DISCOUNT_PERCENT/100.0) * bill_amount
    net_pay = bill_amount - discount_amount

    lines.append(f"{'Bill Amount':<26}{'Rs.':>3}{bill_amount:>11.2f}")
    lines.append(f"{'Discount':<26}{'Rs.':>3}{discount_amount:>11.2f}")
    lines.append(f"{'Net Pay':<26}{'Rs.':>3}{net_pay:>11.2f}")
    lines.append("="*42)

    bill_text.insert(tk.END, "\n".join(lines))

    # Update totals labels
    bill_amount_var.set(f"{bill_amount:.2f}")
    net_pay_var.set(f"{net_pay:.2f}")

def print_bill():
    # Allow saving the bill to a file (txt) which user can print later
    bill_content = bill_text.get("1.0", tk.END).strip()
    if not bill_content:
        messagebox.showerror("Error", "No bill to print. Generate a bill first.")
        return
    fname = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text files","*.txt"),("All files","*.*")],
                                         title="Save Bill As")
    if not fname:
        return
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(bill_content)
        messagebox.showinfo("Saved", f"Bill saved to {fname}\nYou can print it from your OS.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save bill: {e}")

def clear_bill_area():
    bill_text.delete("1.0", tk.END)
    bill_amount_var.set("0.00")
    net_pay_var.set("0.00")
    discount_var.set(f"{DISCOUNT_PERCENT}%")

tk.Button(btns_frame, text="Generate Bill", bg="#1b4f72", fg="white", width=14, command=generate_bill).pack(side="left", padx=8)
tk.Button(btns_frame, text="Print", bg="#1b4f72", fg="white", width=14, command=print_bill).pack(side="left", padx=8)
tk.Button(btns_frame, text="Clear All", bg="#777777", fg="white", width=14, command=lambda: (clear_cart(), clear_bill_area())).pack(side="left", padx=8)

# ------------------- Hook product table selection to auto-fill price/stock in middle (improve UX) -------------------
def populate_product_from_tree(event):
    sel = tree.focus()
    if not sel:
        return
    pid, name, price, stock = tree.item(sel, "values")
    selected_product_id.set(str(pid))
    product_name_var.set(name)
    price_var.set(str(price))
    stock_label_var.set(f"In stock: {stock}")
    qty_var.set("1")

tree.bind("<Double-1>", populate_product_from_tree)

# ------------------- Misc helpers: preview totals when cart changes -------------------
def update_bill_totals_preview():
    total = 0.0
    for item in cart_items.values():
        price = float(item[2])
        qty = int(item[3])
        total += price * qty
    discount_amount = (DISCOUNT_PERCENT/100.0) * total
    net = total - discount_amount
    bill_amount_var.set(f"{total:.2f}")
    net_pay_var.set(f"{net:.2f}")

# ------------------- Finally: run mainloop -------------------
root.mainloop()

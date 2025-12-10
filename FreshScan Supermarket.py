from tkinter import *
from tkinter import ttk, messagebox
import sqlite3, datetime, random



# ================= OPEN SUPERMARKET WINDOW =================
def open_supermarket():
    global root, product_tree, cust_name, cust_phone, cart_tree, cart_items, selected_pid
    global prod_name, prod_price, prod_qty, stock_lbl, bill_text, bill_amt, discount, net_pay

    root = Tk()        
    root.title("Freshscan Supermarket System")
    root.state("zoomed")
    root.configure(bg="white")


    # -------- DB Fetch ----------
    def fetch_products(name=None):
        con = sqlite3.connect("supermarket.db")
        cur = con.cursor()
        if name:
            cur.execute("SELECT id, name, price, stock FROM products WHERE name LIKE ?", (f"%{name}%",))
        else:
            cur.execute("SELECT id, name, price, stock FROM products")
        rows = cur.fetchall()
        con.close()
        return rows

    def update_table(rows):
        product_tree.delete(*product_tree.get_children())
        for row in rows:
            product_tree.insert("", END, values=row)

    # ===== FIXED WIDTHS  =====
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    left_w  = int(screen_w * 0.28)     
    mid_w   = int(screen_w * 0.45)      
    right_w = int(screen_w * 0.27)      

    # ---------------- LEFT PANEL ----------------
    left = Frame(root, bg="white", bd=2, relief="ridge")
    left.place(x=0, y=0, width=left_w, height=screen_h)

    Label(left, text="All Products", font=("Arial", 20, "bold"),
          bg="#1b4f72", fg="white").place(x=0, y=0, width=left_w)

    Label(left, text="Product Name", bg="white", font=("Arial", 12)).place(x=12, y=55)
    product_search = Entry(left, font=("Arial", 12), width=20)
    product_search.place(x=135, y=55)

    def search_item(): update_table(fetch_products(product_search.get()))
    def show_all(): update_table(fetch_products())

    Button(left, text="Search", bg="#1b4f72", fg="white", width=10,
           command=search_item).place(x=60, y=92)
    Button(left, text="Show All", bg="#1b4f72", fg="white", width=10,
           command=show_all).place(x=180, y=92)

    product_tree = ttk.Treeview(left, columns=("ID","Name","Price","Stock"), show="headings", height=30)
    product_tree.heading("ID", text="ID"); product_tree.column("ID", width=50, anchor=CENTER)
    product_tree.heading("Name", text="Name"); product_tree.column("Name", width=170, anchor=W)
    product_tree.heading("Price", text="Price"); product_tree.column("Price", width=70, anchor=CENTER)
    product_tree.heading("Stock", text="Stock"); product_tree.column("Stock", width=60, anchor=CENTER)
    product_tree.place(x=8, y=140, width=left_w-16, height=screen_h-160)

    update_table(fetch_products())

    # ---------------- MIDDLE PANEL ----------------
    mid = Frame(root, bg="white", bd=2, relief="ridge")
    mid.place(x=left_w, y=0, width=mid_w, height=screen_h)

    Label(mid, text="Customer Details", font=("Arial", 20, "bold"),
          bg="#1b4f72", fg="white").place(x=0, y=0, width=mid_w)

    cust_name = StringVar()
    cust_phone = StringVar()

    Label(mid, text="Name", bg="white", font=("Arial", 12)).place(x=20, y=55)
    Entry(mid, textvariable=cust_name, font=("Arial", 12), width=23).place(x=85, y=55)

    Label(mid, text="Contact No.", bg="white", font=("Arial", 12)).place(x=295, y=55)
    Entry(mid, textvariable=cust_phone, font=("Arial", 12), width=20).place(x=385, y=55)

    # ------- Calculator -------
    Label(mid, text="Calculator", bg="white", font=("Arial", 13, "bold")).place(x=35, y=115)
    calc_display = Entry(mid, font=("Arial", 19), bd=3, relief="sunken", justify="right")
    calc_display.place(x=20, y=150, width=255, height=55)

    class Calc:
        exp = ""

    def press(x):
        Calc.exp += str(x); calc_display.delete(0, END); calc_display.insert(0, Calc.exp)

    def clear():
        Calc.exp = ""; calc_display.delete(0, END)

    def equal():
        try:
            Calc.exp = str(eval(Calc.exp))
            calc_display.delete(0, END); calc_display.insert(0, Calc.exp)
        except:
            clear(); calc_display.insert(0, "Err")

    calc_btns = [['7','8','9','+'], ['4','5','6','-'], ['1','2','3','*'], ['Ans','Clear','0','/']]
    bx, by = 20, 225
    for row in calc_btns:
        x_temp = bx
        for val in row:
            if val == "Ans": cmd = equal
            elif val == "Clear": cmd = clear
            else: cmd = lambda key=val: press(key)
            Button(mid, text=val, font=("Arial", 11), width=5, height=2,
                   bg="#E0E0E0", command=cmd).place(x=x_temp, y=by)
            x_temp += 58
        by += 60

    # ------- Cart -------
    Label(mid, text="My Cart", bg="white", font=("Arial", 13, "bold")).place(x=320, y=115)
    total_prod_lbl = Label(mid, text="Total Products: 0", bg="white", font=("Arial", 11, "bold"))
    total_prod_lbl.place(x=400, y=115)

    cart_tree = ttk.Treeview(mid, columns=("ID","Name","Price","Qty"), show="headings")
    cart_tree.heading("ID", text="ID"); cart_tree.column("ID", width=40, anchor=CENTER)
    cart_tree.heading("Name", text="Name"); cart_tree.column("Name", width=155, anchor=W)
    cart_tree.heading("Price", text="Price"); cart_tree.column("Price", width=70, anchor=CENTER)
    cart_tree.heading("Qty", text="Qty"); cart_tree.column("Qty", width=55, anchor=CENTER)

    cart_tree.place(x=300, y=150, width=mid_w-310, height=310)

    # ------- Product Input -------
    Label(mid, text="Product Name", bg="white", font=("Arial", 12)).place(x=20, y=515)
    Label(mid, text="Price", bg="white", font=("Arial", 12)).place(x=245, y=515)
    Label(mid, text="Quantity", bg="white", font=("Arial", 12)).place(x=350, y=515)

    prod_name = Entry(mid, width=20)
    prod_price = Entry(mid, width=10)
    prod_qty = Entry(mid, width=7)
    prod_name.place(x=20, y=540)
    prod_price.place(x=235, y=540)
    prod_qty.place(x=350, y=540)

    stock_lbl = Label(mid, text="In stock: 0", bg="white", font=("Arial", 11, "bold"))
    stock_lbl.place(x=20, y=570)

    cart_items = {}
    selected_pid = None

    def on_select(event):
        global selected_pid
        sel = product_tree.focus()
        if not sel: return
        pid, name, price, stock = product_tree.item(sel,"values")
        selected_pid = pid
        prod_name.delete(0, END); prod_name.insert(0, name)
        prod_price.delete(0, END); prod_price.insert(0, price)
        prod_qty.delete(0, END); prod_qty.insert(0, "1")
        stock_lbl.config(text=f"In stock: {stock}")

    product_tree.bind("<ButtonRelease-1>", on_select)

    def refresh_cart():
        cart_tree.delete(*cart_tree.get_children())
        for item in cart_items.values(): cart_tree.insert("", END, values=item)
        total_prod_lbl.config(text=f"Total Products: {len(cart_items)}")
        update_totals()

    def add_cart():
        if not selected_pid: return messagebox.showerror("Error","Select product first")
        pid = selected_pid
        name = prod_name.get()
        price = float(prod_price.get())
        qty = int(prod_qty.get())
        con = sqlite3.connect("supermarket.db"); cur = con.cursor()
        cur.execute("SELECT stock FROM products WHERE id=?", (pid,))
        stock = cur.fetchone()[0]; con.close()
        if qty > stock: return messagebox.showerror("Error","Not enough stock")
        cart_items[pid] = [pid,name,price,qty]; refresh_cart()

    def update_qty():
        sel = cart_tree.focus()
        if not sel: return messagebox.showerror("Error","Select item")
        pid = cart_tree.item(sel,"values")[0]
        cart_items[pid][3] = int(prod_qty.get()); refresh_cart()

    Button(mid, text="Clear", width=12, bg="#1b4f72", fg="white",
           command=lambda:(prod_name.delete(0,END), prod_price.delete(0,END), prod_qty.delete(0,END))).place(x=40, y=615)

    Button(mid, text="Add/Update Cart", width=15, bg="#1b4f72", fg="white",
           command=add_cart).place(x=175, y=615)

    Button(mid, text="Update Qty", width=12, bg="#1b4f72", fg="white",
           command=update_qty).place(x=345, y=615)
    # ---------------- RIGHT PANEL ----------------
    right = Frame(root, bg="white", bd=2, relief="ridge")
    right.place(x=left_w + mid_w, y=0, width=right_w, height=screen_h)

    Label(right, text="Customer Billing Area", font=("Arial", 20, "bold"),
          bg="#1b4f72", fg="white").place(x=0, y=0, width=right_w)

    bill_text = Text(right, font=("Courier New", 10))
    bill_text.place(x=10, y=55, width=right_w-20, height=500)

    bill_amt = StringVar(value="0.00")
    discount = StringVar(value="5%")
    net_pay = StringVar(value="0.00")

    def update_totals():
        total = sum(i[2] * i[3] for i in cart_items.values())
        bill_amt.set(f"{total:.2f}")
        net_pay.set(f"{total - total*0.05:.2f}")

    def generate_bill():
        if not cart_items: return messagebox.showerror("Error","Cart empty")
        if not cust_name.get() or not cust_phone.get(): return messagebox.showerror("Error","Enter details first")

        bill_text.delete("1.0", END)
        bill_text.insert(END, f"{'Freshscan Supermarket':^55}\n")
        bill_text.insert(END, "="*48 + "\n")

        bill_no = random.randint(10000000,99999999)
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        total = 0

        bill_text.insert(END, f"Name : {cust_name.get()}\n")
        bill_text.insert(END, f"Phone: {cust_phone.get()}     Date: {date}\n")
        bill_text.insert(END, f"Bill#: {bill_no}\n")
        bill_text.insert(END, "-"*48 + "\n")
        bill_text.insert(END, f"{'Product':<18}{'Qty':>7}{'Amount':>15}\n")
        bill_text.insert(END, "-"*48 + "\n")

        con = sqlite3.connect("supermarket.db")
        cur = con.cursor()
        for pid,name,price,qty in cart_items.values():
            amt = price * qty; total += amt
            bill_text.insert(END, f"{name[:16]:<18}{qty:>7}{amt:>15.2f}\n")
            cur.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty,pid))
        con.commit(); con.close()

        disc = total * 0.05; net = total - disc
        bill_text.insert(END, "-"*48 + "\n")
        bill_text.insert(END, f"Bill Amount: Rs {total:.2f}\n")
        bill_text.insert(END, f"Discount   : Rs {disc:.2f}\n")
        bill_text.insert(END, f"Net Pay    : Rs {net:.2f}\n")
        bill_text.insert(END, "="*48)

        update_table(fetch_products())
        cart_items.clear(); refresh_cart()

    # ---- Summary Boxes ----
    def box(x, text, var):
        frame = Frame(right, bg="#2f5a6f")
        frame.place(x=x, y=570, width=right_w/3 - 12, height=60)
        Label(frame, text=text, bg="#2f5a6f", fg="white").pack()
        Label(frame, textvariable=var, font=("Arial", 12, "bold"),
              bg="#2f5a6f", fg="white").pack()

    box(5, "Bill Amount (Rs)", bill_amt)
    box(right_w/3 + 5, "Discount", discount)
    box((right_w/3) * 2 + 5, "Net Pay (Rs)", net_pay)

    # ---- Big Bottom Buttons ----
    Button(right, text="Generate Bill", font=("Arial", 12, "bold"),
           bg="#1b4f72", fg="white", command=generate_bill).place(
           x=10, y=645, width=right_w/3 - 20, height=55)

    Button(right, text="Print", font=("Arial", 12, "bold"),
           bg="#1b4f72", fg="white",
           command=lambda: messagebox.showinfo("Saved","Bill Saved")).place(
           x=right_w/3 + 10, y=645, width=right_w/3 - 20, height=55)

    Button(right, text="Clear All", font=("Arial", 12, "bold"),
           bg="#1b4f72", fg="white", command=lambda: bill_text.delete("1.0", END)).place(
           x=(right_w/3)*2 + 10, y=645, width=right_w/3 - 20, height=55)

# ================= LOGIN WINDOW =================
def getin():
    username = entry_1.get()
    password = entry_2.get()
    if username == '' and password == '':
        messagebox.showerror('login', 'Blanks are not allowed')
    elif username == 'admin' and password == 'abcd':
        messagebox.showinfo('login', 'Login Accessed')
        login.destroy()
        open_supermarket()
    else:
        messagebox.showerror('login', 'Invalid username or password')

login = Tk()
login.title("Login")
login.state("zoomed")
login.config(bg="#FDF5E6")

heading = Label(login, text="USER LOGIN", font=("Arial",50,"bold"), fg="#3F51B5", bg="#FDF5E6")
heading.place(relx=0.36)

icon = PhotoImage(file="C:\\Users\\HP\\Desktop\\jackfruit problem\\Freshscan Logo.png")
Label(login, image=icon).place(relx=0.36, rely=0.2)

Label(login, text="USERNAME : ", font=("Arial",20,"bold"), fg="#3F51B5", bg="#FDF5E6").place(relx=0.2, rely=0.48)
entry_1 = Entry(login, font=('Arial',26), fg="#004D40", bg="#FFFFE0",
                highlightbackground="#FF9800", highlightthickness=2, bd=0)
entry_1.place(relx=0.33, rely=0.475)

Label(login, text="PASSWORD : ", font=("Arial",20,"bold"), fg="#3F51B5", bg="#FDF5E6").place(relx=0.2, rely=0.635)
entry_2 = Entry(login, font=("Arial",26), fg="#004D40", show="*", bg="#FFFFE0",
                highlightbackground="#FF9800", highlightthickness=2, bd=0)
entry_2.place(relx=0.33, rely=0.63)

Button(login, text='LOGIN', font=('Arial',30), command=getin,
       bg="#E91E63", fg="white").place(relx=0.42, rely=0.84)

login.mainloop()
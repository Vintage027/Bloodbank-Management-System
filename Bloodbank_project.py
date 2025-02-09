import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Initialization
def init_db():
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()

    # Create Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        contact TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL
    )
    ''')

    # Default Admin
    cursor.execute('INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)', ('admin', 'password123'))
    conn.commit()
    conn.close()

# Admin Login Functionality
def admin_login(username, password):
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

# Get donor count
def get_donor_count():
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM donors')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Get donor distribution by blood group
def get_donor_distribution():
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group')
    data = cursor.fetchall()
    conn.close()
    return data

# Register Donor
def register_donor(name, age, blood_group, contact, address):
    try:
        age = int(age)
        if age <= 18:
            messagebox.showerror("Error", "Age must be above 18.")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid age. Please enter a numeric value.")
        return

    if not contact.isdigit() or len(contact) != 10:
        messagebox.showerror("Error", "Contact must be exactly 10 digits.")
        return

    if not (address.isdigit() and len(address) == 6):
        messagebox.showerror("Error", "Address must be a valid 6-digit pincode.")
        return

    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO donors (name, age, blood_group, contact, address) VALUES (?, ?, ?, ?, ?)
        ''', (name, age, blood_group, contact, address))
        conn.commit()
        messagebox.showinfo("Success", "Donor registered successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Contact number already exists!")
    conn.close()

# Search Donor
def search_donor(blood_group=None, address=None):
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    if blood_group and address:
        cursor.execute('SELECT * FROM donors WHERE blood_group = ? AND address = ?', (blood_group, address))
    elif blood_group:
        cursor.execute('SELECT * FROM donors WHERE blood_group = ?', (blood_group,))
    elif address:
        cursor.execute('SELECT * FROM donors WHERE address = ?', (address,))
    else:
        cursor.execute('SELECT * FROM donors')
    donors = cursor.fetchall()
    conn.close()
    return donors


# Function to display Age chart (Pie chart)
def display_age_chart():
    graph_window = Toplevel()
    graph_window.title("Statistical Data - Age Distribution")
    graph_window.configure(bg="#f2f2f2")

    # Age Group Data (Sample data, replace with actual data)
    age_groups = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    age_counts = [50, 80, 40, 30, 20]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(age_counts, labels=age_groups, autopct='%1.1f%%', colors=['#FF6347', '#FF4500', '#FFD700', '#FF8C00', '#FF7F50'])
    ax.set_title("Donor Distribution by Age Group")

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

# Function to display Bar Graph (Age Group Distribution)
def display_bar_graph():
    graph_window = Toplevel()
    graph_window.title("Statistical Data - Age Group Distribution")
    graph_window.configure(bg="#f2f2f2")

    # Age Group Data (Dynamic Data based on the donor's age)
    age_groups = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    age_counts = [0, 0, 0, 0, 0]  # Counts for each age group

    # Query to get all donors' age data
    conn = sqlite3.connect('bloodbank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT age FROM donors')
    donors_ages = cursor.fetchall()
    conn.close()

    # Counting donors for each age group
    for age in donors_ages:
        # Ensure age is an integer before comparison
        age = int(age[0])  # Convert to int
        if 18 <= age <= 25:
            age_counts[0] += 1
        elif 26 <= age <= 35:
            age_counts[1] += 1
        elif 36 <= age <= 45:
            age_counts[2] += 1
        elif 46 <= age <= 55:
            age_counts[3] += 1
        elif 56 <= age <= 65:
            age_counts[4] += 1

    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(6, 6))
    bars = ax.bar(age_groups, age_counts, color='lightgreen')

    # Add labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, str(height), ha='center', va='bottom')

    ax.set_title("Donor Distribution by Age Group")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Number of Donors")

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)


# Admin Dashboard Update (adding dropdown menu)
def admin_window():
    login_window.destroy()

    # Admin Functions Window
    admin = Toplevel()
    admin.title("Admin Dashboard")
    admin.configure(bg="#f2f2f2")

    def toggle_fullscreen(event=None):
        admin.attributes('-fullscreen', not admin.attributes('-fullscreen'))

    admin.bind("<Escape>", toggle_fullscreen)
    admin.attributes('-fullscreen', True)

    # Main Layout (Centering content)
    main_frame = Frame(admin, bg="#f2f2f2")
    main_frame.pack(fill=BOTH, expand=True)

    # Center frame for content
    center_frame = Frame(main_frame, bg="#f2f2f2")
    center_frame.place(relx=0.5, rely=0.5, anchor=CENTER)  # Centering the content frame

    # Header Label
    Label(center_frame, text="BLOOD BANK MANAGEMENT SYSTEM", font=("Helvetica", 30, "bold"), bg="#f2f2f2").pack(pady=20)

    # Donors Registered Section
    donor_count = get_donor_count()
    Label(center_frame, text=f"Donors Registered: {donor_count}", font=("Helvetica", 16), bg="#f2f2f2").pack(pady=20)

    # Register Donor Section
    Label(center_frame, text="Register Donor", font=("Helvetica", 16, "bold"), bg="#f2f2f2").pack(pady=10)
    frame_register = Frame(center_frame, bg="#f2f2f2")
    frame_register.pack(pady=10)

    # Register donor form fields
    Label(frame_register, text="Name", bg="#f2f2f2").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    entry_name = ttk.Entry(frame_register)
    entry_name.grid(row=0, column=1, padx=10, pady=5)

    Label(frame_register, text="Age", bg="#f2f2f2").grid(row=1, column=0, sticky=W, padx=10, pady=5)
    entry_age = ttk.Entry(frame_register)
    entry_age.grid(row=1, column=1, padx=10, pady=5)

    Label(frame_register, text="Blood Group", bg="#f2f2f2").grid(row=2, column=0, sticky=W, padx=10, pady=5)
    blood_group_options = ["A +", "A -", "B +", "B -", "AB +", "AB -", "O +", "O -"]
    selected_blood_group = StringVar()
    blood_group_dropdown = ttk.Combobox(frame_register, textvariable=selected_blood_group, values=blood_group_options, state="readonly")
    blood_group_dropdown.grid(row=2, column=1, padx=10, pady=5)

    Label(frame_register, text="Contact", bg="#f2f2f2").grid(row=3, column=0, sticky=W, padx=10, pady=5)
    entry_contact = ttk.Entry(frame_register)
    entry_contact.grid(row=3, column=1, padx=10, pady=5)

    Label(frame_register, text="Pincode", bg="#f2f2f2").grid(row=4, column=0, sticky=W, padx=10, pady=5)
    entry_address = ttk.Entry(frame_register)
    entry_address.grid(row=4, column=1, padx=10, pady=5)

    ttk.Button(frame_register, text="Register", command=lambda: register_donor(
        entry_name.get(), entry_age.get(), selected_blood_group.get(),
        entry_contact.get(), entry_address.get())
    ).grid(row=5, column=1, pady=10)

    # Search Donor Section
    Label(center_frame, text="Search Donor", font=("Helvetica", 16, "bold"), bg="#f2f2f2").pack(pady=10)
    frame_search = Frame(center_frame, bg="#f2f2f2")
    frame_search.pack(pady=10)

    Label(frame_search, text="Blood Group", bg="#f2f2f2").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    selected_search_blood_group = StringVar()
    blood_group_search_dropdown = ttk.Combobox(frame_search, textvariable=selected_search_blood_group, values=blood_group_options, state="readonly")
    blood_group_search_dropdown.grid(row=0, column=1, padx=10, pady=5)

    Label(frame_search, text="Pincode", bg="#f2f2f2").grid(row=1, column=0, sticky=W, padx=10, pady=5)
    entry_search_address = ttk.Entry(frame_search)
    entry_search_address.grid(row=1, column=1, padx=10, pady=5)

    def search():
        blood_group = selected_search_blood_group.get()
        address = entry_search_address.get()
        results = search_donor(blood_group=blood_group, address=address)
        result_window = Toplevel()
        result_window.title("Search Results")
        result_window.configure(bg="#f2f2f2")
        Label(result_window, text="Donors Found:", font=("Helvetica", 14, "bold"), bg="#f2f2f2").pack(pady=10)
        for donor in results:
            Label(result_window, text=f"Name: {donor[1]}, Age: {donor[2]}, Blood Group: {donor[3]}, Contact: {donor[4]}, Address: {donor[5]}", bg="#f2f2f2").pack(pady=5)

    ttk.Button(frame_search, text="Search", command=search).grid(row=2, column=1, pady=10)

    # Data Visualization Section
    Label(center_frame, text="Data Visualization", font=("Helvetica", 16, "bold"), bg="#f2f2f2").pack(pady=10)

    def show_graph():
        selected_graph = graph_choice.get()
        if selected_graph == "Blood group distribution":
            display_bar_graph()
        elif selected_graph == "Age chart":
            display_age_chart()

    graph_choice = StringVar()
    graph_choice.set("Blood group distribution")

    graph_dropdown = ttk.Combobox(center_frame, textvariable=graph_choice, values=["Blood group distribution", "Age chart"], state="readonly")
    graph_dropdown.pack(pady=10)

    ttk.Button(center_frame, text="Show Graph", command=show_graph).pack(pady=10)

# Main GUI (Unchanged)
init_db()
login_window = Tk()
login_window.title("Blood Bank Admin Login")
login_window.attributes('-fullscreen', True)
login_window.configure(bg="#f2f2f2")

Label(login_window, text="Admin Login", font=("Helvetica", 20, "bold"), bg="#f2f2f2").pack(pady=20)

frame_login = Frame(login_window, bg="#f2f2f2")
frame_login.pack(pady=20)

Label(frame_login, text="Username", bg="#f2f2f2").grid(row=0, column=0, padx=10, pady=10, sticky=E)
entry_username = ttk.Entry(frame_login)
entry_username.grid(row=0, column=1, padx=10, pady=10)

Label(frame_login, text="Password", bg="#f2f2f2").grid(row=1, column=0, padx=10, pady=10, sticky=E)
entry_password = ttk.Entry(frame_login, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)

def login():
    username = entry_username.get()
    password = entry_password.get()
    if admin_login(username, password):
        admin_window()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

ttk.Button(frame_login, text="Login", command=login).grid(row=2, column=1, pady=10)

login_window.mainloop()







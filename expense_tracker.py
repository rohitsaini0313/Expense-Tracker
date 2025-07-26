import sqlite3
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

# --- Database Functions (Backend) ---

def initialize_db():
    """Initializes the database and the expenses table if it doesn't exist."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(description, amount, category):
    """Adds a new transaction to the database."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    today_date = date.today().strftime("%Y-%m-%d")
    # The INSERT statement needs 4 values
    cursor.execute(
        "INSERT INTO expenses (transaction_date, description, amount, category) VALUES (?, ?, ?, ?)",
        (today_date, description, amount, category)
    )
    conn.commit()
    conn.close()

def get_all_transactions():
    """Fetches all transactions from the database, ordered by date."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, transaction_date, description, amount, category FROM expenses ORDER BY transaction_date DESC")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def delete_transaction(transaction_id):
    """Deletes a transaction from the database by its ID."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

def calculate_totals():
    """Calculates total income, total expenses, and the current balance."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # Calculate total income (positive amounts)
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE amount > 0")
    total_income = cursor.fetchone()[0] or 0.0
    
    # Calculate total expenses (negative amounts)
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE amount < 0")
    total_expenses = cursor.fetchone()[0] or 0.0

    conn.close()

    balance = total_income + total_expenses # total_expenses is already negative
    return {
       "income": total_income,
       "expenses": abs(total_expenses),
       "balance": balance
    }

# --- GUI Class (Frontend) ---

class ExpenseTrackerApp:
    def __init__(self, root):
      self.root = root
      self.root.title("Personal Expense Tracker")
      self.root.geometry("850x600")
      
      # --- Frames ---
      dashboard_frame = tk.Frame(root, padx=10, pady=10)
      dashboard_frame.pack(fill="x")
     
      input_frame = tk.Frame(root, padx=10, pady=10)
      input_frame.pack(fill="x")

      history_frame = tk.Frame(root, padx=10, pady=10)
      history_frame.pack(fill="both", expand=True)
      
      # --- Dashboard Widgets ---
      self.income_label = tk.Label(dashboard_frame, text="Income: $0.00", font=("Helvetica", 14), fg="green")
      self.income_label.pack(side="left", expand=True)
      
      self.expense_label = tk.Label(dashboard_frame, text="Expense: $0.00", font=("Helvetica", 14), fg="red")
      self.expense_label.pack(side="left", expand=True)
      
      self.balance_label = tk.Label(dashboard_frame, text="Balance: $0.00", font=("Helvetica", 14), fg="blue")
      self.balance_label.pack(side="left", expand=True)
    
      # --- Input Widgets ---
      tk.Label(input_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
      self.desc_entry = tk.Entry(input_frame, width=30)
      self.desc_entry.grid(row=0, column=1, padx=5, pady=5)
       
      tk.Label(input_frame, text="Amount (use '-' for expense):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
      self.amount_entry = tk.Entry(input_frame, width=15)
      self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
      tk.Label(input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
      self.categories = ["Income", "Food", "Transport", "Shopping", "Bills", "Entertainment", "Others"]
      self.category_var = tk.StringVar(root)
      self.category_var.set(self.categories[1]) # Default value
      self.category_menu = tk.OptionMenu(input_frame, self.category_var, *self.categories)
      self.category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

      self.add_button = tk.Button(input_frame, text="Add Transaction", command=self.handle_add_transaction)
      self.add_button.grid(row=1, column=3, padx=5, pady=5)

      # --- History Widgets ---
      self.tree = ttk.Treeview(history_frame, columns=("ID", "Date", "Description", "Amount", "Category"), show="headings")
      self.tree.heading("ID", text="ID")
      self.tree.heading("Date", text="Date")
      self.tree.heading("Description", text="Description")
      self.tree.heading("Amount", text="Amount")
      self.tree.heading("Category", text="Category")
        
      self.tree.column("ID", width=40, anchor="center")
      self.tree.column("Amount", width=100, anchor="e") # Right-align amount
      self.tree.column("Description", width=250)
        
      self.tree.pack(side="left", fill="both", expand=True)
        
      scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
      self.tree.configure(yscrollcommand=scrollbar.set)
      scrollbar.pack(side="right", fill="y")
        
      self.delete_button = tk.Button(history_frame, text="Delete Selected", command=self.handle_delete_transaction, bg="red", fg="white")
      self.delete_button.pack(pady=10)

      # Initial UI Update
      self.refresh_ui()

    def handle_add_transaction(self):
        desc = self.desc_entry.get()
        amount_str = self.amount_entry.get()
        category = self.category_var.get()

        if not desc or not amount_str:
            messagebox.showerror("Error", "Description and Amount are required.")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        add_transaction(desc, amount, category)
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.refresh_ui()  

    def handle_delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a transaction to delete.")
            return

        # Get the transaction ID from the first column of the selected row
        transaction_id = self.tree.item(selected_item[0])['values'][0]
        delete_transaction(transaction_id)
        self.refresh_ui()

    def refresh_ui(self):
        # Update dashboard
        totals = calculate_totals()
        self.income_label.config(text=f"Income: ${totals['income']:.2f}")
        self.expense_label.config(text=f"Expenses: ${totals['expenses']:.2f}")
        self.balance_label.config(text=f"Balance: ${totals['balance']:.2f}")

        # Update transaction list (Treeview)
        # First, clear the existing items in the tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Then, fetch and insert the updated transactions
        transactions = get_all_transactions()
        for t in transactions:
            self.tree.insert("", "end", values=t)

# --- Main Execution Block ---

if __name__ == "__main__":
    # This runs once when the application starts
    initialize_db()

    # Create the main window and start the app
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
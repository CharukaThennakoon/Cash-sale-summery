import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# --- 1. Database Setup (දත්ත සමුදාය සකස් කිරීම) ---
def setup_db():
    conn = sqlite3.connect("distribution.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS credit_bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area TEXT,
                        bill_name TEXT,
                        bill_number TEXT,
                        amount_due REAL)''')
    conn.commit()
    conn.close()


# --- 2. Main Application GUI Setup ---
class CashSaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CASH SALE MANAGEMENT SYSTEM")
        self.root.geometry("850x670")

        # අද දවසේ එකතුවන් තබා ගැනීමට
        self.current_collection = 0.0

        # අද ලැබුණු මුදල තාවකාලිකව පෙන්වීමට භාවිත කරන dictionary එක (Database එකට සේව් නොවේ)
        self.session_received = {}

        # ප්‍රධාන මාතෘකාව
        tk.Label(root, text="CASH SALE", font=("Arial", 22, "bold"), fg="#2c3e50").pack(pady=15)

        # -----------------------------------------------------------
        # කොටස 1: අද දවසේ ලැබිච්ච මුළු මුදල ඇතුලත් කරන ස්ථානය
        # -----------------------------------------------------------
        frame_total_cash = tk.LabelFrame(root, text=" 1. Cash Input ", font=("Arial", 11, "bold"), padx=10, pady=10)
        frame_total_cash.pack(pady=10, fill="x", padx=40)

        tk.Label(frame_total_cash, text="Today Total Cash (Rs):", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.entry_total_cash = tk.Entry(frame_total_cash, font=("Arial", 12), width=20)
        self.entry_total_cash.pack(side=tk.LEFT, padx=10)

        # -----------------------------------------------------------
        # කොටස 2: ප්‍රදේශය තෝරා ගැනීම සහ වගුව
        # -----------------------------------------------------------
        frame_area = tk.LabelFrame(root, text=" 2. Credit Bills Management ", font=("Arial", 11, "bold"), padx=10,
                                   pady=10)
        frame_area.pack(pady=10, fill="both", expand=True, padx=40)

        # ප්‍රදේශය තේරීම
        inner_frame_top = tk.Frame(frame_area)
        inner_frame_top.pack(fill="x", pady=5)

        tk.Label(inner_frame_top, text="Select Area:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.area_var = tk.StringVar()
        self.combo_area = ttk.Combobox(inner_frame_top, textvariable=self.area_var,
                                       values=["Area 1", "Area 2", "Area 3"], state="readonly", font=("Arial", 11))
        self.combo_area.pack(side=tk.LEFT, padx=10)
        self.combo_area.bind("<<ComboboxSelected>>", self.load_data)

        # වගුවේ තීරු (No වෙනුවට 1,2,3 ලෙස සටහන් වේ)
        columns = ("No", "Bill Name", "Bill Number", "Amount Due", "Received Today")
        self.tree = ttk.Treeview(frame_area, columns=columns, show="headings", height=8)

        self.tree.heading("No", text="අංකය")
        self.tree.heading("Bill Name", text="ණය බිලේ නම")
        self.tree.heading("Bill Number", text="ණය බිලේ අංකය")
        self.tree.heading("Amount Due", text="ලැබිය යුතු ගාන")
        self.tree.heading("Received Today", text="අද ලැබුණු මුදල")

        self.tree.column("No", width=50, anchor="center")
        self.tree.column("Bill Name", width=150, anchor="w")
        self.tree.column("Bill Number", width=120, anchor="center")
        self.tree.column("Amount Due", width=130, anchor="e")
        self.tree.column("Received Today", width=130, anchor="e")
        self.tree.pack(pady=10, fill="x")

        # මුළු එකතුවන් පෙන්වන කොටස (වගුවට පහලින්)
        inner_frame_totals = tk.Frame(frame_area)
        inner_frame_totals.pack(fill="x", pady=5)

        self.lbl_total_due = tk.Label(inner_frame_totals, text="Total Amount Due: Rs. 0.00", font=("Arial", 12, "bold"),
                                      fg="#2980b9")
        self.lbl_total_due.pack(side=tk.LEFT, padx=5)

        self.lbl_total_collection = tk.Label(inner_frame_totals, text="Total Collection: Rs. 0.00",
                                             font=("Arial", 12, "bold"), fg="#27ae60")
        self.lbl_total_collection.pack(side=tk.RIGHT, padx=5)

        # වගුවෙන් තෝරාගත් බිලකට සල්ලි කැපීම
        inner_frame_pay = tk.Frame(frame_area)
        inner_frame_pay.pack(fill="x", pady=10)

        tk.Label(inner_frame_pay, text="Enter Received Amount for Selected Bill (Rs):", font=("Arial", 10)).pack(
            side=tk.LEFT, padx=5)
        self.entry_received = tk.Entry(inner_frame_pay, font=("Arial", 10), width=15)
        self.entry_received.pack(side=tk.LEFT, padx=5)

        btn_update = tk.Button(inner_frame_pay, text="Update Bill", command=self.update_bill, bg="#f39c12", fg="white",
                               font=("Arial", 10, "bold"), padx=10)
        btn_update.pack(side=tk.LEFT, padx=5)

        # අලුතෙන් බිලක් ඇතුලත් කිරීම
        btn_add = tk.Button(frame_area, text="+ Add New Bill", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white",
                            command=self.add_new_bill_popup)
        btn_add.pack(anchor="w", pady=5)

        # -----------------------------------------------------------
        # කොටස 3: අවසාන ගණනය කිරීම් (Today Sale)
        # -----------------------------------------------------------
        frame_final = tk.LabelFrame(root, text=" 3. Summary & Final Sale ", font=("Arial", 11, "bold"), padx=10,
                                    pady=10)
        frame_final.pack(pady=10, fill="x", padx=40)

        btn_calculate = tk.Button(frame_final, text="Calculate Today Sale", command=self.calculate_final_sale,
                                  font=("Arial", 12, "bold"), bg="#34495e", fg="white", pady=5)
        btn_calculate.pack(side=tk.LEFT, padx=10)

        self.lbl_today_sale = tk.Label(frame_final, text="TODAY SALE: Rs. 0.00", font=("Arial", 18, "bold"),
                                       fg="#c0392b")
        self.lbl_today_sale.pack(side=tk.RIGHT, padx=20)

    # --- 3. Core Logic & Database Operations ---

    def load_data(self, event=None):
        area = self.area_var.get()
        # වගුවේ පරණ දත්ත මැකීම
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("distribution.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, bill_name, bill_number, amount_due FROM credit_bills WHERE area=?", (area,))
        rows = cursor.fetchall()

        total_due = 0.0
        serial_no = 1  # වගුවේ අංකය 1 සිට ආරම්භ වීම

        for row in rows:
            db_id = row[0]
            name = row[1]
            number = row[2]
            due = row[3]

            # මෙම බිලට අද මුදලක් ගෙවා ඇත්නම් එය ලබාගැනීම (නැත්නම් 0)
            received_today = self.session_received.get(db_id, 0.0)

            # වගුවට දත්ත ඇතුලත් කිරීම. text=str(db_id) මගින් නියම Database ID එක පරිශීලකයාට නොපෙනෙන සේ රඳවා තබා ගනී.
            self.tree.insert("", tk.END, text=str(db_id),
                             values=(serial_no, name, number, f"{due:.2f}", f"{received_today:.2f}"))

            total_due += due
            serial_no += 1  # ඊළඟ පේළියට අංකය වැඩි කිරීම

        self.lbl_total_due.config(text=f"Total Amount Due: Rs. {total_due:.2f}")
        conn.close()

    def update_bill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "කරුණාකර ප්‍රථමයෙන් වගුවෙන් බිල්පතක් තෝරන්න!")
            return

        try:
            received = float(self.entry_received.get())
            if received <= 0:
                messagebox.showerror("Error", "කරුණාකර බිංදුවට වඩා වැඩි වලංගු මුදලක් ඇතුලත් කරන්න!")
                return

            item = self.tree.item(selected)
            # Database ID එක ලබා ගන්නේ සැඟවුණු text attribute එකෙනි
            db_id = int(item['text'])
            values = item['values']
            current_due = float(values[3])

            new_due = current_due - received

            conn = sqlite3.connect("distribution.db")
            cursor = conn.cursor()

            if new_due <= 0:
                cursor.execute("DELETE FROM credit_bills WHERE id=?", (db_id,))
                messagebox.showinfo("Success",
                                    "ණය මුදල සම්පූර්ණයෙන්ම ගෙවා ඇති බැවින් මෙම බිල්පත පද්ධතියෙන් ඉවත් කරන ලදී!")
                # සම්පුර්ණයෙන් ගෙව්වා නම් තාවකාලික මතකයෙන්ද ඉවත් කිරීම
                if db_id in self.session_received:
                    del self.session_received[db_id]
            else:
                cursor.execute("UPDATE credit_bills SET amount_due=? WHERE id=?", (new_due, db_id))
                # අද ලැබුණු මුදල තාවකාලිකව dictionary එකේ යාවත්කාලීන කිරීම
                self.session_received[db_id] = self.session_received.get(db_id, 0.0) + received

            conn.commit()
            conn.close()

            self.current_collection += received
            self.lbl_total_collection.config(text=f"Total Collection: Rs. {self.current_collection:.2f}")

            self.entry_received.delete(0, tk.END)
            self.load_data()

        except ValueError:
            messagebox.showerror("Error", "කරුණාකර ඇතුලත් කළ මුදල නැවත පරීක්ෂා කරන්න!")

    def calculate_final_sale(self):
        try:
            total_cash = float(self.entry_total_cash.get())
            today_sale = total_cash - self.current_collection
            self.lbl_today_sale.config(text=f"TODAY SALE: Rs. {today_sale:.2f}")
        except ValueError:
            messagebox.showerror("Error", "කරුණාකර Today Total Cash සඳහා වලංගු මුදලක් ඇතුලත් කරන්න!")

    def add_new_bill_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Credit Bill Form")
        popup.geometry("400x320")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="ඇතුලත් කිරීමේ පෝරමය", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=15)

        form_frame = tk.Frame(popup)
        form_frame.pack(pady=5, padx=20)

        tk.Label(form_frame, text="Area (ප්‍රදේශය):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w",
                                                                                       pady=5)
        popup_combo_area = ttk.Combobox(form_frame, values=["Area 1", "Area 2", "Area 3"], state="readonly", width=22,
                                        font=("Arial", 10))
        popup_combo_area.grid(row=0, column=1, pady=5, padx=10)
        popup_combo_area.set("Area 1")

        tk.Label(form_frame, text="Bill Name (නම):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w",
                                                                                      pady=5)
        popup_entry_name = tk.Entry(form_frame, width=24, font=("Arial", 10))
        popup_entry_name.grid(row=1, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Bill Number (අංකය):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w",
                                                                                          pady=5)
        popup_entry_number = tk.Entry(form_frame, width=24, font=("Arial", 10))
        popup_entry_number.grid(row=2, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Amount Due (මුදල):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w",
                                                                                         pady=5)
        popup_entry_due = tk.Entry(form_frame, width=24, font=("Arial", 10))
        popup_entry_due.grid(row=3, column=1, pady=5, padx=10)

        def save_to_database():
            area = popup_combo_area.get()
            name = popup_entry_name.get().strip()
            num = popup_entry_number.get().strip()
            due_str = popup_entry_due.get().strip()

            if not name or not num or not due_str:
                messagebox.showerror("Error", "කරුණාකර සියලුම හිස්තැන් පුරවන්න!", parent=popup)
                return
            try:
                due_amount = float(due_str)
                if due_amount <= 0:
                    messagebox.showerror("Error", "ලැබිය යුතු මුදල බිංදුවට වඩා වැඩි විය යුතුය!", parent=popup)
                    return
            except ValueError:
                messagebox.showerror("Error", "කරුණාකර මුදල සඳහා වලංගු සංඛ්‍යාවක් ඇතුලත් කරන්න!", parent=popup)
                return

            conn = sqlite3.connect("distribution.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO credit_bills (area, bill_name, bill_number, amount_due) VALUES (?, ?, ?, ?)",
                           (area, name, num, due_amount))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "නව ණය බිල්පත සාර්ථකව ඇතුලත් කරන ලදී!", parent=popup)

            if self.area_var.get() == area:
                self.load_data()

            popup.destroy()

        btn_save = tk.Button(popup, text="Save Bill", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white", width=15,
                             command=save_to_database)
        btn_save.pack(pady=15)


if __name__ == "__main__":
    setup_db()
    root = tk.Tk()
    app = CashSaleApp(root)
    root.mainloop()
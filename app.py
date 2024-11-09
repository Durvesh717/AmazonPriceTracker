import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import Database
import sqlite3

# Install matplotlib if it's not already installed
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt

class PriceTrackerApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.title("Amazon Price Tracker")
        self.geometry("500x400")
        self.username = username

        # Load and set background image
        self.background_image = Image.open("bg1.jpg")
        self.background_image = self.background_image.resize((500, 400), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Widget Styling
        title_font = ("Helvetica", 18, "bold")
        label_font = ("Helvetica", 12)
        entry_font = ("Helvetica", 12)
        button_font = ("Helvetica", 12, "bold")

        # Sign Out and Delete User Buttons
        self.sign_out_button = tk.Button(self, text="Sign Out", font=button_font, fg="red", bg="white", command=self.sign_out)
        self.sign_out_button.place(relx=0.7, rely=0.1, anchor="center")
        self.delete_user_button = tk.Button(self, text="Delete User", font=button_font, fg="red", bg="white", command=self.delete_user)
        self.delete_user_button.place(relx=0.9, rely=0.1, anchor="center")

        # Main Widgets
        self.title_label = tk.Label(self, text="Amazon Price Tracker", font=title_font, fg="white", bg="black")
        self.link_label = tk.Label(self, text="Product Link:", font=label_font, fg="white", bg="black")
        self.link_entry = tk.Entry(self, width=30, font=entry_font)
        self.price_label = tk.Label(self, text="Target Price:", font=label_font, fg="white", bg="black")
        self.price_entry = tk.Entry(self, width=15, font=entry_font)
        self.track_button = tk.Button(self, text="Track Price", font=button_font, bg="#007acc", fg="white",
                                      activebackground="green", command=self.open_price_tracker_window)
        self.display_all_button = tk.Button(self, text="Display All Products", font=button_font, bg="#007acc", fg="white",
                                            command=self.display_all_tracked_products)
        self.view_history_button = tk.Button(self, text="View Tracked Product History", font=button_font, bg="#007acc", fg="white",
                                             command=self.prompt_and_display_product_history)

        # Place widgets
        self.place_widgets()
        self.bind("<Configure>", self.resize_background)

    def place_widgets(self):
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")  # Adjusted rely to 0.2 for a lower position
        self.link_label.place(relx=0.3, rely=0.35, anchor="e")
        self.link_entry.place(relx=0.35, rely=0.35, anchor="w")
        self.price_label.place(relx=0.3, rely=0.5, anchor="e")
        self.price_entry.place(relx=0.35, rely=0.5, anchor="w")
        self.track_button.place(relx=0.5, rely=0.65, anchor="center")
        self.display_all_button.place(relx=0.5, rely=0.75, anchor="center")
        self.view_history_button.place(relx=0.5, rely=0.85, anchor="center")


    def resize_background(self, event):
        new_width, new_height = event.width, event.height
        resized_image = self.background_image.resize((new_width, new_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.bg_label.config(image=self.bg_photo)

    def sign_out(self):
        if messagebox.askyesno("Sign Out", f"Are you sure you want to sign out?"):
            self.destroy()

    def delete_user(self):
        if messagebox.askyesno("Delete User", f"Are you sure you want to delete your account ({self.username})? This action is irreversible."):
            self.remove_user_from_credentials()
            db_file = f"{self.username}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
            messagebox.showinfo("Deleted", f"User {self.username} has been deleted.")
            self.destroy()

    def remove_user_from_credentials(self):
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
        with open("credentials.txt", "w") as file:
            for line in lines:
                if not line.startswith(f"{self.username},"):
                    file.write(line)

    def open_price_tracker_window(self):
        product_id = simpledialog.askstring("Product ID", "Enter a unique product ID:")
        product_name = simpledialog.askstring("Product Name", "Enter the product name:")

        if not product_id or not product_name:
            messagebox.showerror("Input Error", "Both Product ID and Product Name are required.")
            return

        link = self.link_entry.get()
        target_price = self.price_entry.get()
        if not link or not target_price:
            messagebox.showerror("Input Error", "Both product link and target price are required.")
            return

        try:
            target_price = float(target_price)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for the target price.")
            return

        self.save_price_tracking_info(product_id, product_name, link, target_price)

    def save_price_tracking_info(self, product_id, product_name, link, target_price):
        try:
            Database.addproduct(self.username, product_id, product_name, link, target_price)
            messagebox.showinfo("Success", "Product added and tracking started.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate ID", "Product ID already exists. Please enter a unique ID.")

    def display_all_tracked_products(self):
        products = Database.loadproductsdb(self.username)
        if not products:
            messagebox.showinfo("No Products", "No products are currently being tracked.")
            return

        self.all_products_window = tk.Toplevel(self)
        self.all_products_window.title("Tracked Products")
        self.all_products_window.geometry("400x300")

        tk.Label(self.all_products_window, text="Currently Tracked Products", font=("Helvetica", 14, "bold")).pack(pady=10)
        for product_id, product_name, link, price in products:
            product_label = tk.Label(self.all_products_window, text=f"ID: {product_id}, Name: {product_name}, Target Price: ${price}")
            product_label.pack(anchor="w", padx=10, pady=2)

            delete_button = tk.Button(self.all_products_window, text="Delete", command=lambda pid=product_id: self.delete_product(pid))
            delete_button.pack(anchor="e", padx=10)

    def delete_product(self, product_id):
        if messagebox.askyesno("Delete Product", f"Are you sure you want to delete Product ID: {product_id}?"):
            Database.deleteproduct(self.username, product_id)
            messagebox.showinfo("Deleted", f"Product ID {product_id} has been deleted.")
            if hasattr(self, 'all_products_window') and self.all_products_window.winfo_exists():
                self.all_products_window.destroy()
            self.display_all_tracked_products()

    def prompt_and_display_product_history(self):
        # Prompt the user for the product ID to display the price history
        product_id = simpledialog.askstring("Product ID", "Enter the product ID to view price history:")
        if not product_id:
            messagebox.showerror("Input Error", "Product ID is required.")
            return

        # Retrieve the price history data
        price_history = Database.loadproductpricedb(self.username, product_id)
        if not price_history:
            messagebox.showerror("ERROR", "Either product history has not been tracked or the ID is invalid.")
            return

        # Extract prices from the price history for the graph
        prices = [h[0] for h in price_history]
        highest_price = max(prices)
        lowest_price = min(prices)
        average_price = sum(prices) / len(prices)

        # Create a window for displaying price history
        price_window = tk.Toplevel(self)
        price_window.title(f"Price History for Product ID: {product_id}")
        price_window.geometry("700x550")  # Adjusted window size

        product_label = tk.Label(price_window, text=f"Product ID: {product_id}", font=("Helvetica", 14, "bold"))
        product_label.pack(pady=10)

        # Display price summary details
        tk.Label(price_window, text=f"Highest Price: ${highest_price:.2f}").pack(pady=5)
        tk.Label(price_window, text=f"Lowest Price: ${lowest_price:.2f}").pack(pady=5)
        tk.Label(price_window, text=f"Average Price: ${average_price:.2f}").pack(pady=5)

        fig, ax = plt.subplots(figsize=(6, 5))  # Increased figure size for label visibility
        ax.plot(prices, marker="o")
        ax.set_title("Price History")
        ax.set_xlabel("Time(Day)")
        ax.set_ylabel("Price ($)")
        ax.grid(True)

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=price_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


if __name__ == "__main__":
    username = sys.argv[2]
    app = PriceTrackerApp(username)
    app.mainloop()

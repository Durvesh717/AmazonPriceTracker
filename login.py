import Database
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import os

class TrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Price Tracker")
        self.root.geometry("400x400")

        # Load background image and create placeholders
        self.original_image = Image.open("lback1.jpg")  # Replace with your image path
        self.bg_photo = ImageTk.PhotoImage(self.original_image)

        # Create canvas for background and widgets
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill="both", expand=True)

        # Display the background image
        self.background_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Configure styles for a clean look
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        self.style.configure("TLabel", background="#f2f2f2", font=("Arial", 10))
        self.style.configure("Title.TLabel", font=("Arial", 14, "bold"), foreground="#333")

        # Initialize login screen
        self.show_login_screen()

        # Bind the resize event to adjust layout
        root.bind("<Configure>", self.resize_background)

    def resize_background(self, event):
        # Resize background to fit new window size
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.canvas.itemconfig(self.background_id, image=self.bg_photo)

        # Reposition widgets dynamically
        self.reposition_widgets(new_width, new_height)

    def reposition_widgets(self, width, height):
        # Calculate centered positions for widgets based on the current window size
        widget_y_positions = {
            "title": height * 0.15,
            "login_frame": height * 0.4,
            "login_button": height * 0.65,
            "register_button": height * 0.65
        }

        # Center widgets horizontally and position vertically as per layout
        if hasattr(self, "title_label_id"):
            self.canvas.coords(self.title_label_id, width / 2, widget_y_positions["title"])
        if hasattr(self, "login_frame_id"):
            self.canvas.coords(self.login_frame_id, width / 2, widget_y_positions["login_frame"])
        if hasattr(self, "login_button_id"):
            self.canvas.coords(self.login_button_id, width / 3, widget_y_positions["login_button"])
        if hasattr(self, "register_button_id"):
            self.canvas.coords(self.register_button_id, 2 * width / 3, widget_y_positions["register_button"])

    def show_login_screen(self):
        self.clear_widgets()

        # Place widgets on the canvas for positioning over background
        self.title_label = ttk.Label(self.root, text="Amazon Price Tracker", style="Title.TLabel")
        self.title_label_id = self.canvas.create_window(200, 50, window=self.title_label, tags="title")

        # Login form
        self.login_frame = ttk.Frame(self.root, padding="10 10 10 10", style="TFrame")
        self.login_frame_id = self.canvas.create_window(200, 150, window=self.login_frame, tags="login_frame")

        ttk.Label(self.login_frame, text="Username:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(column=1, row=0, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.grid(column=1, row=1, pady=5)

        # Login and Register buttons
        self.login_button = ttk.Button(self.root, text="Login", command=self.login)
        self.login_button_id = self.canvas.create_window(140, 250, window=self.login_button, tags="login_button")

        self.register_button = ttk.Button(self.root, text="Create Account", command=self.show_register_screen)
        self.register_button_id = self.canvas.create_window(260, 250, window=self.register_button,
                                                            tags="register_button")

    def show_register_screen(self):
        self.clear_widgets()

        self.title_label = ttk.Label(self.root, text="Register a New Account", style="Title.TLabel")
        self.title_label_id = self.canvas.create_window(200, 50, window=self.title_label, tags="title")

        self.register_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.register_frame_id = self.canvas.create_window(200, 150, window=self.register_frame, tags="register_frame")

        ttk.Label(self.register_frame, text="Username:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.register_frame, width=30)
        self.username_entry.grid(column=1, row=0, pady=5)

        ttk.Label(self.register_frame, text="Password:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.register_frame, show="*", width=30)
        self.password_entry.grid(column=1, row=1, pady=5)

        ttk.Label(self.register_frame, text="Email:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(self.register_frame, width=30)
        self.email_entry.grid(column=1, row=2, pady=5)

        self.register_button = ttk.Button(self.root, text="Register", command=self.register)
        self.register_button_id = self.canvas.create_window(200, 250, window=self.register_button,
                                                            tags="register_button")

        self.back_button = ttk.Button(self.root, text="Back to Login", command=self.show_login_screen)
        self.back_button_id = self.canvas.create_window(200, 300, window=self.back_button, tags="back_button")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.create_user_database(username)

        # Read credentials file and check for a match
        try:
            with open("credentials.txt", "r") as file:
                for line in file:
                    fields= line.strip().split(",")
                    if not fields[0]:
                        messagebox.showerror("Error", "No registered accounts found. Please register first.")
                        return
                    saved_username, saved_password, saved_email = fields[:3]
                    if saved_username == username and saved_password == password:
                        messagebox.showinfo("Login Successful", "Welcome back!")
                        self.show_dashboard(saved_email,saved_username)
                        return
            messagebox.showerror("Login Failed", "Incorrect username or password")
        except FileNotFoundError:
            messagebox.showerror("Error", "No registered accounts found. Please register first.")

    def create_user_database(self, username):
            db_name = f"{username}.db"
            if not os.path.exists(db_name):
                Database.createdb(db_name)

    def show_dashboard(self,email,username):
        subprocess.Popen(['python', 'app.py',email,username])

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        if username and password and email:
            with open("credentials.txt", "r") as file:
                for line in file:
                    fields= line.strip().split(",")
                    if fields[0]=='':
                        break
                    saved_username, saved_password, saved_email = fields[:3]
                    if(username == saved_username):
                        messagebox.showerror("Error", "Username already exists")
                        return
            self.save_credentials(username, password, email)
            self.create_user_database(username)
            messagebox.showinfo("Registration", "Account created successfully!")
            self.show_login_screen()
        else:
            messagebox.showerror("Error", "All fields are required.")

    def save_credentials(self, username, password, email):
        with open("credentials.txt", "a") as file:
            file.write(f"{username},{password},{email},\n")

    def track_price(self):
        product_link = self.link_entry.get()
        target_price = self.price_entry.get()
        messagebox.showinfo("Tracking", f"Tracking {product_link} at ${target_price} or less.")

    def clear_widgets(self):
        # Clear all items on the canvas
        self.canvas.delete("all")
        # Re-create the background image
        self.background_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")


# Run the app
root = tk.Tk()
app = TrackerApp(root)
root.mainloop()

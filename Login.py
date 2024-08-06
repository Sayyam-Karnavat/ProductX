import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk,ImageSequence
import ctypes

import requests
import default
from deploy_locale import *


class LoginApp:
    def __init__(self):
        self.data = default.DefaultApp()
    def Login(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1 = PROCESS_SYSTEM_DPI_AWARE
        except Exception as e:
            print(f"Error setting DPI awareness: {e}")
        # data.root.wm_attributes('-fullscreen', True)  # Make the window full screen
        self.data.default()
        # Configure the window's size to match the screen size
        screen_width = self.data.screen_width
        screen_height = self.data.screen_height
        # self.data.root.geometry(f"{screen_width}x{screen_height}")
        self.data.root.iconbitmap('./Assets/login.ico')
        self.data.root.title("Login Page")

        frame = tk.Frame(self.data.root,bg="#fff",relief="solid")
        frame.pack(fill="both", padx=100, pady=100)

        image_frame = tk.Frame(frame, bg="#000")
        image_frame.pack(side="right", fill="both")

        text_frame = tk.Frame(frame, bg="#fff")
        text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(text_frame,text="LOGIN",font=(self.data.header_font,24,"bold"),bg="#fff").pack()

        # exit_button = tk.Button(self.data.root, text="Exit Full Screen", command=self.exit_fullscreen)
        # exit_button.pack(pady=20)

        image=Image.open("./Assets/user.png")
        image = image.resize((200,200))

        self.img = ImageTk.PhotoImage(image)

        lable = tk.Label(text_frame,bg="#fff", image=self.img)
        lable.pack()
    
        scl=Image.open("./Assets/scl.jpg")
        scl.thumbnail((screen_width-800, screen_height))
        # sclimg = scl.resize((frame_height, frame_width))
        self.scl = ImageTk.PhotoImage(scl)

        scllable = tk.Label(image_frame, image=self.scl)
        scllable.pack()

        tk.Label(text_frame, text="Username/Mobile Number", bg="#fff", font=(self.data.font, 14)).pack(padx=10, pady=10)
        self.mobile_entry = tk.Entry(text_frame, font=(self.data.font, 14),relief="solid")
        self.mobile_entry.pack(padx=10, pady=10)

        tk.Label(text_frame, text="Password", bg="#fff", font=(self.data.font, 14)).pack(padx=10, pady=10)
        self.password_entry = tk.Entry(text_frame, show='*', font=(self.data.font, 14),relief="solid")
        self.password_entry.pack(padx=10, pady=10)

        tk.Button(text_frame, text="Login", bg="#4CAF50", font=(self.data.font, 14), relief="raised",command=self.check_credentials).pack(pady=20)

    def open_loading_window(self):
        # Create a pop-up window for loading
        loading_window = tk.Toplevel(self.data.root)
        loading_window.title("Loading")
        window_width = 400
        window_height = 300
        x = (self.data.screen_width - window_width) // 2
        y = (self.data.screen_height - window_height) // 2
        loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        loading_window.overrideredirect(True)

        # Load the GIF and prepare frames
        gif_path = "./Assets/loading.gif"
        gif_image = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]
        label = tk.Label(loading_window, text="Loading, please wait...", compound="top",font=(self.data.font, 14),fg="gray")
        label.pack(expand=True)
        # Function to update the frame
        def update_frame(frame_index):
            if loading_window.winfo_exists():  # Check if the window still exists
                label.config(image=frames[frame_index])
                frame_index = (frame_index + 1) % len(frames)
                loading_window.after(100, update_frame, frame_index)  # Update every 100ms

        update_frame(0)

        # Simulate processing task
        self.data.root.after(3000, lambda: self.finish_loading(loading_window))

    def finish_loading(self,loading_window=None):
        if loading_window and loading_window.winfo_exists():  # Check if the window still exists
            loading_window.destroy()

    def check_credentials(self):
        valid_mobile = "admin"
        valid_password = "admin"

        mobile = self.mobile_entry.get()
        password = self.password_entry.get()

        if mobile == valid_mobile and password == valid_password:
            self.open_loading_window()
            self.data.root.after(3000, lambda: self.process_login()) 
        else:
            messagebox.showerror("Login Error", "Invalid mobile number or password.")


    def process_login(self):
        self.create_database_and_table()
        transaction_id = deploy_data("B", self.data.start_time, "-", "-")
        student_data = {
            "wallet_address": wallet_address,
            "booklet": "B",
            "start_time": self.data.start_time,
            "que_ans": "-",
            "end_time": "-",
            "transaction_id": transaction_id
        }
        # print("Sending student data:", student_data)
        self.add_student_data(student_data)
        self.data.root.destroy()
        self.open_quiz_page()

    def create_database_and_table(self):
        api_url = "http://127.0.0.1:5000/create_student_data"
        try:
            response = requests.post(api_url)
            response.raise_for_status() 
            print("Database and table created successfully.")
        except requests.RequestException as e:
            print(f"Error creating database and table: {e}")
    
    def add_student_data(self,student_data):
        api_url = "http://127.0.0.1:5000/add_student_data"
        try:
            response = requests.post(api_url, json=student_data)
            response.raise_for_status()  
            print("Data uploaded successfully.")
        except requests.RequestException as e:
            print(f"Error uploading data in table: {e}")

    def open_quiz_page(self):
        import Qna 
        app = Qna.QuizApp()
        app.QnA()

if __name__ == "__main__":
    login=LoginApp()
    login.Login()
    login.data.root.mainloop()


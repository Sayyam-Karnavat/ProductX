import datetime
import tkinter as tk

class DefaultApp:
    
    def default(self):
        self.root = tk.Tk()
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.header_font="Segoe Script"
        self.font = "Comic Sans MS"
        self.root.wm_attributes('-fullscreen', True)  # Make the window full screen
        self.time = datetime.datetime.now()
        self.date = f"{self.time.day}/{self.time.month}/{self.time.year}"
        self.time_str = f"{self.time.hour}:{self.time.minute}:{self.time.second}"
        self.start_time = f"{self.date} {self.time_str}"

        # Configure the window's size to match the screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.credentials = {
            "user":"admin",
            "password":"admin"
        }
    
    def exit_fullscreen(self, event=None):
        self.root.wm_attributes('-fullscreen', False)
        self.root.quit()

# data=DefaultApp()
# data.default()




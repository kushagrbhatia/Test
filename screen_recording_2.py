import tkinter as tk
from tkinter import ttk
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
from threading import Thread

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.recording = False
        self.region = None
        self.video_writer = None
        
        # UI Elements
        self.frame = ttk.Frame(root, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.select_btn = ttk.Button(self.frame, text="Select Region", command=self.start_region_selection)
        self.start_btn = ttk.Button(self.frame, text="Start Recording", command=self.start_recording)
        self.stop_btn = ttk.Button(self.frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        
        self.select_btn.pack(pady=5, fill=tk.X)
        self.start_btn.pack(pady=5, fill=tk.X)
        self.stop_btn.pack(pady=5, fill=tk.X)
        
        # Region selection variables
        self.overlay = None
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None

    def start_region_selection(self):
        self.region = None
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.configure(background='gray')
        
        self.canvas = tk.Canvas(self.overlay, cursor='cross', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline='white', width=2)

    def on_drag(self, event):
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_release(self, event):
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.region = (
            min(self.start_x, self.end_x),
            min(self.start_y, self.end_y),
            abs(self.end_x - self.start_x),
            abs(self.end_y - self.start_y)
        )
        self.overlay.destroy()

    def start_recording(self):
        if not self.region:
            return
            
        self.recording = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            "recording.avi", fourcc, 20.0, 
            (self.region[2], self.region[3])
        )
        
        Thread(target=self.record_screen, daemon=True).start()

    def record_screen(self):
        while self.recording:
            img = ImageGrab.grab(bbox=self.region)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.video_writer.write(frame)
            
        self.video_writer.release()

    def stop_recording(self):
        self.recording = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()

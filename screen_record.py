import os
import pyautogui
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from PyPDF2 import PdfWriter
import datetime

# Store captured screenshots
captured_images = []

def capture_screen_area(x1, y1, x2, y2):
    width = x2 - x1
    height = y2 - y1
    return pyautogui.screenshot(region=(x1, y1, width, height))

def capture_and_preview(x1, y1, x2, y2):
    img = capture_screen_area(x1, y1, x2, y2)

    preview = tk.Toplevel(root)
    preview.title("Screenshot Preview")

    img_tk = ImageTk.PhotoImage(img)
    img_label = tk.Label(preview, image=img_tk)
    img_label.image = img_tk
    img_label.pack()

    def add_to_pdf():
        captured_images.append(img.convert('RGB'))
        messagebox.showinfo("Added", "Screenshot added to PDF!")
        preview.destroy()

    def retake():
        preview.destroy()
        launch_snip_mode()

    button_frame = tk.Frame(preview)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Add to PDF", command=add_to_pdf).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Retake", command=retake).pack(side=tk.LEFT, padx=10)

def launch_snip_mode():
    snip_window = tk.Toplevel(root)
    snip_window.attributes("-fullscreen", True)
    snip_window.attributes("-alpha", 0.3)
    snip_window.configure(bg='gray')

    canvas = tk.Canvas(snip_window, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)
    rect = canvas.create_rectangle(0, 0, 0, 0, outline="red", width=2)

    start_x = start_y = end_x = end_y = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y

    def on_mouse_drag(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        canvas.coords(rect, start_x, start_y, end_x, end_y)

    def on_mouse_up(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y

        abs_start_x = canvas.winfo_rootx() + start_x
        abs_start_y = canvas.winfo_rooty() + start_y
        abs_end_x = canvas.winfo_rootx() + end_x
        abs_end_y = canvas.winfo_rooty() + end_y

        snip_window.destroy()

        x1, x2 = sorted([abs_start_x, abs_end_x])
        y1, y2 = sorted([abs_start_y, abs_end_y])

        capture_and_preview(x1, y1, x2, y2)

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

def save_all_to_pdf():
    if not captured_images:
        messagebox.showwarning("No Images", "You haven't added any screenshots yet.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"screenshots_{timestamp}.pdf"
    captured_images[0].save(output_path, save_all=True, append_images=captured_images[1:])
    messagebox.showinfo("Saved", f"PDF saved as:\n{output_path}")
    captured_images.clear()

def quit_app():
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Snipping Tool (Cross-Platform)")
root.geometry("300x180")

tk.Label(root, text="Snipping Tool Clone", font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="New Snip", command=launch_snip_mode, width=20).pack(pady=5)
tk.Button(root, text="Save All to PDF", command=save_all_to_pdf, width=20).pack(pady=5)
tk.Button(root, text="Exit", command=quit_app, width=20).pack(pady=5)

root.mainloop()
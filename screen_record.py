import os
from PIL import ImageGrab, Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import datetime
from PyPDF2 import PdfReader, PdfWriter

# List to store screenshots
screenshots = []

# Expansion constants
EXPAND_X = 20  # Expand width on both sides
EXPAND_Y = 50  # Expand height (mostly at the bottom)

def take_screenshot():
    global selection_window
    selection_window = tk.Toplevel(root)
    selection_window.attributes("-fullscreen", True)
    selection_window.attributes("-alpha", 0.3)
    selection_window.configure(bg='gray')

    canvas = tk.Canvas(selection_window, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)
    rect = canvas.create_rectangle(0, 0, 0, 0, outline='red', width=2)

    global start_x, start_y, end_x, end_y
    start_x = start_y = end_x = end_y = 0

    def on_mouse_down(event):
        global start_x, start_y
        start_x, start_y = event.x, event.y

    def on_mouse_drag(event):
        global end_x, end_y
        end_x, end_y = event.x, event.y
        canvas.coords(rect, start_x, start_y, end_x, end_y)

    def on_mouse_up(event):
        global end_x, end_y
        end_x, end_y = event.x, event.y

        # Convert to screen coordinates
        abs_start_x = canvas.winfo_rootx() + start_x
        abs_start_y = canvas.winfo_rooty() + start_y
        abs_end_x = canvas.winfo_rootx() + end_x
        abs_end_y = canvas.winfo_rooty() + end_y

        # Expand horizontally
        if abs_end_x > abs_start_x:
            abs_start_x -= EXPAND_X
            abs_end_x += EXPAND_X
        else:
            abs_start_x += EXPAND_X
            abs_end_x -= EXPAND_X

        # Expand vertically
        if abs_end_y > abs_start_y:
            abs_start_y -= EXPAND_Y // 2
            abs_end_y += EXPAND_Y
        else:
            abs_start_y += EXPAND_Y
            abs_end_y -= EXPAND_Y // 2

        selection_window.destroy()

        # Sort coordinates
        x1, x2 = sorted([abs_start_x, abs_end_x])
        y1, y2 = sorted([abs_start_y, abs_end_y])

        capture_screenshot(x1, y1, x2, y2)

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

def capture_screenshot(x1, y1, x2, y2):
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    preview_screenshot(screenshot)

def preview_screenshot(screenshot):
    preview_window = tk.Toplevel(root)
    preview_window.title("Screenshot Preview")

    img = ImageTk.PhotoImage(screenshot)
    img_label = tk.Label(preview_window, image=img)
    img_label.image = img
    img_label.pack()

    def add_to_pdf():
        screenshots.append(screenshot)
        messagebox.showinfo("Info", "Screenshot added to PDF!")
        preview_window.destroy()

    add_button = tk.Button(preview_window, text="Add to PDF", command=add_to_pdf)
    add_button.pack(pady=10)

def save_pdf():
    if not screenshots:
        messagebox.showwarning("Warning", "No screenshots to save!")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"screenshots_{timestamp}.pdf"

    screenshots_rgb = [img.convert('RGB') for img in screenshots]
    screenshots_rgb[0].save(
        pdf_path,
        save_all=True,
        append_images=screenshots_rgb[1:],
        resolution=100.0
    )

    max_size = 8 * 1024 * 1024  # 8 MB
    if os.path.getsize(pdf_path) > max_size:
        compress_pdf(pdf_path)

    messagebox.showinfo("Info", f"Screenshots saved as {pdf_path}")

def compress_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with open(pdf_path, "wb") as f:
        writer.write(f)

# GUI
root = tk.Tk()
root.title("Screenshot to PDF")

take_screenshot_button = tk.Button(root, text="Take Screenshot", command=take_screenshot)
take_screenshot_button.pack(pady=10)

save_pdf_button = tk.Button(root, text="Save PDF", command=save_pdf)
save_pdf_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=root.quit)
stop_button.pack(pady=10)

root.mainloop()
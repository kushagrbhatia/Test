import os
import pyautogui
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from PyPDF2 import PdfWriter
import datetime
import threading
from tkinter import filedialog

# Globals for session
session_folder = None
capture_coords = None
capture_running = False
screenshot_counter = 0
capture_timer_id = None

# --- Screenshot Capture Logic ---
def get_session_folder():
    global session_folder
    if session_folder is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        session_folder = os.path.join(os.getcwd(), f"snip_session_{timestamp}")
        os.makedirs(session_folder, exist_ok=True)
    return session_folder

def capture_screen_area(x1, y1, x2, y2):
    width = x2 - x1
    height = y2 - y1
    return pyautogui.screenshot(region=(x1, y1, width, height))

def periodic_capture():
    global screenshot_counter, capture_running, capture_coords, capture_timer_id
    if not capture_running or not capture_coords:
        return
    x1, y1, x2, y2 = capture_coords
    img = capture_screen_area(x1, y1, x2, y2)
    folder = get_session_folder()
    filename = os.path.join(folder, f'snip_{screenshot_counter:03d}.png')
    img.save(filename)
    screenshot_counter += 1
    # Schedule next capture in 0.5 seconds
    capture_timer_id = root.after(500, periodic_capture)

def start_periodic_capture(x1, y1, x2, y2):
    global capture_running, capture_coords, screenshot_counter, session_folder, capture_timer_id
    capture_running = True
    capture_coords = (x1, y1, x2, y2)
    screenshot_counter = 0
    session_folder = None
    if capture_timer_id:
        root.after_cancel(capture_timer_id)
    periodic_capture()

def stop_periodic_capture():
    global capture_running, capture_timer_id
    capture_running = False
    if capture_timer_id:
        root.after_cancel(capture_timer_id)
        capture_timer_id = None

# --- GUI and Workflow ---
def capture_and_show(x1, y1, x2, y2):
    start_periodic_capture(x1, y1, x2, y2)
    # Show preview of the first screenshot
    img = capture_screen_area(x1, y1, x2, y2)
    show_preview(img)
    show_post_snip_controls()

def save_all_to_pdf():
    stop_periodic_capture()
    folder = get_session_folder()
    images = []
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith('.png'):
            img_path = os.path.join(folder, fname)
            img = Image.open(img_path).convert('RGB')
            images.append(img)
    if not images:
        messagebox.showwarning("No Images", "No screenshots found to save.")
        return
    pdf_path = os.path.join(folder, 'snip_session.pdf')
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    messagebox.showinfo("PDF Saved", f"Saved all screenshots to {pdf_path}")

def add_to_pdf():
    # Deprecated: all images are saved automatically now
    messagebox.showinfo("Info", "Screenshots are automatically saved. Use 'Save as PDF' to combine them.")
    hide_post_snip_controls()

def retake():
    hide_post_snip_controls()
    clear_preview()
    launch_snip_mode()

def show_preview(img):
    resized = img.resize((250, int(img.height * 250 / img.width))) if img.width > 250 else img
    preview_img = ImageTk.PhotoImage(resized)
    preview_label.config(image=preview_img)
    preview_label.image = preview_img  # prevent garbage collection
    preview_label.pack(pady=10)

def clear_preview():
    preview_label.config(image='')
    preview_label.image = None
    preview_label.pack_forget()

def show_post_snip_controls():
    add_button.pack(pady=5)
    retake_button.pack(pady=5)

def hide_post_snip_controls():
    add_button.pack_forget()
    retake_button.pack_forget()
    clear_preview()

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

        capture_and_show(x1, y1, x2, y2)

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

def save_all_to_pdf():
    stop_periodic_capture()
    folder = get_session_folder()
    images = []
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith('.png'):
            img_path = os.path.join(folder, fname)
            img = Image.open(img_path).convert('RGB')
            images.append(img)
    if not images:
        messagebox.showwarning("No Images", "No screenshots found to save.")
        return
    # Ask user for base filename and location
    file_path = filedialog.asksaveasfilename(
        defaultextension='.pdf',
        filetypes=[('PDF files', '*.pdf')],
        title='Save PDF As',
        initialfile='snip_session.pdf'
    )
    if not file_path:
        return
    base, ext = os.path.splitext(file_path)
    # Split into multiple PDFs if size > 8MB
    max_size = 8 * 1024 * 1024  # 8MB
    part = 1
    idx = 0
    total = len(images)
    saved_files = []
    while idx < total:
        part_images = []
        # Always put at least one image in each PDF
        part_images.append(images[idx])
        idx += 1
        temp_path = f"{base}_part{part}{ext}" if total > 1 else file_path
        # Try to add as many images as possible without exceeding max_size
        for j in range(idx, total+1):
            try:
                part_images_to_save = part_images + images[idx:j]
                part_images_to_save[0].save(temp_path, save_all=True, append_images=part_images_to_save[1:])
                if os.path.getsize(temp_path) > max_size:
                    break
                part_images = part_images_to_save
                idx = j
            except Exception as e:
                break
        # Save the current part
        part_images[0].save(temp_path, save_all=True, append_images=part_images[1:])
        if os.path.getsize(temp_path) > max_size and len(part_images) > 1:
            # Remove last image and save again
            part_images = part_images[:-1]
            part_images[0].save(temp_path, save_all=True, append_images=part_images[1:])
            idx -= 1
        saved_files.append(temp_path)
        part += 1
    messagebox.showinfo("PDF Saved", f"Saved screenshots as PDF(s):\n" + '\n'.join(saved_files))
    clear_preview()
    hide_post_snip_controls()


def quit_app():
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Snipping Tool Clone")
root.geometry("300x500")

tk.Label(root, text="Snipping Tool Clone", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="New Snip", command=launch_snip_mode, width=25).pack(pady=5)
tk.Button(root, text="Save All to PDFs", command=save_all_to_pdf, width=25).pack(pady=5)
tk.Button(root, text="Exit", command=quit_app, width=25).pack(pady=5)

# Screenshot preview (hidden until used)
preview_label = tk.Label(root)
preview_label.pack_forget()

# Action buttons (hidden until screenshot is taken)
add_button = tk.Button(root, text="Add Screenshot to PDF", command=add_to_pdf, width=25, bg="#4CAF50", fg="white")
retake_button = tk.Button(root, text="Retake Screenshot", command=retake, width=25, bg="#f44336", fg="white")

root.mainloop()

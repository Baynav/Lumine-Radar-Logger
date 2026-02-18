import time
import re
import json
import sys
import os
import threading
import ctypes
import pytesseract
from mss import mss
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import messagebox
import pystray

def distance(a, b):
    return math.sqrt(
        (float(a[0]) - float(b[0])) ** 2 +
        (float(a[1]) - float(b[1])) ** 2 +
        (float(a[2]) - float(b[2])) ** 2
    )


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

tesseract_path = os.path.join(BASE_PATH, "tesseract", "tesseract.exe")
tessdata_path = os.path.join(BASE_PATH, "tesseract", "tessdata")

pytesseract.pytesseract.tesseract_cmd = tesseract_path
os.environ["TESSDATA_PREFIX"] = tessdata_path

APP_NAME = "Lumine Radar Logger"
CONFIG_FILE = "config.json"
LOG_FILE = "coords_log.txt"

tray_icon = None

def create_tray_image(color):
    img = Image.new("RGB", (64, 64), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse((16, 16, 48, 48), fill=color)
    return img

def update_tray(state, tooltip=None):
    colors = {
        "stopped": (200, 0, 0),
        "waiting": (220, 180, 0),
        "active": (0, 200, 0),
        "error": (120, 120, 120)
    }

    if tray_icon:
        tray_icon.icon = create_tray_image(colors[state])
        tray_icon.title = tooltip if tooltip else state.capitalize()

def setup_tray(root):
    global tray_icon

    def restore(icon, item=None):
        root.after(0, root.deiconify)

    def quit_app(icon, item=None):
        icon.stop()
        root.after(0, root.destroy)

    tray_icon = pystray.Icon(
        APP_NAME,
        create_tray_image((200, 0, 0)),
        "Stopped"
    )

    tray_icon.menu = pystray.Menu(
        pystray.MenuItem("Restore", restore, default=True),
        pystray.MenuItem("Quit", quit_app)
    )

    tray_icon.run_detached()

def select_region():
    messagebox.showinfo(APP_NAME, "Drag to select the Chat Box Area.")

    overlay = tk.Toplevel()
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)
    overlay.configure(bg="black")

    canvas = tk.Canvas(overlay, cursor="cross", bg="black")
    canvas.pack(fill="both", expand=True)

    coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
    rect = None

    def on_press(event):
        nonlocal rect
        coords["x1"] = event.x
        coords["y1"] = event.y
        rect = canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="lime", width=3
        )

    def on_drag(event):
        coords["x2"] = event.x
        coords["y2"] = event.y
        canvas.coords(rect,
                      coords["x1"], coords["y1"],
                      coords["x2"], coords["y2"])

    def on_release(event):
        coords["x2"] = event.x
        coords["y2"] = event.y
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    overlay.wait_window()

    return {
        "left": min(coords["x1"], coords["x2"]),
        "top": min(coords["y1"], coords["y2"]),
        "width": abs(coords["x2"] - coords["x1"]),
        "height": abs(coords["y2"] - coords["y1"])
    }

def save_region(region):
    with open(CONFIG_FILE, "w") as f:
        json.dump(region, f)

def load_region():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None


def preprocess(pil):
    pil = pil.convert("L")
    pil = pil.resize((pil.width * 2, pil.height * 2), Image.NEAREST)
    pil = pil.point(lambda p: 255 if p > 180 else 0)
    return pil

def extract_events(text):
    events = []
    lines = text.splitlines()

    for line in lines:
        lower = line.lower()

        if "logged" not in lower:
            continue

        numbers = re.findall(r"-?\d+\.\d+", line)

        if len(numbers) >= 3:

            event_match = re.search(r"logged([a-zA-Z]+)", lower)
            if event_match:
                event_name = event_match.group(1).upper()
            else:
                event_name = "UNKNOWN"

            events.append((event_name, numbers[0], numbers[1], numbers[2]))

    return events


def logger_loop(region, update_status, app_state):
    DISTANCE_THRESHOLD = 350.0
    logged_coords = {}  
    update_tray("waiting")
    previous_frame_hash = None

    try:
        with mss() as sct:
            while app_state["running"]:

                screenshot = sct.grab(region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                current_hash = hash(img.tobytes())

                if current_hash == previous_frame_hash:
                    time.sleep(1)
                    continue

                previous_frame_hash = current_hash

                processed = preprocess(img)
                text = pytesseract.image_to_string(
                    processed,
                    config="--psm 6 -c tessedit_char_whitelist=0123456789-.,[]()ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                )

                print("OCR OUTPUT:")
                print(text)
                print("-----")

                events = extract_events(text)

                for event in events:
                    event_type, x, y, z = event

                    current_coords = (
                        round(float(x), 2),
                        round(float(y), 2),
                        round(float(z), 2)
                    )

                    bucket = (
                        int(current_coords[0] // DISTANCE_THRESHOLD),
                        int(current_coords[1] // DISTANCE_THRESHOLD),
                        int(current_coords[2] // DISTANCE_THRESHOLD),
                    )

                    if bucket in logged_coords:
                        continue

                    logged_coords[bucket] = True

                    with open(app_state["session_log"], "a") as f:
                        f.write(
                            f"[{time.strftime('%H:%M:%S')}] "
                            f"{event_type} - X: {x} Y: {y} Z: {z}\n"
                        )

                    app_state["logged_count"] += 1
                    update_status(
                        f"Logged Coords: {app_state['logged_count']}",
                        "green"
                    )

                    update_tray(
                        "active",
                        f"Running | Logged Coords: {app_state['logged_count']}"
                    )

                time.sleep(1)

    except Exception as e:
        print("LOGGER ERROR:", e)
        update_tray("error")

    update_tray("stopped")

def main():
    global tray_icon

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("340x240")
    root.resizable(False, False)
    root.configure(bg="#1e1e1e")

    try:
        root.iconbitmap(resource_path("pixel_cat.ico"))
    except:
        pass

    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.windll.user32.GetParent(root.winfo_id()),
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.c_int)
        )
    except:
        pass

    app_state = {
        "running": False,
        "region": load_region(),
        "logged_count": 0,
        "session_log": None
    }

    status_frame = tk.Frame(root, bg="#1e1e1e")
    status_frame.pack(pady=15)

    status_dot = tk.Label(status_frame, text="●",
                          fg="red", bg="#1e1e1e",
                          font=("Segoe UI", 14))
    status_dot.pack(side="left", padx=(0, 8))

    status_label = tk.Label(status_frame,
                            text="Stopped",
                            fg="#cccccc",
                            bg="#1e1e1e",
                            font=("Segoe UI", 9))
    status_label.pack(side="left")

    def update_status(text, color):
        status_label.config(text=text)
        status_dot.config(fg=color)

    def start():
        if not app_state["region"] or app_state["running"]:
            return

        from datetime import datetime

        if not os.path.exists("logs"):
            os.makedirs("logs")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        app_state["session_log"] = os.path.join(
            "logs",
            f"session_{timestamp}.log"
        )

        app_state["logged_count"] = 0
        app_state["running"] = True

        start_btn.config(state="disabled")
        stop_btn.config(state="normal")

        update_status("Running...", "orange")
        update_tray("active", "Running")

        threading.Thread(
            target=logger_loop,
            args=(app_state["region"], update_status, app_state),
            daemon=True
        ).start()

    def stop():
        if not app_state["running"]:
            return

        app_state["running"] = False

        time.sleep(0.3)

        start_btn.config(state="normal")
        stop_btn.config(state="disabled")

        update_status("Stopped", "red")
        update_tray("stopped", "Stopped")

    def pick():
        was_running = app_state["running"]
        stop()

        region = select_region()
        save_region(region)
        app_state["region"] = region

        start_btn.config(state="normal")
        update_status("Region Selected", "cyan")

        if was_running:
            start()

    def on_close():
        if tray_icon:
            tray_icon.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=5)

    start_btn = tk.Button(button_frame, text="Start",
                          width=15, command=start,
                          bg="#2d2d2d", fg="white",
                          activebackground="#3a3a3a",
                          relief="flat",
                          state="disabled")
    start_btn.pack(pady=4)

    stop_btn = tk.Button(button_frame, text="Stop",
                         width=15, command=stop,
                         bg="#2d2d2d", fg="white",
                         activebackground="#3a3a3a",
                         relief="flat",
                         state="disabled")
    stop_btn.pack(pady=4)

    lower_frame = tk.Frame(root, bg="#1e1e1e")
    lower_frame.pack(pady=15)

    tk.Button(lower_frame, text="Select Chat Box Area",
              width=22, command=pick,
              bg="#2d2d2d", fg="white",
              activebackground="#3a3a3a",
              relief="flat").pack(pady=5)

    tk.Button(lower_frame, text="Minimize to Tray",
              width=22, command=root.withdraw,
              bg="#2d2d2d", fg="white",
              activebackground="#3a3a3a",
              relief="flat").pack(pady=5)

    if not app_state["region"]:
        root.after(400, pick)
    else:
        start_btn.config(state="normal")

    setup_tray(root)

    root.mainloop()

if __name__ == "__main__":
    main()

import re
import subprocess
import threading
import tkinter as tk

import hid


def get_primary_monitor_geometry():
    xrandr_output = subprocess.check_output("xrandr --query", shell=True).decode()
    match = re.search(r"primary (\d+)x(\d+)\+(\d+)\+(\d+)", xrandr_output)
    if match:
        width, height, offset_x, offset_y = map(int, match.groups())
        return width, height, offset_x, offset_y
    else:
        return None


# === CONFIG ===
VID = 0x359B
PID = 0x0010
RAW_EPSIZE = 32

# === GUI Setup ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.0)  # start transparent
# root.geometry("2560x5+0+1435")  # full width, 5px tall, position at bottom#
geom = get_primary_monitor_geometry()
if geom:
    w, h, x, y = geom
    bar_height = 5
    y_pos = y + h - bar_height
    root.geometry(f"{w}x{bar_height}+{x}+{y_pos}")
canvas = tk.Canvas(root, width=2560, height=5, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)
bar = canvas.create_rectangle(0, 0, 2560, 5, fill="", outline="")


# HID SETUP

device_path = None

for d in hid.enumerate():
    if d["vendor_id"] == VID and d["product_id"] == PID and d["usage_page"] == 0xFF60:
        device_path = d["path"]
        break

if not device_path:
    raise RuntimeError("Raw HID device not found!")


def update_bar_color(layer):
    if layer == 1:
        root.attributes("-alpha", 1.0)
        canvas.configure(bg="#FF0000")
    else:
        root.attributes("-alpha", 0.0)


# === HID Listener Thread ===
def hid_listener():
    with hid.Device(path=device_path) as h:
        print(f"Connected to {h.product} (raw HID)")
        while True:
            try:
                data = h.read(RAW_EPSIZE, timeout=100)
                if data:
                    if data[0] == 0x01:
                        layer = data[1]
                        print(f"Layer: {data}")
                        root.after(0, update_bar_color, layer)
            except OSError as e:
                print("HID device disconnected:", e)
                break
            except Exception as e:
                print("HID thread error:", e)
                break


threading.Thread(target=hid_listener, daemon=True).start()

# === Run the GUI ===
root.mainloop()

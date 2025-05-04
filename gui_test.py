import threading
import tkinter as tk

import hid

# === CONFIG ===
VID = 0x359B
PID = 0x0010
RAW_EPSIZE = 32

# === GUI Setup ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.0)  # start transparent
root.geometry("1920x5+0+1075")  # full width, 5px tall, position at bottom
canvas = tk.Canvas(root, width=1920, height=5, highlightthickness=0, bd=0)
canvas.pack()
bar = canvas.create_rectangle(0, 0, 1920, 5, fill="", outline="")


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
        canvas.itemconfig(bar, fill="#FF0000")
    else:
        root.attributes("-alpha", 0.0)


# === HID Listener Thread ===
def hid_listener():
    with hid.Device(path=device_path) as h:
        print(f"Connected to {h.product} (raw HID)")
        while True:
            data = h.read(32)
            if data:
                print(f"Layer update: {data}")
                if data[0] == 0x01:
                    layer = data[1]
                    print(f"Layer: {data}")
                    root.after(0, update_bar_color, layer)


threading.Thread(target=hid_listener, daemon=True).start()

# === Run the GUI ===
root.mainloop()

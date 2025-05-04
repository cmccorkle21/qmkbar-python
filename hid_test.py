import hid

device_path = None

for d in hid.enumerate():
    if d['vendor_id'] == 0x3297 and d['product_id'] == 0x1969 and d['usage_page'] == 0xff60:
        device_path = d['path']
        break

if not device_path:
    raise RuntimeError("Raw HID device not found!")

with hid.Device(path=device_path) as h:
    print(f'Connected to {h.product} (raw HID)')
    while True:
        data = h.read(32)
        if data:
            print(f"Layer update: {data}")
            if data[0] == 0x01:
                print(f"Layer: {data[1]}")

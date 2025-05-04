import hid

for d in hid.enumerate():
    print(f"{d['vendor_id']:04x}:{d['product_id']:04x} | {d['interface_number']} | {d['usage_page']:04x} | {d['product_string']}")

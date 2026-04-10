import openpyxl

wb = openpyxl.Workbook()

# Devices Sheet
ws_devices = wb.active
ws_devices.title = "Devices"
ws_devices.append(["Device Name", "Device Type", "Status"])
ws_devices.append(["SW-01", "Switch", "active"])
ws_devices.append(["SW-02", "Switch", "active"]) 
ws_devices.append(["SW-03", "Switch", "offline"]) # Scoped group consistency failure
ws_devices.append(["FW-01", "Firewall", "offline"]) # Not a Switch, so shouldn't trigger scoped rule!

wb.save("test_config_driven_data.xlsx")
print("test_config_driven_data.xlsx generated")

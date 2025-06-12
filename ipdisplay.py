import tkinter as tk
from tkinter import messagebox
import psutil
import socket
import subprocess

# --------------------------
# Function: test_wan_dns
# --------------------------
# Pings 8.8.8.8 to test WAN connectivity and google.com to test DNS resolution.
def test_wan_dns():
    try:
        result_ping_ip = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", "8.8.8.8"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW
        )
        wan_status = "Online" if result_ping_ip.returncode == 0 else "Offline"
    except Exception:
        wan_status = "Error"

    try:
        result_ping_dns = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", "google.com"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW
        )
        dns_status = "Working" if result_ping_dns.returncode == 0 else "Not working"
    except Exception:
        dns_status = "Error"

    return wan_status, dns_status

# --------------------------
# Function: get_network_info
# --------------------------
# Gathers network info for adapters exactly named "Wi-Fi", "wifi", or "ethernet".
# Displays Internet connection status and for each adapter shows the IPv4 address and MAC.
def get_network_info():
    info = ""
    wan_status, dns_status = test_wan_dns()
    info += f"Internet Connection: {wan_status}\nDNS Resolution (8.8.8.8): {dns_status}\n"
    
    net_status = psutil.net_if_stats()
    for interface, addrs in psutil.net_if_addrs().items():
        if interface.lower() in ["wi-fi", "wifi", "ethernet"]:
            status = "Connected" if net_status.get(interface, None) and net_status[interface].isup else "Disconnected"
            info += f"\n=== {interface.upper()} ({status}) ===\n"
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    info += f"  IPv4: {addr.address}\n"
                elif addr.family == psutil.AF_LINK:
                    info += f"  MAC: {addr.address}\n"
    return info.strip()

# --------------------------
# Function: update_info
# --------------------------
# Updates the text widget with the latest network information every 5 seconds.
def update_info():
    text_widget.config(state=tk.NORMAL)  # Enable text widget for updating
    text_widget.delete(1.0, tk.END)  # Clear existing content
    text_widget.insert(tk.END, get_network_info())  # Insert the new info
    text_widget.config(state=tk.DISABLED)  # Disable it after updating
    root.after(5000, update_info)  # Refresh every 5 seconds

# --------------------------
# Function: open_adapter_settings
# --------------------------
# Opens a settings window for the specified adapter (Wi-Fi or Ethernet)
# to allow setting to DHCP or configuring a static IP.
def open_adapter_settings(adapter):
    settings_window = tk.Toplevel(root)
    settings_window.title(f"{adapter} Settings")
    
    def set_dhcp():
        try:
            subprocess.run(
                ["netsh", "interface", "ip", "set", "address", f"name={adapter}", "source=dhcp"],
                check=True
            )
            subprocess.run(
                ["netsh", "interface", "ip", "set", "dns", f"name={adapter}", "source=dhcp"],
                check=True
            )
            messagebox.showinfo("Success", f"{adapter} set to DHCP successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # Button to set adapter to DHCP
    dhcp_button = tk.Button(settings_window, text="Set DHCP", command=set_dhcp)
    dhcp_button.pack(padx=10, pady=5, fill="x")
    
    def open_static_config():
        static_window = tk.Toplevel(settings_window)
        static_window.title(f"{adapter} Static Configuration")
        
        tk.Label(static_window, text="IP Address:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ip_entry = tk.Entry(static_window)
        ip_entry.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(static_window, text="Subnet Mask:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        mask_entry = tk.Entry(static_window)
        mask_entry.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(static_window, text="Default Gateway:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        gateway_entry = tk.Entry(static_window)
        gateway_entry.grid(row=2, column=1, padx=5, pady=2)
        
        tk.Label(static_window, text="DNS:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        dns_entry = tk.Entry(static_window)
        dns_entry.grid(row=3, column=1, padx=5, pady=2)
        
        def apply_static():
            ip = ip_entry.get().strip()
            mask = mask_entry.get().strip()
            gateway = gateway_entry.get().strip()
            dns = dns_entry.get().strip()
            if not ip or not mask:
                messagebox.showerror("Error", "IP Address and Subnet Mask are required.")
                return
            try:
                subprocess.run(
                    ["netsh", "interface", "ip", "set", "address", f"name={adapter}", "static", ip, mask, gateway, "1"],
                    check=True
                )
                subprocess.run(
                    ["netsh", "interface", "ip", "set", "dns", f"name={adapter}", "static", dns, "primary"],
                    check=True
                )
                messagebox.showinfo("Success", f"{adapter} set to static IP successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Button to apply the static IP configuration
        apply_button = tk.Button(static_window, text="Apply", command=apply_static)
        apply_button.grid(row=4, column=0, columnspan=2, pady=5)
    
    # Button to open static configuration window
    static_button = tk.Button(settings_window, text="Set Static", command=open_static_config)
    static_button.pack(padx=10, pady=5, fill="x")

# --------------------------
# Main Application Window Setup
# --------------------------
root = tk.Tk()
root.title("Network Info")
root.geometry("350x250")  # Set fixed window size

# Create a text widget to display network info.
# Using pack with expand=False ensures the text widget only takes the space it needs,
# removing extra space underneath the last line of adapter info.

# Create a Text widget to display network info.
text_widget = tk.Text(root, font=("Georgia", 12, "bold"), padx=10, pady=10, bg="#f0f0f0", fg="black", wrap="word", height=10, width=30)
text_widget.pack(side="top", fill="both", expand=True)

# Disable the Text widget to prevent user interaction
text_widget.config(state=tk.DISABLED)

#text_widget = tk.Label(root, text="test", font=("Georgia bold", 12), padx=10, pady=10, bg="#f0f0f0", anchor="w", justify="left")
#text_widget.pack(side="top", fill="x")

# Create a frame for the settings buttons at the bottom.
button_frame = tk.Frame(root)
button_frame.pack(side="bottom", fill="x", padx=10, pady=5)

# Button for Wi-Fi adapter settings
wifi_button = tk.Button(button_frame, text="Wi-Fi Settings", command=lambda: open_adapter_settings("Wi-Fi"))
wifi_button.pack(side="left", padx=5)

# Button for Ethernet adapter settings
ethernet_button = tk.Button(button_frame, text="Ethernet Settings", command=lambda: open_adapter_settings("Ethernet"))
ethernet_button.pack(side="left", padx=5)

update_info()
root.mainloop()

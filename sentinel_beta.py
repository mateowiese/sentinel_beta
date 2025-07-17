
# Sentinel Beta v0.1
# Electric Body Protection Scanner (Windows-only for now)
# Scans running programs, detects high EMF-risk software, allows manual reset
# Requirements: psutil, tkinter (preinstalled), socket, subprocess

import psutil
import socket
import subprocess
import tkinter as tk
from tkinter import messagebox

# --- Helper Functions ---
def is_wifi_enabled():
    try:
        result = subprocess.check_output("netsh interface show interface", shell=True).decode()
        return "Wi-Fi" in result and "Connected" in result
    except:
        return False

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_info'].rss / (1024 * 1024)  # in MB
            processes.append((proc.info['name'], cpu, mem))
        except:
            continue
    return sorted(processes, key=lambda x: x[1], reverse=True)

def scan_programs():
    processes = get_running_processes()
    harmful = []
    for name, cpu, mem in processes:
        if cpu > 10 or mem > 200:
            harmful.append((name, cpu, mem))
    return harmful

def perform_energy_reset():
    try:
        subprocess.call("netsh interface set interface \"Wi-Fi\" admin=disable", shell=True)
        messagebox.showinfo("Reset", "Wi-Fi disabled. Now rest and ground.")
    except:
        messagebox.showwarning("Error", "Could not disable Wi-Fi.")

# --- UI ---
class SentinelApp:
    def __init__(self, master):
        self.master = master
        master.title("Sentinel Beta – Electric Body Scanner")

        self.label = tk.Label(master, text="🧠 Scan Results:", font=('Arial', 14))
        self.label.pack(pady=10)

        self.text = tk.Text(master, width=60, height=15)
        self.text.pack()

        self.scan_button = tk.Button(master, text="Scan for Energy-Draining Programs", command=self.run_scan)
        self.scan_button.pack(pady=5)

        self.wifi_label = tk.Label(master, text="Wi-Fi Status: Unknown", fg="gray")
        self.wifi_label.pack(pady=5)

        self.reset_button = tk.Button(master, text="Perform Energy Reset (Disable Wi-Fi)", command=perform_energy_reset)
        self.reset_button.pack(pady=5)

        self.update_wifi_status()

    def run_scan(self):
        self.text.delete('1.0', tk.END)
        harmful = scan_programs()
        if harmful:
            for name, cpu, mem in harmful:
                self.text.insert(tk.END, f"⚠️ {name} – CPU: {cpu}% | Memory: {mem:.1f}MB\n")
        else:
            self.text.insert(tk.END, "✅ No major energy-draining processes found.\n")

    def update_wifi_status(self):
        if is_wifi_enabled():
            self.wifi_label.config(text="Wi-Fi Status: Connected ⚠️ (High EMF risk)", fg="red")
        else:
            self.wifi_label.config(text="Wi-Fi Status: Disabled ✅ (Low EMF)", fg="green")

# --- Launch App ---
def main():
    root = tk.Tk()
    app = SentinelApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

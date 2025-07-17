
# Sentinel Beta v0.6 – Stealth Process Detection + Safe End Button

import psutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import os
import datetime

try:
    import win32gui
    import win32process
    import win32con
except ImportError:
    win32gui = None
    win32process = None
    win32con = None

known_distracting_apps = ["chrome.exe", "discord.exe", "tiktok.exe", "spotify.exe"]
known_distracting_sites = ["tiktok", "instagram", "twitter", "reddit", "youtube shorts"]
LOG_FILE = "stimulus_log.txt"

system_paths = ["C:\Windows", "C:\Program Files", "C:\Program Files (x86)"]

# --- Utility Functions ---
def is_wifi_enabled():
    try:
        result = subprocess.check_output("netsh interface show interface", shell=True).decode()
        return "Wi-Fi" in result and "Connected" in result
    except:
        return False

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'exe']):
        try:
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_info'].rss / (1024 * 1024)
            pid = proc.info['pid']
            name = proc.info['name']
            user = proc.info['username']
            exe_path = proc.info['exe'] or ""
            processes.append((pid, name, cpu, mem, user, exe_path))
        except:
            continue
    return sorted(processes, key=lambda x: x[2], reverse=True)

def calculate_disruption_score(name, cpu, mem):
    score = 0
    if name.lower() in known_distracting_apps:
        score += 30
    if cpu > 15:
        score += 15
    if mem > 200:
        score += 15
    return min(score, 100)

def is_safe_to_kill(proc):
    exe = proc.info.get('exe') or ""
    username = proc.info.get('username') or ""
    return not any(p in exe for p in system_paths) and "system" not in username.lower()

def get_active_websites():
    titles = []
    if win32gui:
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if any(browser in title.lower() for browser in ["chrome", "edge", "firefox"]):
                    titles.append(title.lower())
        win32gui.EnumWindows(callback, None)
    return titles

def log_results(log_text):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
")
        f.write(log_text + "

")

# --- GUI ---
class SentinelApp:
    def __init__(self, master):
        self.master = master
        master.title("Sentinel Beta v0.6 – Stealth Monitor")
        master.configure(bg="#eaf1fb")

        self.label = tk.Label(master, text="🕵️ Digital Stimulus & Stealth Scan", font=('Arial', 16, 'bold'), bg="#eaf1fb")
        self.label.pack(pady=(15, 5))

        self.text = tk.Text(master, width=95, height=26, bg="#ffffff", fg="#223344", font=('Courier New', 9), relief=tk.FLAT)
        self.text.pack(padx=10, pady=5)

        self.scan_button = tk.Button(master, text="🌞 Scan Now", command=self.run_scan, bg="#cdeccd", fg="#2e5c2e", font=('Arial', 11, 'bold'))
        self.scan_button.pack(pady=6)

        self.reset_button = tk.Button(master, text="🛑 Energy Reset (Disable Wi-Fi)", command=perform_energy_reset, bg="#ffcccc", fg="#550000", font=('Arial', 10, 'bold'))
        self.reset_button.pack(pady=5)

        self.wifi_label = tk.Label(master, text="Wi-Fi Status: Unknown", bg="#eaf1fb", fg="#555555")
        self.wifi_label.pack(pady=3)

        self.footer = tk.Label(master, text="Your sunlight is sacred.", font=('Arial', 9, 'italic'), bg="#eaf1fb", fg="#445566")
        self.footer.pack(pady=10)

        self.update_wifi_status()

    def end_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
            messagebox.showinfo("Process Terminated", f"Process {p.name()} was safely ended.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_scan(self):
        self.text.delete('1.0', tk.END)
        results = get_running_processes()
        websites = get_active_websites()
        log_buffer = ""

        self.text.insert(tk.END, "🧠 Stimulus Load Scan:

")
        for pid, name, cpu, mem, user, exe in results:
            score = calculate_disruption_score(name, cpu, mem)
            safe = not any(p in exe for p in system_paths) and "system" not in (user or '').lower()
            tag = "Safe to End" if safe else "System"
            line = f"{name:<22} | CPU: {cpu:>5.1f}% | Mem: {mem:>6.1f}MB | {tag}"
            if score >= 60:
                line += " ⚠️"
            line += "
"
            self.text.insert(tk.END, line)
            log_buffer += line

        self.text.insert(tk.END, "
🔍 Stealth Candidates:

")
        hidden_found = False
        for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
            try:
                if not any(win32gui.GetWindowText(w).strip() for w in win32gui.EnumWindows(lambda hwnd, _: hwnd, None)):
                    if p.info['cpu_percent'] > 2:
                        hidden_found = True
                        self.text.insert(tk.END, f"Hidden Activity: {p.info['name']} (PID {p.info['pid']}) ⚠️
")
                        log_buffer += f"Hidden Activity: {p.info['name']} (PID {p.info['pid']})
"
            except:
                continue
        if not hidden_found:
            self.text.insert(tk.END, "No stealthy apps found.
")

        if websites:
            self.text.insert(tk.END, "
🌐 Active Sites:

")
            for w in websites:
                flag = any(kw in w for kw in known_distracting_sites)
                symbol = "⚠️" if flag else ""
                self.text.insert(tk.END, f"{w[:70]} {symbol}
")

        log_results(log_buffer)

    def update_wifi_status(self):
        if is_wifi_enabled():
            self.wifi_label.config(text="Wi-Fi Status: Connected ⚠️ (EMF active)", fg="red")
        else:
            self.wifi_label.config(text="Wi-Fi Status: Disabled ✅", fg="green")

# --- Wi-Fi reset ---
def perform_energy_reset():
    try:
        subprocess.call("netsh interface set interface "Wi-Fi" admin=disable", shell=True)
        messagebox.showinfo("Reset", "Wi-Fi disabled. Now rest and ground.")
    except:
        messagebox.showwarning("Error", "Could not disable Wi-Fi.")

# --- Main Entry ---
def main():
    root = tk.Tk()
    root.geometry("860x680")
    app = SentinelApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

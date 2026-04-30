import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import webbrowser
import os 
import platform
import socket
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import urlparse, parse_qs

# -------------------------------
# VOLUME CONTROL (pycaw)
# -------------------------------
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

def decrease_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 23, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.01), None)

def increase_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 23, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.01), None)

# -------------------------------
# EXTRA ACTIONS
# -------------------------------

def close_program():
    root.destroy()

def open_firefox():
    os.system("start firefox") if platform.system() == "Windows" else os.system("firefox &")

def open_spotify():
    os.system("start spotify") if platform.system() == "Windows" else os.system("spotify &")

def shutdown_device():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    else:
        os.system("shutdown now")

# -------------------------------
# CUSTOM HTTP HANDLER
# -------------------------------

class ActionHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/action":
            params = parse_qs(parsed.query)
            cmd = params.get("cmd", [""])[0]

            if cmd == "increase":
                increase_volume()
            elif cmd == "decrease":
                decrease_volume()
            elif cmd == "close":
                close_program()
            elif cmd == "firefox":
                open_firefox()
            elif cmd == "spotify":
                open_spotify()
            elif cmd == "shutdown":
                shutdown_device()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        return super().do_GET()

# -------------------------------
# TKINTER WINDOW SETUP
# -------------------------------

root = tk.Tk()
root.title("10 Full-Screen Blocks")

system = platform.system()
if system == "Windows":
    root.state("zoomed")
elif system == "Linux":
    root.attributes("-zoomed", True)
else:
    root.attributes("-fullscreen", True)

root.configure(bg="black")

# -------------------------------
# START LOCAL WEB SERVER
# -------------------------------

def start_server():
    os.chdir(os.getcwd())
    with TCPServer(("", 8000), ActionHandler) as httpd:
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# -------------------------------
# GET LOCAL IP ADDRESS
# -------------------------------

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

html_filename = "webpage.html"
html_url = f"http://{local_ip}:8000/{html_filename}"
print(html_url)
# -------------------------------
# GENERATE QR CODE
# -------------------------------

qr_img = qrcode.make(html_url)
qr_img.save("qr_temp.png")
qr_photo = ImageTk.PhotoImage(Image.open("qr_temp.png"))

# -------------------------------
# LAYOUT: 60% LEFT, 40% RIGHT
# -------------------------------

root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=1)

# -------------------------------
# RIGHT SIDEBAR
# -------------------------------

sidebar = tk.Frame(root, bg="purple", bd=4, relief="solid")
sidebar.grid(row=0, column=1, sticky="nsew")

qr_label = tk.Label(sidebar, image=qr_photo, bg="white")
qr_label.pack(pady=40)

qr_text = tk.Label(sidebar, text="QR CODE", fg="black", bg="white",
                   font=("Arial", 28, "bold"))
qr_text.pack(pady=10)

# -------------------------------
# LEFT SIDE: COLOURED BARS
# -------------------------------

blocks_frame = tk.Frame(root, bg="black")
blocks_frame.grid(row=0, column=0, sticky="nsew")

colours = [
    "#ff4d4d", "#ffdb4d", "#5cd65c", "#4da6ff", "#b366ff", "#ff6666"
]

titles = [
    "Increase The Volume",
    "Decrease The Volume",
    "Close This Program",
    "Open Firefox",
    "Open Spotify",
    "Shutdown Device"
]

actions = [
    increase_volume,
    decrease_volume,
    close_program,
    open_firefox,
    open_spotify,
    shutdown_device
]

for i in range(6):
    blocks_frame.grid_rowconfigure(i, weight=1)

    block = tk.Frame(blocks_frame, bg=colours[i], bd=3, relief="solid")
    block.grid(row=i, column=0, sticky="nsew")

    block.grid_columnconfigure(0, weight=1)

    inner = tk.Frame(block, bg=colours[i])
    inner.grid(row=0, column=0, sticky="nsew")

    label = tk.Label(inner, text=titles[i], bg=colours[i], fg="black",
                     font=("Arial", 22, "bold"), anchor="w")
    label.pack(side="left", padx=20)

    tk.Button(inner, text="Run", font=("Arial", 16),
              command=actions[i]).pack(side="right", padx=20)

root.mainloop()

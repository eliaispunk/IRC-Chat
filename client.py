import random
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

HOST = '127.0.0.1'
PORT = 6667
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

root = tk.Tk()
root.withdraw()

username = simpledialog.askstring("Username", "Enter your username:", parent=root)
if not username:
    client.close()
    root.destroy()
    exit()

client.sendall(username.encode())
response = client.recv(1024).decode()
if response == "VARATTU":
    messagebox.showerror("Error", "That username is already in use.")
    client.close()
    root.destroy()
    exit()

if response != "OK":
    messagebox.showerror("Error", "The server did not return a valid response.")
    client.close()
    root.destroy()
    exit()

# The server waits for READY before sending history and the join notice.
client.sendall("READY".encode())

root.deiconify()
root.title(f"Chat - {username}")
root.geometry("640x480")
root.minsize(320, 200)

BG_COLOR = "#2b2b2b"
FG_COLOR = "#f1f1f1"
ENTRY_BG = "#3c3f41"
BUTTON_BG = "#4e5254"
BUTTON_ACTIVE = "#5c6164"

USER_COLORS = [
    "#80cbc4", "#ffcc80", "#ef9a9a", "#b39ddb",
    "#90caf9", "#c5e1a5", "#f48fb1", "#fff59d",
    "#80deea", "#ce93d8", "#ffab91", "#a5d6a7",
]
random.shuffle(USER_COLORS)
username_colors = {}
username_tags = {}
available_colors = USER_COLORS.copy()

root.configure(bg=BG_COLOR)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1, minsize=40)

chat_area = scrolledtext.ScrolledText(
    root, state='disabled', wrap=tk.WORD, height=1,
    bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
    font=("Consolas", 10)
)
chat_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

def ensure_user_style(name):
    if name not in username_colors:
        if available_colors:
            color = available_colors.pop()
        else:
            color = random.choice(USER_COLORS)
        tag = f"user_{len(username_tags)}"
        username_colors[name] = color
        username_tags[name] = tag
        chat_area.tag_configure(tag, foreground=color, font=("Consolas", 10, "bold"))
    return username_tags[name]

def append_chat_line(line):
    if not line:
        return

    username_in_line = None
    message_part = line

    if ": " in line:
        username_in_line, message_part = line.split(": ", 1)
        message_part = ": " + message_part
    elif " joined channel " in line or " left channel " in line:
        username_in_line, message_part = line.split(" ", 1)
        message_part = " " + message_part

    chat_area.config(state='normal')
    if username_in_line:
        chat_area.insert(tk.END, username_in_line, ensure_user_style(username_in_line))
        chat_area.insert(tk.END, message_part)
    else:
        chat_area.insert(tk.END, line)
    chat_area.insert(tk.END, "\n")
    chat_area.config(state='disabled')
    chat_area.yview(tk.END)

msg_entry = tk.Entry(
    root, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
    font=("Consolas", 10)
)
msg_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

def send_message():
    msg = msg_entry.get().strip()
    if msg:
        client.sendall((msg + "\n").encode())

        if not msg.startswith("/join "):
            append_chat_line(f"{username}: {msg}")

        msg_entry.delete(0, tk.END)

        if msg.lower() == 'exit':
            root.quit()

send_button = tk.Button(
    root, text="Send", command=send_message,
    bg=BUTTON_BG, fg=FG_COLOR, activebackground=BUTTON_ACTIVE,
    font=("Consolas", 9)
)
send_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

def receive_messages():
    buffer = ""
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line and not line.startswith(f"{username}: "):
                    root.after(0, append_chat_line, line)
        except:
            break

    if buffer and not buffer.startswith(f"{username}: "):
        root.after(0, append_chat_line, buffer)

threading.Thread(target=receive_messages, daemon=True).start()
msg_entry.bind("<Return>", lambda event: send_message())

root.mainloop()
client.close()

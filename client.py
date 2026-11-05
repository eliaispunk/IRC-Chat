import random
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

try:
    import winsound
except ImportError:
    winsound = None

HOST = '127.0.0.1'
PORT = 6667
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

root = tk.Tk()
root.withdraw()

username = simpledialog.askstring("Käyttäjänimi", "Syötä käyttäjänimesi:", parent=root)
if not username:
    client.close()
    root.destroy()
    exit()

client.sendall(username.encode())
response = client.recv(1024).decode()
if response == "VARATTU":
    messagebox.showerror("Virhe", "Käyttäjänimi on jo varattu.")
    client.close()
    root.destroy()
    exit()

if response != "OK":
    messagebox.showerror("Virhe", "Palvelimelta ei saatu kelvollista vastausta.")
    client.close()
    root.destroy()
    exit()

# The server waits for READY before sending history and the join notice.
client.sendall("READY".encode())

root.deiconify()
root.title(f"IRC Chat - {username}")
root.geometry("720x520")
root.minsize(480, 360)

BG_COLOR = "#22272a"
PANEL_COLOR = "#2c3337"
CHAT_COLOR = "#171c1f"
FG_COLOR = "#d7dfdc"
MUTED_COLOR = "#9aa8a2"
ACCENT_COLOR = "#93b7a0"
ENTRY_COLOR = "#30383b"
BUTTON_COLOR = "#43554c"
BUTTON_ACTIVE = "#536b5f"

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

header = tk.Frame(root, bg=PANEL_COLOR, padx=14, pady=10)
header.pack(fill=tk.X, padx=10, pady=(10, 0))

title_label = tk.Label(
    header, text="IRC // CHAT", bg=PANEL_COLOR, fg=ACCENT_COLOR,
    font=("Consolas", 13, "bold")
)
title_label.pack(side=tk.LEFT)

sound_enabled = tk.BooleanVar(value=True)
sound_toggle = tk.Checkbutton(
    header, text="BLING", variable=sound_enabled,
    bg=PANEL_COLOR, fg=MUTED_COLOR, selectcolor=ENTRY_COLOR,
    activebackground=PANEL_COLOR, activeforeground=FG_COLOR,
    font=("Consolas", 8, "bold"), relief=tk.FLAT, borderwidth=0,
    cursor="hand2"
)
sound_toggle.pack(side=tk.RIGHT, padx=(12, 0))

account_label = tk.Label(
    header, text=f"CONNECTED AS  {username}", bg=PANEL_COLOR,
    fg=FG_COLOR, font=("Consolas", 9)
)
account_label.pack(side=tk.RIGHT)

chat_area = scrolledtext.ScrolledText(
    root, state='disabled', wrap=tk.WORD,
    bg=CHAT_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR,
    selectbackground=BUTTON_COLOR, relief=tk.FLAT, borderwidth=0,
    padx=12, pady=10, font=("Consolas", 10), spacing1=2, spacing3=2
)
chat_area.pack(padx=10, pady=8, fill=tk.BOTH, expand=True)

def ensure_user_style(name):
    if name not in username_colors:
        if available_colors:
            color = available_colors.pop()
        else:
            color = random.choice(USER_COLORS)
        tag = f"user_{len(username_colors)}"
        username_colors[name] = color
        username_tags[name] = tag
        chat_area.tag_configure(tag, foreground=color, font=("Consolas", 10, "bold"))
    return username_colors[name], username_tags[name]

account_label.configure(fg=ensure_user_style(username)[0])

hint_label = tk.Label(
    root, text="ENTER lähettää    •    /join #kanava vaihtaa kanavaa",
    bg=BG_COLOR, fg=MUTED_COLOR, anchor=tk.W,
    font=("Consolas", 8)
)
hint_label.pack(fill=tk.X, padx=12, pady=(0, 5))

entry_row = tk.Frame(root, bg=BG_COLOR)
entry_row.pack(fill=tk.X, padx=10, pady=(0, 10))

msg_entry = tk.Entry(
    entry_row, bg=ENTRY_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR,
    relief=tk.FLAT, borderwidth=0, font=("Consolas", 10)
)
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))

def play_bling():
    if not sound_enabled.get():
        return

    if winsound is None:
        root.bell()
        return

    def play_tones():
        try:
            winsound.Beep(880, 75)
            winsound.Beep(1175, 100)
        except RuntimeError:
            pass

    threading.Thread(target=play_tones, daemon=True).start()

def append_chat_line(line, play_sound=False):
    if not line:
        return

    username_in_line = None
    message_part = line
    is_chat_message = False

    if ": " in line:
        username_in_line, message_part = line.split(": ", 1)
        message_part = ": " + message_part
        is_chat_message = True
    elif " liittyi kanavalle " in line or " poistui kanavalta " in line:
        username_in_line, message_part = line.split(" ", 1)
        message_part = " " + message_part

    chat_area.config(state='normal')
    if username_in_line:
        _, user_tag = ensure_user_style(username_in_line)
        chat_area.insert(tk.END, username_in_line, user_tag)
        chat_area.insert(tk.END, message_part)
    else:
        chat_area.insert(tk.END, line)
    chat_area.insert(tk.END, "\n")
    chat_area.config(state='disabled')
    chat_area.yview(tk.END)

    # Only play for another user's chat message, not local echoes or join notices.
    if play_sound and is_chat_message and username_in_line != username:
        play_bling()

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
    entry_row, text="LÄHETÄ", command=send_message,
    bg=BUTTON_COLOR, fg=FG_COLOR, activebackground=BUTTON_ACTIVE,
    activeforeground=FG_COLOR, relief=tk.FLAT, borderwidth=0,
    padx=16, pady=7, font=("Consolas", 9, "bold"), cursor="hand2"
)
send_button.pack(side=tk.RIGHT)

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
                    root.after(0, append_chat_line, line, True)
        except:
            break

    if buffer and not buffer.startswith(f"{username}: "):
        root.after(0, append_chat_line, buffer, True)

threading.Thread(target=receive_messages, daemon=True).start()
msg_entry.bind("<Return>", lambda event: send_message())

root.mainloop()
client.close()

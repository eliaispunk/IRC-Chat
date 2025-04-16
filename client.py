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

username = simpledialog.askstring("Käyttäjänimi", "Syötä käyttäjänimesi:", parent=root)
if not username:
    exit()

client.sendall(username.encode())
response = client.recv(1024).decode()
if response == "VARATTU":
    messagebox.showerror("Virhe", "Käyttäjänimi on jo varattu.")
    root.destroy()
    exit()

root.deiconify()
root.title(f"Chat - {username}")
root.configure(bg='#2b2b2b')

BG_COLOR = "#2b2b2b"
FG_COLOR = "#f1f1f1"
ENTRY_BG = "#3c3f41"
BUTTON_BG = "#4e5254"
BUTTON_ACTIVE = "#5c6164"

chat_area = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, 
                                      bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

msg_entry = tk.Entry(root, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR)
msg_entry.pack(padx=10, pady=(0, 5), fill=tk.X)

send_button = tk.Button(root, text="Lähetä", command=lambda: send_message(),
                        bg=BUTTON_BG, fg=FG_COLOR, activebackground=BUTTON_ACTIVE)
send_button.pack(padx=10, pady=(0, 10), fill=tk.X)

def send_message():
    msg = msg_entry.get()
    if msg:
        client.sendall(msg.encode())

        if not msg.startswith("/join "):
            chat_area.config(state='normal')
            chat_area.insert(tk.END, f"{username}: {msg}\n")
            chat_area.config(state='disabled')
            chat_area.yview(tk.END)

        msg_entry.delete(0, tk.END)

        if msg.lower() == 'exit':
            root.quit()

def receive_messages():
    while True:
        try:
            msg = client.recv(1024)
            if not msg:
                break
            decoded = msg.decode()

            if not decoded.startswith(f"{username}:"):
                chat_area.config(state='normal')
                chat_area.insert(tk.END, decoded + '\n')
                chat_area.config(state='disabled')
                chat_area.yview(tk.END)

        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()
msg_entry.bind("<Return>", lambda event: send_message())

root.mainloop()
client.close()

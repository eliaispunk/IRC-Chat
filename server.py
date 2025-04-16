import socket
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6667

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}
user_channels = {}

def write_to_log(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chatlog.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def broadcast(msg, sender_conn=None, channel=None):
    if not channel:
        channel = user_channels.get(sender_conn, "#yleinen")
    write_to_log(f"{channel} | {msg}")
    for client in clients:
        if user_channels.get(client) == channel:
            try:
                client.sendall(msg.encode())
            except:
                pass

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    try:
        username = conn.recv(1024).decode().strip()
        if username in usernames.values():
            conn.sendall("VARATTU".encode())
            conn.close()
            return
        usernames[conn] = username
        clients.append(conn)
        user_channels[conn] = "#yleinen"

        welcome_msg = f"{username} liittyi kanavalle {user_channels[conn]}"
        print(welcome_msg)
        broadcast(welcome_msg, conn, user_channels[conn])

        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            decoded_msg = msg.decode().strip()

            if decoded_msg.startswith("/join "):
                new_channel = decoded_msg.split(" ", 1)[1]
                old_channel = user_channels[conn]
                user_channels[conn] = new_channel
                switch_msg = f"{usernames[conn]} siirtyi kanavalta {old_channel} kanavalle {new_channel}"
                print(switch_msg)
                broadcast(f"{usernames[conn]} poistui kanavalta {old_channel}", conn, old_channel)
                broadcast(f"{usernames[conn]} liittyi kanavalle {new_channel}", conn, new_channel)
            else:
                full_msg = f"{usernames[conn]}: {decoded_msg}"
                print(f"{user_channels[conn]} | {full_msg}")
                broadcast(full_msg, conn, user_channels[conn])

    except:
        pass
    finally:
        if conn in clients:
            clients.remove(conn)
        channel = user_channels.get(conn, "#yleinen")
        leave_msg = f"{usernames.get(conn, 'Tuntematon')} poistui kanavalta {channel}"
        print(leave_msg)
        broadcast(leave_msg, conn, channel)
        conn.close()
        usernames.pop(conn, None)
        user_channels.pop(conn, None)

print(f"Server listening on {HOST}:{PORT}...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
    thread.start()

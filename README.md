# IRC-Chat

A small Python chat application with a Tkinter desktop client and a TCP server. Users connect with a username, exchange messages in channels, and can view recent channel history when joining.

This is a custom chat application; it does not implement the IRC protocol.

## Requirements

- Python 3.6 or newer
- No third-party Python packages are required

## Run it

1. Open a terminal in the repository directory.
2. Start the server:

   ```bash
   python server.py
   ```

3. In another terminal, start a client:

   ```bash
   python client.py
   ```

4. Start additional clients by running `python client.py` again.

The client connects to `127.0.0.1:6667`, so the server and clients must currently run on the same computer. The server listens on TCP port `6667`.

## Using the chat

- Enter a username when prompted.
- Type a message and press Enter or click **Lähetä** to send it.
- Join or create a channel by sending `/join #channel-name`.
- New users start in `#yleinen`.
- The server keeps up to the ten most recent messages per channel in memory and sends that history when a user joins.
- Chat activity is appended to `chatlog.txt` in the server's current working directory.

A username can only be used by one connected client at a time. Usernames are not accounts: there are no passwords or login tokens.

## Current limitations

- The server only binds to localhost, so clients on other computers cannot connect as configured.
- Connections and messages are not encrypted.
- There is no password-based authentication or persistent account system.
- Channel history is held in memory and is lost when the server stops.
- The server and client use a simple custom TCP message exchange, not the standard IRC protocol.

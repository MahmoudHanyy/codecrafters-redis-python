import socket
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))  # add current file's directory to path
from db import Database

db = Database()  

def resp_bulk(msg: bytes) -> bytes:
    return b"$" + str(len(msg)).encode() + b"\r\n" + msg + b"\r\n"

async def handle_client(client_socket: socket.socket, loop: asyncio.AbstractEventLoop) -> None:
    while True:
        data = await loop.sock_recv(client_socket, 1024)
        if not data:
            break

        parts = data.split(b"\r\n")
        command = parts[2].upper()

        if command == b"PING":
            await loop.sock_sendall(client_socket, b"+PONG\r\n")

        elif command == b"ECHO":  
            await loop.sock_sendall(client_socket, resp_bulk(parts[4]))

        elif command == b"SET":
            key = parts[4]
            value = parts[6]
            expiry = None
            if len(parts) > 8 and parts[8].upper() in (b"EX", b"PX"):
                expiry = int(parts[10]) / 1000 if parts[8].upper() == b"PX" else int(parts[10]) 
            db.set(key, value, expire=expiry)
            await loop.sock_sendall(client_socket, b"+OK\r\n")

        elif command == b"GET":
            value = db.get(parts[4])
            response = resp_bulk(value) if value is not None else b"$-1\r\n"
            await loop.sock_sendall(client_socket, response)

        elif command == b"RPUSH":
            key = parts[4]
            values = parts[6::2]
            length = 0
            for value in values:
                length = db.rpush(key, value)
            await loop.sock_sendall(client_socket, b":" + str(length).encode() + b"\r\n")

        elif command == b"LPUSH":
            key = parts[4]
            values = parts[6::2]
            length = 0
            for value in values:
                length = db.lpush(key, value)
            await loop.sock_sendall(client_socket, b":" + str(length).encode() + b"\r\n")

        elif command == b"LRANGE":
            key = parts[4]
            start = int(parts[6])
            end = int(parts[8])
            values = db.lrange(key, start, end)
            response = b"*" + str(len(values)).encode() + b"\r\n"
            for value in values:
                response += resp_bulk(value)
            await loop.sock_sendall(client_socket, response)

        elif command == b"LLEN":
            key = parts[4]
            lst = db.get(key, [])
            length = len(lst) if isinstance(lst, list) else 0
            await loop.sock_sendall(client_socket, b":" + str(length).encode() + b"\r\n")

    client_socket.close()

async def main() -> None:
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.setblocking(False)
    loop = asyncio.get_event_loop()

    while True:
        client_socket, _ = await loop.sock_accept(server_socket)
        asyncio.create_task(handle_client(client_socket, loop))

if __name__ == "__main__":
    asyncio.run(main())
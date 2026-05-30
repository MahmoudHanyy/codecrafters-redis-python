import socket
import asyncio

async def handle_client(client_socket, loop):
    while True:
        data = await loop.sock_recv(client_socket, 1024)
        if not data:
            break
        parts = data.split(b"\r\n")
        command = parts[2].upper()

        if command == b"PING":
             await loop.sock_sendall(client_socket, b"+PONG\r\n")
        if command == b"ECHO":
            msg = parts[4]
            await loop.sock_sendall(client_socket, b"$" + str(len(msg)).encode() + b"\r\n" + msg + b"\r\n")
    client_socket.close()

async def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.setblocking(False) 
    loop = asyncio.get_event_loop()
    
    while True:
        client_socket, _ = await loop.sock_accept(server_socket)
        asyncio.create_task(handle_client(client_socket, loop)) 
        

if __name__ == "__main__":
    asyncio.run(main())
    
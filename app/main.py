import socket
import asyncio


async def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.setblocking(False) 
    loop = asyncio.get_event_loop()
    
    client_socket, _ = await loop.sock_accept(server_socket) 
    while True:
        data = await loop.sock_recv(client_socket, 1024)
        if not data:
            break
        await loop.sock_sendall(client_socket, b"+PONG\r\n")
    client_socket.close()


if __name__ == "__main__":
    asyncio.run(main())
import os
import socket
import socketserver
import threading
import json
from request_handler import RequestHandler
from database import Database
from dotenv import load_dotenv

PORT = 8000

load_dotenv()
db_path = os.getenv('DATABASE_PATH')
if not db_path:
    raise ValueError("DATABASE_PATH not set in environment variables")

db = Database(db_path)
handler = RequestHandler
handler.connect_database(db)


def start_http_server():
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\nServing at port {PORT}")
        httpd.serve_forever()


def handle_socket_client(conn, addr):
    print(f"Connected by {addr}")
    buffer = b""
    while True:
        db = conn.recv(1024)
        if not db:
            break
        buffer += db

    try:
        json_data = json.loads(buffer.decode('utf-8'))
        handler.add_data_to_db(json_data)
        conn.sendall(b"Data received and added to database")
    except json.JSONDecodeError:
        conn.sendall(b"Invalid JSON db")
    finally:
        conn.close()


def start_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", PORT + 1))
        s.listen()
        print(f"\nSocket server listening on port {PORT + 1}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_socket_client, args=(conn, addr))
            client_thread.start()


if __name__ == "__main__":
    http_server_thread = threading.Thread(target=start_http_server)
    socket_server_thread = threading.Thread(target=start_socket_server)

    http_server_thread.start()
    socket_server_thread.start()

    http_server_thread.join()
    socket_server_thread.join()

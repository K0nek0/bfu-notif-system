import os
import socket
import socketserver
import threading
from request_handler import RequestHandler
from database import Database
from dotenv import load_dotenv

HOST, PORT = "185.16.137.205", 8000

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


def start_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", PORT + 1))
        s.listen()
        print(f"\nSocket server listening on port {PORT + 1}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)


if __name__ == "__main__":
    http_server_thread = threading.Thread(target=start_http_server)
    socket_server_thread = threading.Thread(target=start_socket_server)

    http_server_thread.start()
    socket_server_thread.start()

    http_server_thread.join()
    socket_server_thread.join()

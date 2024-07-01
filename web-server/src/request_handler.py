import http.server
import os
import json
# import socket


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    _database = None

    @classmethod
    def connect_database(cls, database):
        cls._database = database

    def do_GET(self):
        if self.path == '/':
            self.path = os.path.join('..', 'pages', 'index.html')
        elif self.path == '/admin':
            self.path = os.path.join('..', 'pages', 'admin.html')
        elif self.path.startswith('/static/'):
            self.path = os.path.join('..', self.path[1:])
        # elif self.path == '/data':
        #     self.handle_data_request()
        #     return
        else:
            self.send_error(404, "File not found")
            return

        try:
            file_to_open = open(self.path, 'rb').read()
            self.send_response(200)
            if self.path.endswith('.html'):
                self.send_header('Content_type', 'text/html')
            elif self.path.endswith('.css'):
                self.send_header('Content_type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content_type', 'application/javascript')
            self.end_headers()
            self.wfile.write(file_to_open)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    # def do_POST(self):
    #     if self.path == '/newevent':
    #         self.handle_new_event()
    #     else:
    #         self.send_error(404, "File not found")
    #
    # def handle_new_event(self):
    #     content_length = int(self.headers['Content-Length'])
    #     post_data = self.rfile.read(content_length)
    #     event_data = json.loads(post_data.decode('utf-8'))
    #
    #     if RequestHandler._database:
    #         try:
    #             # Сохраняем событие в базу данных
    #             query = "INSERT INTO events (title, description, category, event_time) VALUES (?, ?, ?, ?)"
    #             RequestHandler._database.cursor.execute(query, (response_data['title'],
    #                                                             response_data['description'],
    #                                                             response_data['category'],
    #                                                             response_data['event_time']))
    #             RequestHandler._database.conn.commit()
    #
    #             # Отправляем данные Телеграм-боту через TCP-сокет
    #             self.send_to_telegram_bot(event_data)
    #
    #             self.send_response(200)
    #             self.send_header('Content-type', 'application/json')
    #             self.end_headers()
    #             self.wfile.write(json.dumps({"status": "success"}).encode())
    #         except Exception as e:
    #             self.send_error(500, f"Database error: {str(e)}")
    #     else:
    #         self.send_error(500, "Database not connected")
    # def add_user(self):
    #     try:
    #         query = "INSERT INTO telegram_subscribers (id, category) VALUES (?, ?)"
    #         RequestHandler._database.cursor.execute(query, (response_data['id'],
    #                                                         response_data['category']))
    #         RequestHandler._database.conn.commit()
    #
    #         self.send_response(200)
    #         self.send_header('Content-type', 'application/json')
    #         self.end_headers()
    #         self.wfile.write(json.dumps({"status": "success"}).encode())
    #
    #     except Exception as e:
    #         self.send_error(500, f"Database error: {str(e)}")

    # def send_to_telegram_bot(self, event_data):
    #     try:
    #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         sock.connect(('91.109.158.233', 9090))  # Телеграм-бот слушает на порту 9090
    #         message = json.dumps(event_data)
    #         sock.sendall(message.encode())
    #
    #         # Получаем ответ от Телеграм-бота
    #         response = sock.recv(1024).decode()
    #         print(f"Response from Telegram bot: {response}")
    #         sock.close()
    #     except Exception as e:
    #         print(f"Error sending data to Telegram bot: {str(e)}")

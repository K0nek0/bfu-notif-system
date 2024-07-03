import http.server
import os


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
            elif self.path.endswith('.ico'):
                self.send_header('Content_type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(file_to_open)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def add_event_to_db(json_data):
        query = "INSERT INTO events (title, description, category, event_time) VALUES (?, ?, ?, ?)"
        RequestHandler._database.cursor.execute(query, (json_data['title'],
                                                        json_data['description'],
                                                        json_data['category'],
                                                        json_data['event_time']))
        RequestHandler._database.conn.commit()

    def add_user_to_db(json_data):
        query = "INSERT OR IGNORE INTO telegram_users (user_id) VALUES (?)"
        RequestHandler._database.cursor.execute(query, (json_data['user_id'],))
        RequestHandler._database.conn.commit()

        query = "SELECT id FROM telegram_users WHERE user_id = ?"
        RequestHandler._database.cursor.execute(query, (json_data['user_id'],))
        user_db_id = RequestHandler._database.cursor.fetchone()[0]

        query = "SELECT id FROM categories WHERE category = ?"
        RequestHandler._database.cursor.execute(query, (json_data['category'],))
        category_db_id = RequestHandler._database.cursor.fetchone()[0]

        query = "INSERT OR IGNORE INTO user_categories (user_id, category_id) VALUES (?, ?)"
        RequestHandler._database.cursor.execute(query, (user_db_id, category_db_id))
        RequestHandler._database.conn.commit()

    def delete_user_from_db(json_data):
        query = "SELECT id FROM telegram_users WHERE user_id = ?"
        RequestHandler._database.cursor.execute(query, (json_data['user_id'],))
        user_db_id = RequestHandler._database.cursor.fetchone()[0]
        if user_db_id:
            query = "DELETE FROM user_categories WHERE user_id = ?"
            RequestHandler._database.cursor.execute(query, (user_db_id,))
            query = "DELETE FROM telegram_users WHERE id = ?"
            RequestHandler._database.cursor.execute(query, (user_db_id,))
            RequestHandler._database.conn.commit()

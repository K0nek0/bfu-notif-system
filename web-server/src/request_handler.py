import http.server
import json
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
        elif self.path == '/events':
            self.handle_get_events()
            return
        elif self.path == '/upcoming_events':
            self.handle_get_upcoming_events()
            return
        else:
            self.send_error(404, "File not found")
            return

        try:
            file_to_open = open(self.path, 'rb').read()
            self.send_response(200)
            if self.path.endswith('.html'):
                self.send_header('Content-Type', 'text/html')
            elif self.path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif self.path.endswith('.ico'):
                self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(file_to_open)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == '/new_event':
            self.handle_new_event()
        elif self.path == '/delete_event':
            self.handle_delete_event()
        else:
            self.send_error(404, "File not found")

    def handle_get_events(self):
        if RequestHandler._database:
            try:
                query = "SELECT * FROM events"
                RequestHandler._database.cursor.execute(query)
                events = RequestHandler._database.cursor.fetchall()

                result = [{
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "category_id": row[3],
                    "created_at": row[4],
                    "event_time": row[5]
                } for row in events]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_error(500, f"Database query error: {str(e)}")
        else:
            self.send_error(500, "Database not connected")

    def handle_get_upcoming_events(self):
        if RequestHandler._database:
            try:
                query = """
                        SELECT * FROM events
                        WHERE event_time >= datetime('now')
                        ORDER BY event_time ASC
                        LIMIT 10
                        """
                RequestHandler._database.cursor.execute(query)
                events = RequestHandler._database.cursor.fetchall()

                result = [{
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "category_id": row[3],
                    "created_at": row[4],
                    "event_time": row[5]
                } for row in events]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_error(500, f"Database query error: {str(e)}")
        else:
            self.send_error(500, "Database not connected")

    def handle_new_event(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        event_data = json.loads(post_data.decode('utf-8'))

        if RequestHandler._database:
            try:
                query = "INSERT INTO events (title, description, category_id, event_time) VALUES (?, ?, ?, ?)"
                RequestHandler._database.cursor.execute(query, (
                    event_data['title'],
                    event_data['description'],
                    event_data['category_id'],
                    event_data['event_time']
                ))
                RequestHandler._database.conn.commit()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_error(500, f"Database error: {str(e)}")
        else:
            self.send_error(500, "Database not connected")

    def handle_delete_event(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        delete_data = json.loads(post_data.decode('utf-8'))

        event_id = delete_data.get('id')

        if not event_id:
            self.send_error(400, "Missing event id")
            return

        if RequestHandler._database:
            try:
                query = "DELETE FROM events WHERE id = ?"
                RequestHandler._database.cursor.execute(query, (event_id,))
                RequestHandler._database.conn.commit()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "event deleted"}).encode())
            except Exception as e:
                self.send_error(500, f"Database error: {str(e)}")
        else:
            self.send_error(500, "Database not connected")

    def add_user_to_db(json_data):
        try:
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

        except Exception as e:
            print(f"Error when adding a user to the database: {e}")

    def delete_user_from_db(json_data):
        try:
            query = "SELECT id FROM telegram_users WHERE user_id = ?"
            RequestHandler._database.cursor.execute(query, (json_data['user_id'],))
            result = RequestHandler._database.cursor.fetchone()
            if result:
                user_db_id = result[0]

                query = "DELETE FROM user_categories WHERE user_id = ?"
                RequestHandler._database.cursor.execute(query, (user_db_id,))
                query = "DELETE FROM telegram_users WHERE id = ?"
                RequestHandler._database.cursor.execute(query, (user_db_id,))

                RequestHandler._database.conn.commit()
            else:
                pass

        except Exception as e:
            print(f"Error when deleting a user from the database: {e}")

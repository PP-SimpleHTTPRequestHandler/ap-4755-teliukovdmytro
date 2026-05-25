import json
from http.server import BaseHTTPRequestHandler, HTTPServer

INITIAL_USER = {
    "id": 1,
    "username": "theUser",
    "firstName": "John",
    "lastName": "James",
    "email": "john@email.com",
    "password": "12345"
}

USERS_LIST = [INITIAL_USER.copy()]

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if body is not None:
            self.wfile.write(json.dumps(body).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])
        return json.loads(self.rfile.read(content_length).decode('utf-8'))

    def do_GET(self):
        if self.path == "/reset":
            global USERS_LIST
            USERS_LIST = [INITIAL_USER.copy()]
            return self._set_response(200, {})

        if self.path == "/users":
            return self._set_response(200, USERS_LIST)

        if self.path.startswith("/user/"):
            username = self.path.split("/")[-1]
            for user in USERS_LIST:
                if user.get("username") == username:
                    return self._set_response(200, user)
            return self._set_response(400, {"error": "User not found"})

        self._set_response(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == "/user/createWithList":
            try:
                data_list = self._pars_body()
                required_fields = ["id", "username", "firstName", "lastName", "email", "password"]
                
                for item in data_list:
                    if not all(field in item for field in required_fields):
                        return self._set_response(400, {})
                    if any(user["id"] == item["id"] for user in USERS_LIST):
                        return self._set_response(400, {})
                
                for item in data_list:
                    USERS_LIST.append(item)
                return self._set_response(201, data_list)
            except Exception:
                return self._set_response(400, {})

        if self.path == "/user":
            try:
                data = self._pars_body()
                required_fields = ["id", "username", "firstName", "lastName", "email", "password"]
                
                if not all(field in data for field in required_fields):
                    return self._set_response(400, {})
                
                if any(user["id"] == data["id"] for user in USERS_LIST):
                    return self._set_response(400, {})
                
                USERS_LIST.append(data)
                return self._set_response(201, data)
            except Exception:
                return self._set_response(400, {})

        self._set_response(404, {"error": "Not Found"})

    def do_PUT(self):
        if self.path.startswith("/user/"):
            try:
                user_id = int(self.path.split("/")[-1])
            except ValueError:
                return self._set_response(400, {"error": "Invalid ID"})

            try:
                data = self._pars_body()
                required_fields = ["username", "firstName", "lastName", "email", "password"]
                
                if not all(field in data for field in required_fields):
                    return self._set_response(400, {"error": "not valid request data"})
                
                for user in USERS_LIST:
                    if user["id"] == user_id:
                        user.update(data)
                        return self._set_response(200, user)
                
                return self._set_response(404, {"error": "User not found"})
            except Exception:
                return self._set_response(400, {"error": "not valid request data"})

        self._set_response(404, {"error": "Not Found"})

    def do_DELETE(self):
        if self.path.startswith("/user/"):
            try:
                user_id = int(self.path.split("/")[-1])
                global USERS_LIST
                initial_len = len(USERS_LIST)
                USERS_LIST = [user for user in USERS_LIST if user["id"] != user_id]
                
                if len(USERS_LIST) < initial_len:
                    return self._set_response(200, {})
                else:
                    return self._set_response(404, {"error": "User not found"})
            except ValueError:
                return self._set_response(400, {"error": "Invalid ID"})

        self._set_response(404, {"error": "Not Found"})

def run(host="localhost", port=8765):
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Сервер запущено на http://{host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

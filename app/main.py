# Uncomment this to pass the first stage
import socket
import threading

echo = "/echo/"
user_agent = "/user-agent"


def parse_http_request(request_data):
    request = {"headers": {}}
    lines = request_data.decode('utf-8').splitlines()
    method, path, version = lines[0].split()
    for line in lines[1:]:
        line = line.strip()
        if line != "":
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key:
                request["headers"][key.lower()] = value
    request['method'] = method
    request['path'] = path
    request['version'] = version
    return request


def create_http_response(status_code, status_message, content="", content_type="text/html"):
    # HTTP response
    response = f"HTTP/1.1 {status_code} {status_message}\r\n"
    response += f"Content-Type: {content_type}\r\n"  # "; charset=utf-8\r\n"
    response += f"Content-Length: {len(content)}\r\n"
    response += "\r\n"  # blank line to indicate the end of headers
    response += content
    return response.encode("utf-8")


def handle_client(client_socket, address):
    data = client_socket.recv(4096)
    if data:
        request = parse_http_request(data)
        path = request['path']
        if path == "/" or path == "" or path is None:
            client_socket.sendall(create_http_response(200, "OK"))
        elif path.startswith(echo):
            content = path[len(echo):]
            content_type = "text/plain"
            client_socket.sendall(create_http_response(200, "OK", content, content_type))
        elif path.startswith(user_agent):
            # very much the happy path here.
            content = request["headers"]["user-agent"]
            content_type = "text/plain"
            client_socket.sendall(create_http_response(200, "OK", content, content_type))
        else:
            client_socket.sendall(create_http_response(404, "Not Found", path))
    else:
        client_socket.sendall(create_http_response(200, "OK"))
    client_socket.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()  # wait for client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()


if __name__ == "__main__":
    main()

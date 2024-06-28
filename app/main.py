# Uncomment this to pass the first stage
import socket


def parse_http_request(request_data):
    lines = request_data.decode('utf-8').splitlines()
    method, path, version = lines[0].split()
    return method, path, version


def create_http_response(status_code, status_message, content=""):
    # HTTP response
    response = f"HTTP/1.1 {status_code} {status_message}\r\n"
    # response += "Content-Type: text/html; charset=utf-8\r\n"
    # response += f"Content-Length: {len(content)}\r\n"
    response += "\r\n"  # blank line to indicate the end of headers
    response += content
    return response.encode("utf-8")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, addr = server_socket.accept()  # wait for client
    data = client_socket.recv(4096)
    if data:
        method, path, version = parse_http_request(data)
        if path == "/" or path == "" or path is None:
            client_socket.sendall(create_http_response(200, "OK"))
        else:
            client_socket.sendall(create_http_response(404, "Not Found", path))
    else:
        client_socket.sendall(create_http_response(200, "OK"))


if __name__ == "__main__":
    main()

import argparse
import gzip
import io
import os
import socket
import sys
import threading

from .HttpRequest import HttpRequest

echo = "/echo/"
user_agent = "/user-agent"
files_path = "/files/"


def encode_to_gzip(data):
    try:
        with io.BytesIO() as buf:
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(data.encode('utf-8'))
            return buf.getvalue()
    except Exception:
        return None


def write_file_response(file_path, content):
    try:
        with open(file_path, 'wb') as file:
            file.write(content)
            response = create_http_response(201, "Created")
    except IOError:
        response = create_http_response(500, "Internal Server Error")
    return response


def read_file_response(http_path, file_path):
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r') as file:
                response = create_http_response(200, "OK", file.read(), "application/octet-stream")
        except FileNotFoundError:
            response = create_http_response(404, "Not Found", http_path)
    else:
        response = create_http_response(404, "Not Found", http_path)
    return response


def create_http_response(status_code=500, status_message="Internal Server Error", content="", content_type="text/html",
                         compression=False):
    # HTTP response
    response = f"HTTP/1.1 {status_code} {status_message}\r\n"
    response += f"Content-Type: {content_type}\r\n"  # "; charset=utf-8\r\n"

    if compression:
        result = encode_to_gzip(content)
        if result:
            content = result
            response += f"Content-Length: {len(content)}\r\n"
            response += f"Content-Encoding: gzip\r\n"
    else:
        response += f"Content-Length: {len(content)}\r\n"
        content = content.encode('utf-8')

    response += "\r\n"  # blank line to indicate the end of headers
    return response.encode('utf-8') + content


def handle_client(client_socket, directory_path):
    response = create_http_response(status_code=501, status_message="Not Implemented")
    data = client_socket.recv(8192)
    if data:
        request = HttpRequest(data)
        if request.method() == "GET":
            if request.path() == "/" or request.path() == "" or request.path() is None:
                response = create_http_response(200, "OK", compression=request.use_gzip())
            elif request.path().startswith(echo):
                response = create_http_response(200, "OK", request.path()[len(echo):].strip(), "text/plain",
                                                request.use_gzip())
            elif request.path().startswith(user_agent):
                # very much the happy path here.
                response = create_http_response(200, "OK", request.user_agent(), "text/plain", request.use_gzip())
            elif request.path().startswith(files_path):
                filename = request.path()[len(files_path):].strip()
                response = read_file_response(request.path(), os.path.join(directory_path, filename))
            else:
                response = create_http_response(404, "Not Found", request.path())
        elif request.method() == "POST" and request.path().startswith(files_path):
            filename = request.path()[len(files_path):].strip()
            response = write_file_response(os.path.join(directory_path, filename), request.body())
        else:
            print(f"Unhandled request: {request.method()} {request.path()}", file=sys.stderr)

    client_socket.sendall(response)
    client_socket.close()


def main():
    parser = argparse.ArgumentParser(description='Simple webserver')
    parser.add_argument('--directory', type=str,
                        help='path to the directory to serve files from')

    args = parser.parse_args()

    # Validate if the directory exists
    directory_path = args.directory
    if directory_path is not None:
        if not os.path.isdir(directory_path):
            print(f"Error: '{directory_path}' is not a valid directory.")
            return -1
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()  # wait for client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, directory_path))
        client_thread.start()


if __name__ == "__main__":
    main()

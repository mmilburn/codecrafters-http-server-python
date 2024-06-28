import argparse
import gzip
import io
import os
import socket
import threading

echo = "/echo/"
user_agent = "/user-agent"
files_path = "/files/"


def encode_to_gzip(data):
    try:
        with io.BytesIO() as buf:
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(data.encode('utf-8'))
            return buf.getvalue()
    except Exception as e:
        print(e)
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


def parse_http_request(request_data):
    request = {"headers": {}}
    lines = request_data.decode('utf-8').splitlines()
    method, path, version = lines[0].split()
    for line in lines[1:]:
        line = line.strip()
        if line != "":
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key:
                request["headers"][key] = value
                if "," in value:
                    request["headers"][key] = set([x.strip() for x in value.split(",")])
                if key == "content-length":
                    request["headers"][key] = int(value)
        else:
            break
    request['method'] = method
    request['path'] = path
    request['version'] = version
    if "content-length" in request["headers"] and request["headers"]["content-length"] > 0:
        length = request["headers"]["content-length"]
        request["body"] = request_data[-length:]
    return request


def create_http_response(status_code=500, status_message="Internal Server Error", content="", content_type="text/html",
                         compression=False):
    # HTTP response
    print(compression)
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
        request = parse_http_request(data)
        method = request['method']
        path = request['path']
        # print(request['headers'])
        compression = True if 'accept-encoding' in request['headers'] and "gzip" in request['headers'][
            'accept-encoding'] else False
        if method.upper() == "GET":
            if path == "/" or path == "" or path is None:
                response = create_http_response(200, "OK", compression=compression)
            elif path.startswith(echo):
                response = create_http_response(200, "OK", path[len(echo):].strip(), "text/plain", compression)
            elif path.startswith(user_agent):
                # very much the happy path here.
                response = create_http_response(200, "OK", request["headers"]["user-agent"], "text/plain", compression)
            elif path.startswith(files_path):
                filename = path[len(files_path):].strip()
                response = read_file_response(path, os.path.join(directory_path, filename))
            else:
                response = create_http_response(404, "Not Found", path)
        elif method.upper() == "POST" and path.startswith(files_path):
            filename = path[len(files_path):].strip()
            response = write_file_response(os.path.join(directory_path, filename), request["body"])

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

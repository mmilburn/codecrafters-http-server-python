import argparse
import os
import socket
import sys
import threading

from .Http import HttpRequest, Response


def handle_client(client_socket, directory_path):
    data = client_socket.recv(8192)
    if data:
        response = Response(directory_path, HttpRequest(data))
        client_socket.sendall(response.to_string())
    client_socket.close()


def main():
    parser = argparse.ArgumentParser(description='Simple webserver')
    parser.add_argument('--directory', type=str,
                        help='path to the directory to serve files from')

    args = parser.parse_args()

    # Validate if the directory exists
    directory_path = args.directory
    if directory_path is not None:
        directory_path.strip()
        if not os.path.isdir(directory_path):
            print(f"Error: '{directory_path}' is not a valid directory.", file=sys.stderr)
            return -1
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()  # wait for client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, directory_path))
        client_thread.start()


if __name__ == "__main__":
    main()

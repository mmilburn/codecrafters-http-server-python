import sys

from .IOHelpers import read_file, write_file, encode_to_gzip

USER_AGENT = "User-Agent"
CONTENT_TYPE = "Content-Type"
CONTENT_LENGTH = "Content-Length"
CONTENT_ENCODING = "Content-Encoding"
ACCEPT_ENCODING = "Accept-Encoding"
GZIP = "gzip"


class Headers:

    def __init__(self):
        self.headers = {}

    def add_header(self, line):
        k, v = line.split(':', 1)
        k = k.strip()
        v = v.strip()
        if k not in self.headers:
            if v.isdigit():
                self.headers[k] = int(v)
            elif "," in v:
                self.headers[k] = set([x.strip() for x in v.split(",")])
            else:
                self.headers[k] = v
        else:
            print(f"{k} already present in headers!", file=sys.stderr)

    def user_agent(self):
        return self.headers[USER_AGENT] if USER_AGENT in self.headers else ""

    def content_length(self):
        return self.headers[CONTENT_LENGTH] if CONTENT_LENGTH in self.headers else 0

    def gzip_accepted(self):
        if ACCEPT_ENCODING in self.headers and GZIP in self.headers[ACCEPT_ENCODING]:
            return True
        return False

    def set_content_length(self, length):
        self.headers[CONTENT_LENGTH] = str(length)
        return self

    def set_content_type(self, content_type):
        self.headers[CONTENT_TYPE] = content_type
        return self

    def set_content_encoding(self, encoding):
        self.headers[CONTENT_ENCODING] = encoding
        return self

    def set_content_encoding_gzip(self):
        self.set_content_encoding(GZIP)
        return self

    def content_encoding_is_gzip(self):
        return True if CONTENT_ENCODING in self.headers and self.headers[CONTENT_ENCODING] == GZIP else False

    def get_headers_as_list(self):
        return [": ".join([key, value]) for key, value in self.headers.items()]


class HttpRequest:
    def __init__(self, data):
        self._headers = Headers()
        lines = data.decode('utf-8').splitlines()
        self._method, self._path, self._version = lines[0].split()
        self._method = self._method.upper()
        for line in lines[1:]:
            line = line.strip()
            if line:
                self._headers.add_header(line)
            else:
                break
        if self._headers.content_length() > 0:
            self._body = data[-1 * self._headers.content_length():]

    def method(self):
        return self._method

    def path(self):
        return self._path

    def version(self):
        return self._version

    def body(self):
        return self._body

    def headers(self):
        return self._headers

    def use_gzip(self):
        return self._headers.gzip_accepted()

    def user_agent(self):
        return self._headers.user_agent()


class HttpResponse:

    def __init__(self, status, headers: Headers, body=None):
        self._status = status
        self._headers = headers
        self._body = None
        if body is not None:
            if not self._headers.content_encoding_is_gzip():
                self._body = body.encode('utf-8')
            else:
                self._body = body

    def to_bytes(self):
        response = f"HTTP/1.1 {self._status}\r\n"
        for entry in self._headers.get_headers_as_list():
            response += f"{entry}\r\n"
        response += "\r\n"
        response = response.encode('utf-8')
        return response + self._body if self._body is not None else response


class HttpResponseBuilder:
    _statuses = {
        200: "200 OK",
        201: "201 Created",
        404: "404 Not Found",
        500: "500 Internal Server Error",
        501: "501 Not Implemented",
    }

    def __init__(self):
        self._status_line = None
        self._headers = Headers()
        self._body = None

    def set_status(self, status_code):
        if status_code not in self._statuses:
            print(f"status code: {status_code} not implemented using status code 501", file=sys.stderr)
            self._status_line = self._statuses[501]
        else:
            self._status_line = self._statuses[status_code]
        return self

    def set_body(self, body):
        self._body = body
        return self

    def set_headers(self, headers: Headers):
        self._headers = headers
        return self

    def build(self):
        if self._body is not None:
            self._headers.set_content_length(len(self._body))
        else:
            self._headers.set_content_length(0)
        return HttpResponse(self._status_line, self._headers, self._body)


class Response:
    """Encapsulate the server 'configuration' here"""
    METHOD_GET = "GET"
    METHOD_POST = "POST"
    FILES_PATH = "/files/"
    GET_ROOT_PATHS = {"/", "", None}
    GET_ECHO_PATH = "/echo/"
    GET_USER_AGENT_PATH = "/user-agent"
    MIME_TEXT = "text/plain"
    MIME_APPLICATION = "application/octet-stream"

    def __init__(self, directory_path, request: HttpRequest):
        body = None
        response = HttpResponseBuilder()
        response_headers = Headers()

        if request.method() == self.METHOD_GET:
            # set defaults that will apply to most responses
            response.set_status(200)
            response_headers.set_content_type(self.MIME_TEXT)
            if request.path().startswith(self.GET_ECHO_PATH):
                body = request.path()[len(self.GET_ECHO_PATH):].strip()
            elif request.path().startswith(self.GET_USER_AGENT_PATH):
                body = request.user_agent()
            elif request.path().startswith(self.FILES_PATH):
                filename = request.path()[len(self.FILES_PATH):].strip()
                file_contents = read_file(directory_path, filename)
                if file_contents:
                    body = file_contents
                    response_headers.set_content_type(self.MIME_APPLICATION)
                else:
                    response.set_status(404)
            elif request.path() not in self.GET_ROOT_PATHS:
                response.set_status(404)
        elif request.method() == self.METHOD_POST and request.path().startswith(self.FILES_PATH):
            filename = request.path()[len(self.FILES_PATH):].strip()
            if write_file(directory_path, filename, request.body()):
                response.set_status(201)
            else:
                response.set_status(500)
        else:
            response.set_status(501)

        if body is not None:
            if request.headers().gzip_accepted():
                gzipped_body = encode_to_gzip(body)
                if gzipped_body is not None:
                    response_headers.set_content_encoding_gzip()
                    response.set_body(gzipped_body)
                else:
                    response.set_body(body)
            else:
                response.set_body(body)

        response.set_headers(response_headers)
        self._response = response

    def to_string(self):
        return self._response.build().to_bytes()

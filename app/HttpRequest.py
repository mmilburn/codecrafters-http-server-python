import sys


class Headers:
    def __init__(self):
        self.headers = {}

    def add_header(self, line):
        k, v = line.split(':', 1)
        k = k.strip().lower()
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
        return self.headers["user-agent"] if "user-agent" in self.headers else ""

    def content_length(self):
        return self.headers["content-length"] if "content-length" in self.headers else 0

    def gzip_accepted(self):
        if "accept-encoding" in self.headers and "gzip" in self.headers["accept-encoding"]:
            return True
        return False


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

import gzip
import io
import os
import sys
from typing import Optional


def encode_to_gzip(data) -> Optional[bytes]:
    try:
        with io.BytesIO() as buf:
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(data.encode('utf-8'))
            return buf.getvalue()
    # FIXME: Not seeing all possible exceptions in the documentation. Must be reading the docs wrong.
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def write_file(directory, file, content):
    success = False
    file_path = os.path.join(directory, file)
    try:
        with open(file_path, 'wb') as file:
            file.write(content)
            file.close()
            success = True
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}", file=sys.stderr)
    return success


def read_file(directory, filename) -> Optional[bytes]:
    content = None
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except Exception as e:
            print(f"Exception occurred: {type(e).__name__}: {e}", file=sys.stderr)
    else:
        print(f"File not found: {file_path}", file=sys.stderr)
    return content

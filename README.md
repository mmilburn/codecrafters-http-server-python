# About the Project

This is a finished Python implementation for the
["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview).
This code implements functionality for all stages (and extensions) of the
challenge as of 2025-02-13.

## What can it do?

1. Respond to a `GET` request made to `/echo/{string}` with a body of `{string}`
2. Respond to a `GET` request made to `/user-agent` with a body containing your
   user-agent.
3. Return a file when a `GET` request is made to `/files/{filename}` given the
   server is started with the command line option `--directory <dir>` and
   `{filename}` is present in the `<dir>`.
4. Write a file `{filename}` to `<dir>` when a `POST` request is made to
   `/files/{filename}` and `--directory <dir>` is provided on the command line.
5. Respond with a `gzip` encoded body when the client's `Accept-Encoding` header
   contains `gzip`.

# TODO

- [ ] Refactor code to be more pythonic
- [ ] Restructure the project into a codebase that is simple to maintain and
  extend (demonstrate how I approach _software engineering_ versus just slinging
  code).

# Test Run Video

A short video of the code being run in the codecrafters test environment:

https://github.com/user-attachments/assets/6bb0cb53-ee2a-4fdf-97e3-9d76e752a986
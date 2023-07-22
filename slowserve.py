"""Serves a file very slowly."""

import time
import re
import sys
import os

if __name__ == "__main__":
    # Exit early if run directly.
    print("This is a WSGI application. Run with `gunicorn server:app`.")
    sys.exit(1)


class HTTPResponse:
    """An object representing a HTTP response."""

    def __init__(
        self,
        status: int = 200,
        data: bytes = b"",
        extra_headers: list[tuple[str, str]] = None,
    ) -> None:
        status_codes = {
            200: "200 OK",
            400: "400 Bad Request",
            403: "403 Forbidden",
            404: "404 Not Found",
            405: "405 Method Not Allowed",
            413: "413 Content Too Large",
            418: "418 I'm a teapot",
            500: "500 Internal Server Error",
            507: "507 Insufficient Storage",
        }
        self.status = status_codes[status]
        self.data = [data]

        if not extra_headers:
            extra_headers = []
        if any(header[0].casefold() == "content-length" for header in extra_headers):
            self.headers = extra_headers
        else:
            self.headers = extra_headers.append(f"Content-Length: {len(data)}")

    def __str__(self) -> str:
        return (
            "┌─────── Response ───────┐\n"
            + f"HTTP/1.1 {self.status}\n"
            + "\n".join(f"{h[0]}: {h[1]}" for h in self.headers)
            + "\n\n"
            + str(self.data[0])
            + "\n└───── End Response ─────┘"
        )


def slowly_read_file(filename: str, rate: float = 100):
    """Returns a generator that yields bytes one at a time at up to the rate
    bytes per second."""
    with open(filename, "rb") as file:
        byte = b"1"
        while byte:
            time.sleep(1.0 / rate)
            byte = file.read(1)
            yield byte


def app(environ, start_response):
    """Entry point of WSGI app."""

    filename = "index.html"

    if environ["QUERY_STRING"]:
        rate = int(
            re.search("rate=[0-9]+", environ["QUERY_STRING"]).group().split("=")[-1]
        )
    else:
        rate = 100
    if environ["REQUEST_METHOD"] == "GET":
        headers = [
            ("Content-Length", str(os.stat(filename).st_size)),
            ("Content-Type", "text/html; charset=utf-8"),
        ]
        response = HTTPResponse(
            200, data=slowly_read_file(filename, rate), extra_headers=headers
        )
    else:
        response = HTTPResponse(405)

    print(response)

    # Send the HTTP response.
    start_response(response.status, response.headers)
    return response.data

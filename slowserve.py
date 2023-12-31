"""Serves a file very slowly."""

import time
import re
import sys
from pathlib import Path

WEB_ROOT = "html/"

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
        if isinstance(data, bytes):
            self.data = [data]
        else:
            self.data = data
        if extra_headers:
            if not any(
                header[0].casefold() == "content-length" for header in extra_headers
            ):
                self.headers = extra_headers.append(("Content-Length", str(len(data))))
            else:
                self.headers = extra_headers
        else:
            self.headers = []

    def __str__(self) -> str:
        return (
            f"HTTP/1.1 {self.status}\n"
            + "".join(f"{h[0]}: {h[1]}\n" for h in self.headers)
            + str(self.data)
        )


def slowly_read_file(filename: str, rate: float = 100):
    """Returns a generator that yields bytes one at a time at up to the rate
    bytes per second."""
    with open(filename, "rb") as file:
        byte = file.read(1)
        while byte:
            time.sleep(1.0 / rate)
            yield byte
            byte = file.read(1)


def get_filepath(file_uri_path: str, webroot: str | Path) -> Path:
    """Returns Path object to requested file if it is inside the webroot and it
    exists. Also return index.html if a directory is requested."""

    filepath = Path(webroot).joinpath(file_uri_path.lstrip("/")).resolve()
    if filepath.is_relative_to(Path(webroot).resolve()) and filepath.exists():
        if filepath.is_file():
            return filepath
        if filepath.is_dir():
            filepath = filepath.joinpath("index.html")
            if filepath.is_file():
                return filepath
    raise FileNotFoundError


def get_content_type(path: str) -> str:
    """Gets the content type based on the path. Defaults to text/html."""

    content_types = {"jpg": "image/jpg"}
    extension = path.split(".")[-1]
    return content_types.get(extension, "text/html; charset=utf-8")


def app(environ, start_response):
    """Entry point of WSGI app."""

    if environ["QUERY_STRING"]:
        rate = int(
            re.search("rate=[0-9]+", environ["QUERY_STRING"]).group().split("=")[-1]
        )
    else:
        rate = 100
    if environ["REQUEST_METHOD"] == "GET":
        try:
            filepath = get_filepath(environ["PATH_INFO"], WEB_ROOT)

            headers = [
                ("Content-Length", str(filepath.stat().st_size)),
                ("Content-Type", get_content_type(environ["PATH_INFO"])),
            ]
            response = HTTPResponse(
                200, data=slowly_read_file(filepath, rate), extra_headers=headers
            )
        except FileNotFoundError:
            response = HTTPResponse(404)
    else:
        response = HTTPResponse(405)

    # Send the HTTP response.
    start_response(response.status, response.headers)
    return response.data

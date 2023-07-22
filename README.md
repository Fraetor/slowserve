# Slowserve

A very slow HTTP server to see what the web is like at extremes.

## Requirements

Slowserve is a [Python WSGI Server](https://peps.python.org/pep-3333/). I
recommend using [gunicorn](https://gunicorn.org/) to run it, ideally behind a
reverse proxy such as [NGINX](https://nginx.org/) for more permanent
deployments.

## Usage

To run slowserve use the following command.

```sh
# We need lots of threads because each one serves very slowly.
gunicorn --threads 50 slowserve:app
```

Once running any GET requests to the server will be served the `index.html`
file. By default the serving rate is 100 bytes per second. To change the rate at
which the file is served you can add a query string for the serving rate in
bytes per second, e.g: `http://localhost:8000/?rate=300`.

## Licence

Slowcat is available under the following public domain equivalent licence.

### BSD Zero Clause License

Copyright © 2023 by James Frost

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

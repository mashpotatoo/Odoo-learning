# Intensive Day 20 - HTTP Controllers and Ecommerce Learning Setup

- **Practical work:** November 5, 2026
- **Follow-up verification and documentation:** November 7, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL
- **Addon:** `ecommerce_learning`
- **Database:** `odoo20dev`
- **Status:** Basic HTTP controller implemented and verified; full Day 20 tracker checklist/sign-off unverified

## What I learned

Started a separate ecommerce learning addon and created a public HTTP endpoint.
This lesson introduces how Odoo receives a web request, matches a route, calls a
Python controller method, and sends a response back to the caller.

The verified Day 20 endpoint is:

```text
GET /learning/http
```

Its response body is:

```text
Hello from the Day 20 HTTP controller!
```

The product JSON endpoints and draft quotation API were developed afterward in
**Intensive Day 21 - Product and Order JSON API**. They are separate from the
Day 20 practical documented here.

## Addon structure

The minimal structure used for the Day 20 controller was:

```text
ecommerce_learning/
|-- __init__.py
|-- __manifest__.py
`-- controllers/
    |-- __init__.py
    `-- main.py
```

The import chain matters: the addon imports `controllers`, and that package
imports `main`. Without those imports, Odoo will not load the controller class.
The current addon also contains later Day 21 work; this section shows the
Day 20 starting point.

### Addon initialization

`ecommerce_learning/__init__.py`:

```python
from . import controllers
```

`ecommerce_learning/controllers/__init__.py` at the Day 20 starting point:

```python
from . import main
```

### Day 20 manifest

The initial manifest used for this lesson was:

```python
{
    "name": "Ecommerce Learning",
    "version": "1.0.0",
    "summary": "Learn HTTP controllers through an ecommerce project",
    "author": "Mashrafi",
    "category": "Sales",
    "depends": ["base", "web", "sale_management"],
    "data": [],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
```

`sale_management` prepares the addon for the later product and quotation
exercises. The Day 20 method itself returns fixed text and does not read or
create Sales records. The manifest version and summary were subsequently
updated during Day 21.

## HTTP controller code

The Day 20 portion of `controllers/main.py` is:

```python
from odoo import http
from odoo.http import request


class EcommerceLearning(http.Controller):

    @http.route(
        "/learning/http",
        type="http",
        auth="public",
        methods=["GET"],
    )
    def http_example(self, **kwargs):
        return request.make_response(
            "Hello from the Day 20 HTTP controller!",
            headers=[("Content-Type", "text/plain; charset=utf-8")],
        )
```

### Understanding the code

| Part | Purpose |
|---|---|
| `http.Controller` | Base class for Odoo web controllers |
| `@http.route(...)` | Registers the URL and its request-handling settings |
| `"/learning/http"` | URL path handled by this method |
| `type="http"` | Uses normal HTTP request/response handling |
| `auth="public"` | Allows callers without a logged-in user session; anonymous execution uses Odoo's public user |
| `methods=["GET"]` | Restricts the route to GET; HEAD is also supported by routing |
| `request.make_response(...)` | Builds the HTTP response |
| `Content-Type` | Identifies the response as UTF-8 plain text |
| `**kwargs` | Accepts additional named request parameters; this example does not use them |

Both the decorator and the method must be indented inside the controller class.
The response-building code is indented inside the method.

## Request and response flow

```text
Browser or HTTP client
    -> GET /learning/http
    -> Odoo matches the controller route
    -> http_example() runs
    -> request.make_response() builds the response
    -> Caller receives status 200 and the plain-text message
```

The caller does not directly execute the Python function. It sends an HTTP
request, and Odoo decides which controller method handles that request.

## Running and testing

From the Odoo checkout, start the development server using its virtual
environment and the intended database:

```powershell
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d odoo20dev
```

Install the `ecommerce_learning` addon before expecting its routes to be
available. Restart Odoo after changing Python controller code, unless a working
automatic reload setup is already in use.

Open the intended database in the browser, then visit the endpoint on the same
host:

```text
http://127.0.0.1:8069/web/login?db=odoo20dev
http://127.0.0.1:8069/learning/http
```

The login page can establish the database selection without signing in. The
controller itself is public and does not require authentication.

For an HTTP client, choose **GET**, enter the endpoint URL, and send the request.
This Day 20 endpoint needs no JSON body. Opening the URL in a browser also sends
a GET request.

When several databases exist, a caller without a selected database can receive
a 404 even when the controller exists in an installed addon. Select the correct
database/session before assuming the Python route is missing. A database name
used for startup and a client's selected database/session are separate concerns.

## Verification evidence

Saved HTTP checks from November 5 recorded:

| Request | Result |
|---|---|
| `GET /learning/http` | **200**, expected greeting, `text/plain; charset=utf-8` |
| `HEAD /learning/http` | **200** |
| `POST /learning/http` | **405 Method Not Allowed** |
| `GET /web/login` | **200** |
| `GET /learning/shop` | **404**; no shop route was implemented in this practical |

The GET, HEAD, and POST checks for `/learning/http` were repeated successfully
against the running `odoo20dev` environment on **November 7, 2026**, after selecting
the database. The GET body still matched the greeting exactly.

The installation log also records successful module loading on November 5.
This README reports those specific checks, rather than treating them as evidence
of a completed shop, product catalog, or order workflow.

## Problems and debugging lessons

- **404 Not Found:** Check the URL, addon installation, Python imports, server
  restart, and database selection.
- **405 Method Not Allowed:** Check whether the caller used a method supported
  by the route. POST is intentionally rejected by this GET endpoint.
- **Controller not loaded:** Check both `__init__.py` files and ensure the method
  belongs to the controller class.
- **Old response after an edit:** Save the Python file and restart the server.
- **Unexpected response format:** This endpoint returns plain text. The JSON-RPC
  request bodies and authentication exercises belong to Day 21.

## Outcome and scope

The Day 20 HTTP-controller practical is implemented and verified. The complete
Day 20 Ultima checklist was not re-read successfully during this documentation
update, and no tracker completion or status change is claimed.

Day 21 extends the same addon with authenticated JSON-RPC requests, database
product searches, pagination, category filtering, product details, input
validation, and draft quotation creation with server-calculated totals. Its
implementation and test results should be documented separately.

[Previous: Intensive Day 19](../Day%2019/README.md) | [Back to learning index](../../README.md)

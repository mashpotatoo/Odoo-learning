# Intensive Day 21 - Product and Order JSON API

- **Original roadmap:** Days 52-53
- **Learning and verification:** November 5-7, 2026
- **Documentation:** November 7, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL
- **Addon:** `ecommerce_learning`
- **Status:** Core product and single-line draft quotation APIs implemented and verified; Ultima completion not updated or verified

## What I built

Extended [Day 20's HTTP controller](../Day%2020/README.md) with authenticated
JSON-RPC endpoints that read real products and create a draft quotation through
Odoo's Sales models. The lesson progressed from returning a fixed dictionary to
searching records, validating inputs, paginating/filtering results, and persisting
an actual quotation with server-calculated prices and totals.

| Endpoint | Purpose | Access |
|---|---|---|
| `/learning/http` | Existing Day 20 plain-text response | Public GET |
| `/learning/product-demo` | Paginated product list with optional category filter | Authenticated POST |
| `/learning/product-detail` | One product by variant ID | Authenticated POST |
| `/learning/quotation-demo` | Create one draft quotation with one product line | Authenticated POST plus ORM create permissions |

All three Day 21 routes use `type="jsonrpc"`, `auth="user"`, and
`methods=["POST"]`. Product IDs are `product.product` variant IDs, not
`product.template` IDs. Customer IDs are `res.partner` record IDs.

This README documents the guided implementation in `controllers/main.py`.
The separate preliminary controller in `controllers/api.py` is not the contract
or the verification scope of this lesson's `/learning/*-demo` and detail routes.
The optional multiple-product extension was discussed and practised as a Python
loop, but it is **not implemented in the quotation endpoint below**.

## Roadmap checklist and evidence

The live Day 21 task was read during the lesson. Its requirements were:

1. Add an authenticated endpoint to create a draft quotation with customer,
   product and quantity validation; calculate prices and totals on the server.
2. Test valid products, missing products, invalid quantities and draft order
   responses in Postman.
3. Create product list and product detail JSON endpoints with pagination and
   category filtering.

The implementation and checks below cover those requirements. User-supplied
screenshots show the Postman requests/responses and the saved Odoo quotation.
The supplied Ultima checklist screenshot still showed unchecked items at 0%;
this documentation publication does not change the checklist or claim that its
status was subsequently updated.

## Authentication in Postman

Use the Postman desktop app. A normal browser address-bar visit sends GET,
whereas these JSON-RPC endpoints require POST.

First send **POST** to:

```text
http://127.0.0.1:8069/web/session/authenticate
```

Select **Body > raw > JSON** and use:

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "odoo20dev",
        "login": "YOUR_ODOO_LOGIN",
        "password": "YOUR_ODOO_PASSWORD"
    },
    "id": 1
}
```

Replace the placeholders locally. They refer to Odoo credentials, not a Postman
account. Successful authentication returns a `result` containing the user's
`uid` and sets a session cookie. Keep the same host for later requests so
Postman can reuse the cookie; `localhost` and `127.0.0.1` have separate cookie
scopes.

An HTTP status of 200 alone does not prove application success. Read the body:
Odoo can return a JSON-RPC error with HTTP 200. Selecting **JSON**, rather than
**Text**, also sets the appropriate request content type.

During debugging, a request with no selected database returned 404. Explicitly
authenticating against `odoo20dev` selected the intended database and established
the user session.

## Product list, pagination and category filtering

Send **POST** to:

```text
http://127.0.0.1:8069/learning/product-demo
```

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "page": 1,
        "category_id": 3
    },
    "id": 1
}
```

`category_id` is optional. Omit it, or use JSON `null`, to skip category filtering.
Category 3 was the local **Services** category; IDs in another database may differ.
The filter matches the exact internal category, not all descendant categories.

The ORM search combines `sale_ok=True` with the optional category condition.
Normal active-record filtering and the caller's access rules still apply.
Each page contains at most **three** products, consistently ordered by `id`.

```python
offset = (page - 1) * 3
```

| Page | Offset | Matching rows requested |
|---|---:|---|
| 1 | 0 | First through third |
| 2 | 3 | Fourth through sixth |
| 3 | 6 | Seventh through ninth |

Offset counts matching records to skip, not product ID numbers. Deleted IDs and
filtered products can leave gaps. An out-of-range page or unmatched category
returns an empty list.

The response's `result` is a list of dictionaries containing `id`, `name`,
`price`, `category_id`, and `category_name`. The price is the variant's
`lst_price`, a catalog sales price. It is not a customer-specific quotation.
An unset category is represented by `false` in this implementation.

`page` and any supplied non-null `category_id` must be positive Python integers.
Numeric strings, zero, negative numbers, floats, and booleans are rejected.

## Product detail

Send **POST** to:

```text
http://127.0.0.1:8069/learning/product-detail
```

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "product_id": 3
    },
    "id": 1
}
```

The search requires both the requested ID and `sale_ok=True`. A matching,
accessible product returns one dictionary instead of a list. An unavailable or
missing product returns `{"error": "Product not found."}` inside `result`.
A provided ID with an invalid type/value returns the positive-integer validation
message.

The guided Postman tests verified an existing product, a missing product, and an
invalid ID. Product 3 was the local Fuchka test product, priced at 300.

## Draft quotation creation

Send **POST** to:

```text
http://127.0.0.1:8069/learning/quotation-demo
```

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "customer_id": 14,
        "product_id": 3,
        "quantity": 3
    },
    "id": 1
}
```

These are lesson-specific IDs. Customer 14 was a dedicated **Day 21 Test
Customer**, created through Odoo's customer form; the final number in its browser
URL identified the record. The customer form URL is not the API endpoint.

### Validation order

Before creating any records, the method:

1. Rejects unexpected fields captured by `**extra`.
2. Validates the customer ID and searches for an active, accessible customer.
3. Validates the product ID and searches for an accessible saleable product.
4. Validates the quantity as an integer or float greater than zero and at most
   1,000,000. Strings, booleans, zero, negative values and out-of-range numbers
   are rejected. The bounded comparison also rejects non-finite float values.

Defaults of `None` let missing quotation inputs reach these validation checks
instead of raising Python's missing-argument `TypeError`.

Unexpected inputs such as `price`, `price_unit`, `amount_total`, `state`, and
`company_id` are rejected. The method constructs its own create values rather
than forwarding arbitrary request data to the ORM.

### Creation and pricing

```python
order = request.env["sale.order"].create({
    "partner_id": customer.id,
    "state": "draft",
    "order_line": [
        Command.create({
            "product_id": product.id,
            "product_uom_qty": quantity,
        }),
    ],
})
```

`sale.order` is the quotation; `sale.order.line` stores each product row.
`Command.create()` creates and links a new line through the quotation's
`order_line` field. One quotation with two separate product rows would have one
order record and two line records. This endpoint currently creates one line.

No price or tax is accepted from the caller. Odoo's model computations apply
customer pricing, discounts, taxes and totals. The result returns the quotation
ID/name, state, customer/product names, quantity, unit price, untaxed amount,
tax amount, total and currency. The endpoint does not confirm the quotation or
create an invoice.

**Each successful request creates a new draft.** There is no idempotency key or
duplicate-request detection in this learning implementation.

## Complete guided controller

The following reproduces the saved `main.py` behavior with indentation/spacing
normalized and an obsolete comment corrected for readability. This publication
changes documentation only; it does not edit the running addon.

```python
from odoo import Command, http
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

    @http.route(
        "/learning/product-demo",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def product_demo(self, page=1, category_id=None):
        # Validate the requested page.
        if type(page) is not int or page < 1:
            return {
                "error": "page must be a positive integer."
            }

        # Only include products that can be sold.
        domain = [("sale_ok", "=", True)]

        # Apply an optional exact-category filter.
        if category_id is not None:
            if type(category_id) is not int or category_id < 1:
                return {
                    "error": "category_id must be a positive integer."
                }

            domain.append(("categ_id", "=", category_id))

        # Each page contains at most three products.
        offset = (page - 1) * 3

        Product = request.env["product.product"]

        products = Product.search(
            domain,
            limit=3,
            offset=offset,
            order="id",
        )

        # Convert product records into JSON-compatible data.
        product_list = []

        for product in products:
            product_list.append({
                "id": product.id,
                "name": product.name,
                "price": product.lst_price,
                "category_id": product.categ_id.id,
                "category_name": product.categ_id.name,
            })

        return product_list

    @http.route(
        "/learning/product-detail",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def product_detail(self, product_id):
        if type(product_id) is not int or product_id < 1:
            return {
                "error": "product_id must be a positive integer."
            }

        product = request.env["product.product"].search(
            [
                ("id", "=", product_id),
                ("sale_ok", "=", True),
            ],
            limit=1,
        )

        if not product:
            return {
                "error": "Product not found."
            }

        return {
            "id": product.id,
            "name": product.name,
            "price": product.lst_price,
            "category_id": product.categ_id.id,
            "category_name": product.categ_id.name,
        }

    @http.route(
        "/learning/quotation-demo",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def quotation_demo(
        self,
        customer_id=None,
        product_id=None,
        quantity=None,
        **extra,
    ):
        if extra:
            return {
                "error": "Unsupported fields: " + ", ".join(sorted(extra))
            }
        # Validate the customer ID.
        if type(customer_id) is not int or customer_id < 1:
            return {
                "error": "customer_id must be a positive integer."
            }

        # Find an active customer accessible to the current user.
        customer = request.env["res.partner"].search(
            [
                ("id", "=", customer_id),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not customer:
            return {
                "error": "Customer not found."
            }

        # Validate the product ID.
        if type(product_id) is not int or product_id < 1:
            return {
                "error": "product_id must be a positive integer."
            }

        # Find a saleable product accessible to the current user.
        product = request.env["product.product"].search(
            [
                ("id", "=", product_id),
                ("sale_ok", "=", True),
            ],
            limit=1,
        )

        if not product:
            return {
                "error": "Product not found."
            }
        if (
            type(quantity) not in (int, float)
            or not 0 < quantity <= 1_000_000
        ):
            return {
                "error": "quantity must be a number greater than 0 and at most 1000000."
            }

        # Create the draft quotation after all validation succeeds.
        order = request.env["sale.order"].create({
            "partner_id": customer.id,
            "state": "draft",
            "order_line": [
                Command.create({
                    "product_id": product.id,
                    "product_uom_qty": quantity,
                }),
            ],
        })

        line = order.order_line[0]

        return {
            "quotation_id": order.id,
            "quotation_name": order.name,
            "state": order.state,
            "customer_name": order.partner_id.name,
            "product_name": line.product_id.name,
            "quantity": line.product_uom_qty,
            "unit_price": line.price_unit,
            "amount_untaxed": order.amount_untaxed,
            "amount_tax": order.amount_tax,
            "amount_total": order.amount_total,
            "currency": order.currency_id.name,
        }
```

## Verified quotations and interface checks

The first successful Postman creation produced **S00001**:

| Field | Verified value |
|---|---|
| State | Draft / Quotation |
| Customer | Dedicated Day 21 test customer |
| Product | Fuchka |
| Quantity | 3 |
| Unit price | 300 |
| Untaxed amount | 900 |
| Tax | 0 |
| Total | 900 USD |

User screenshots showed both the JSON response and the saved quotation's line,
amounts and Quotation status in Odoo. Later checks verified **S00004** with
quantity 2.5 and total 750, and a non-admin Sales user's **S00005** with quantity
1 and total 300. S00005's creator and salesperson matched that Sales user.

An early test discovered that extra inputs were silently ignored by Odoo's route
argument filtering. Those otherwise valid requests created **S00002** and
**S00003**, both at the correct server price and still draft. Adding `**extra`
and rejecting unsupported fields fixed that request-contract issue. The final
live environment was checked at **five draft quotations**, including these test
records; the later validation/access runs did not create more.

## Automated checks and their limits

The following are separate runs with overlapping coverage. Their counts should
not be added together as a unique-test total.

| Verification | Outcome | What it established |
|---|---|---|
| Live HTTP validation retest | **70 passed, 0 failed** | Pagination, category filtering, product detail, invalid/missing inputs, unsupported fields, malformed JSON, anonymous rejection, saved drafts; quotation count stayed 4 |
| Live HTTP role/access run | **124 passed, 0 failed** | Administrator and Sales-user inputs; own-document access; direct read denial for another user's quotation; anonymous rejection; quotation count stayed 5 |
| Non-Sales internal users | All four denied quotation creation | No new quotations; product reads remained available under normal internal-user permissions |
| Isolated pricing/company run | **19 passed, 0 failed** | Nonzero taxes, fractional quantities, fixed/discount pricelists, company filtering and incompatible-company rejection |

### Important permission finding

The first non-Sales run reported six unexpected successful reads: three
University test users could read two quotations each. Inspection showed that
these users also had **Point of Sale / User** membership. Its existing
**POS Sales Orders** permission granted read access to `sale.order`.

All four non-Sales users were still blocked from creating quotations. A separate
non-Sales Lead Manager user without that POS permission was also blocked from
reading them. No permissions were changed. This corrected the initial assumption
that lacking Sales membership always implies lacking quotation read access.

For the **Sales / User: Own Documents Only** account, S00005 was readable, while
Administrator's S00001 was hidden from search and rejected by a direct ORM read
through the authenticated web API. This verifies record access beyond the
interface's My Quotations filter.

### Isolated tax, pricelist and company checks

These called the saved controller methods directly with the actual Odoo ORM and
a temporary Sales-user environment in a separate test database. They were not
Postman or live HTTP tests.

| Scenario | Untaxed | Tax | Total |
|---|---:|---:|---:|
| 2 x 100 with 10% tax | 200 | 20 | 220 |
| 2.5 x 100 with 10% tax | 250 | 25 | 275 |
| Customer fixed price 60, quantity 2, 10% tax | 120 | 12 | 132 |
| Customer 20% discount on 100, quantity 2, 10% tax | 160 | 16 | 176 |
| Second company: 2 x 80 with 5% tax | 160 | 8 | 168 |

Customer-pricelist tests explicitly enabled the pricelist feature in the test
environment. With only one company selected, another company's products and
customers were unavailable. With both companies allowed, incompatible
customer/product combinations were rejected by Odoo's company consistency checks;
request-equivalent savepoints verified rollback in those failure cases.

Final-run temporary fixtures and settings were rolled back. A prepared test
company and localization from the setup remained only in that separate test
database. The live database's settings and five draft quotations were unchanged.

## Debugging lessons

- **Text versus JSON:** Select raw JSON in the request Body, not the response
  viewer's format dropdown.
- **Malformed JSON:** A missing final `}` caused HTTP 400 before the controller
  ran. JSON syntax and business validation are separate checks.
- **Authentication versus authorization:** `auth="user"` requires a login. ORM
  permissions decide whether that user can read products or create quotations.
- **200 with an error:** Both custom validation dictionaries inside `result` and
  top-level Odoo JSON-RPC errors must be inspected; status alone is insufficient.
- **Indentation:** An order assignment nested after a validation `return` was
  unreachable, causing `UnboundLocalError` when the response used `order`.
  Creation must run after validation, at the method-body indentation level.
- **Unexpected fields:** Without `**extra`, Odoo's route wrapper could discard
  unknown named arguments before the method saw them. Explicit capture enables
  deliberate rejection.
- **Default arguments:** Quotation defaults of `None` make missing inputs produce
  the method's validation messages.
- **Record rules:** Test both search results and direct record reads. A hidden
  menu or search filter alone does not establish access security.
- **Pricing:** A catalog price and a customer's quotation price can differ.
  Use Odoo's computed amounts; do not trust a caller-supplied price.

## Current scope and next extension

The core Day 21 checklist has implementation and verification evidence. Ultima
checkbox/task completion remains a separate, unverified action.

Current limitations are explicit:

- One product line per quotation; the multi-product request format and command
  loop were learning exercises, not a deployed endpoint extension.
- Fixed page size of three; no page-count/total metadata or maximum page bound.
- The quotation route rejects unknown/missing fields clearly; the product routes
  do not yet have the same complete argument-contract handling.
- Framework access/company failures use Odoo's native JSON-RPC errors. Custom
  validation messages appear inside `result.error`; there is no unified error
  schema or dedicated HTTP status mapping.
- Discounts can affect computed totals; the response does not expose a separate
  discount field or detailed tax breakdown.
- No configurator/combo-product workflow, retry deduplication, load testing,
  currency-conversion coverage, or claim of production readiness.

The next optional extension is accepting `lines: [{product_id, quantity}, ...]`,
validating every line first, and calling `sale.order.create()` once with the
complete list of `Command.create()` entries.

[Previous: Intensive Day 20](../Day%2020/README.md) | [Back to learning index](../../README.md)

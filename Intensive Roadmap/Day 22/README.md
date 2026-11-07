# Intensive Day 22 - Ecommerce API Authentication and Roles

- **Original roadmap:** Day 54
- **Learning, verification and documentation:** November 7, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL
- **Addon:** `ecommerce_learning`, version `20.0.1.3.0`
- **Currency:** Bangladeshi taka, **BDT / ৳**
- **Status:** Authentication, role permissions and customer-order isolation implemented and tested; Ultima completion not updated or verified by this publication

## What I built

Extended [Day 21's product and quotation APIs](../Day%2021/README.md) with a
public, explicitly approved product catalogue and authenticated order-reading
endpoints. The API now distinguishes Manager, Sales Staff and Customer access,
derives customer ownership from the login session, and returns only selected
response fields.

The day's currency follow-up also made the company, product forms and retained
draft quotations use BDT. A separate user-requested maintenance operation removed
the old Bengali Rasoi POS shop while preserving the ecommerce products,
quotations and unrelated University ERP/Ultima data.

## Roadmap requirements and outcome

| Requirement | Implemented behavior | Verification |
|---|---|---|
| Suitable authentication; separate public catalogue from private orders | Public GET catalogue; session-authenticated JSON-RPC order routes | Anonymous public reads and signed-out private rejection tested |
| Manager, Sales Staff and Customer permissions; own orders and approved fields | Explicit API role gate, exact customer-partner ownership, company filtering and response allowlists | Existing live roles checked; two isolated Customer accounts tested |
| Signed-out, authorized and forbidden requests, including another customer's order | Login required before private handlers; unauthorized and missing order IDs share a generic response | Automated authentication, cross-customer, unrelated-user and input-tampering cases passed |

These requirements are covered by the saved implementation and checks. This
README does not claim that the Ultima checklist was marked complete.

## Authentication versus authorization

**Authentication** establishes who the caller is. Odoo's normal
`/web/session/authenticate` endpoint creates a login session, which Postman retains
using the `session_id` cookie.

**Authorization** decides what that user can access. `auth="user"` requires a
login, but ownership and role checks are still needed inside the private API.
The order controller combines its explicit role domain with the caller's normal
Odoo ORM permissions.

| Route setting | Meaning in this lesson |
|---|---|
| `auth="public"` | Visitors may call the route without a login; anonymous execution uses Odoo's public user |
| `auth="user"` | Odoo requires an authenticated session before executing the handler |
| `methods=["GET"]` | Read-only public catalogue request |
| `type="jsonrpc"`, `methods=["POST"]` | Named JSON-RPC parameters for private learning endpoints |

## Endpoint overview

| Method | Endpoint | Purpose and access |
|---|---|---|
| GET | `/learning/http` | Preserved Day 20 public greeting |
| GET | `/learning/catalogue?page=1` | Public list of approved products; three per page |
| GET | `/learning/catalogue/<product_id>` | Public detail for one approved variant |
| POST | `/learning/product-demo` | Existing authenticated product list, now including currency |
| POST | `/learning/product-detail` | Existing authenticated product detail, now including currency |
| POST | `/learning/quotation-demo` | Sales Staff/Manager single-line draft quotation creation |
| POST | `/learning/orders` | Paginated list of orders permitted by the caller's role |
| POST | `/learning/order-detail` | Detail of one permitted order |

The separate preliminary `/learning/api/*` controller is retained from earlier
work. Its product and quotation routes remain Sales-only and use a different
`success/data/error` response envelope. The examples below follow the guided
routes in `main.py` and the new Day 22 catalogue/order controllers.

Product IDs refer to `product.product` variants. Customer IDs refer to
`res.partner`; order IDs refer to `sale.order` and differ from references such
as `S00005`.

## Public catalogue with explicit approval

Public visitors can see only products approved for this learning catalogue.
A Sales Manager who already has product-edit permission can enable
**Approved for learning catalogue** under a product's **General Information →
Learning ecommerce** section.

The new `product.template` field uses:

```python
learning_catalogue_published = fields.Boolean(
    string="Approved for learning catalogue",
    default=False,
    copy=False,
    groups="sales_team.group_sale_manager",
)
```

The model field's group restriction protects approval through ORM/API writes,
as well as the field's visibility in the form. Normal product write permissions
still apply. Approval covers the template's variants. Existing products and
copies start unapproved.

The public query fixes the company to the public user's company and uses an
explicit domain:

```python
company = request.env.ref("base.public_user").sudo().company_id
Product = request.env["product.product"].sudo().with_company(company)

domain = [
    ("learning_catalogue_published", "=", True),
    ("active", "=", True),
    ("product_tmpl_id.active", "=", True),
    ("sale_ok", "=", True),
    ("company_id", "in", [False, company.id]),
]
```

Anonymous users do not have general product-model read permission. This
controller therefore uses a narrowly scoped elevated product read, with a fixed
domain and fixed output fields. Visitors cannot supply a domain, company or field
list. No public product-write operation is exposed.

The only public product fields are:

```json
{"id": 3, "name": "Example Product", "price": 300.0, "currency": "BDT"}
```

This is an illustrative response; IDs and prices depend on the database.

The list accepts only an ASCII numeric `page`, from 1 to 1,000,000. It returns
`products`, `page`, `page_size`, `total` and `pages`, ordered by variant ID.
Unknown query parameters return HTTP 400. An unavailable or hidden product ID
returns HTTP 404 with the same `Product not found.` message. Responses include
`Cache-Control: no-store`, and POST is rejected with HTTP 405.

At the final live checks, **zero products were approved**, so the public catalogue
correctly returned an empty list. Positive public-product cases were exercised
with approved fixtures in the isolated test database.

## Role and ownership policy

| Role | Order reads through the learning API | Quotation creation |
|---|---|---|
| Signed out | Rejected before the private controller runs | Rejected |
| Portal Customer | Orders whose `partner_id` exactly equals the session user's partner | Denied |
| Sales Staff | Own or unassigned orders within permitted company/ORM access | Allowed subject to normal Sales create rights |
| Sales Manager | Orders within permitted companies and normal ORM access | Allowed subject to normal Sales create rights |
| Other internal users | Rejected by the API role gate | Rejected |

The controller determines ownership from `request.env.user.partner_id`. A caller
cannot choose another customer ID to widen their order access. Extra inputs such
as `customer_id`, `domain`, `fields` or `sudo` are rejected on order reads.

The explicit role gate also blocks unrelated internal users who happen to have
`sale.order` read permission through another addon. Existing generic Odoo model
permissions were preserved. This ownership policy applies to the learning API;
standard Odoo portal pages retain their standard commercial-account access rules.

## Order-read controller

The following is the implemented `controllers/orders.py` behavior:

```python
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class LearningOrders(http.Controller):
    @staticmethod
    def _domain():
        user = request.env.user
        domain = [("company_id", "in", request.env.companies.ids)]
        if user.has_group("sales_team.group_sale_manager"):
            return domain
        if user.has_group("sales_team.group_sale_salesman"):
            return domain + ["|", ("user_id", "=", user.id), ("user_id", "=", False)]
        if user.has_group("base.group_portal") and not user.has_group("base.group_user"):
            return domain + [("partner_id", "=", user.partner_id.id)]
        raise AccessError("Order access is required.")

    @staticmethod
    def _summary(order):
        return {
            "id": order.id, "name": order.name, "state": order.state,
            "amount_total": order.amount_total, "currency": order.currency_id.name,
        }

    @staticmethod
    def _denied():
        return {"error": "You do not have permission to access orders."}

    @http.route("/learning/orders", type="jsonrpc", auth="user", methods=["POST"])
    def orders(self, page=1, **extra):
        try:
            domain = self._domain()
            if extra or type(page) is not int or not 1 <= page <= 1_000_000:
                return {"error": "Use only page, an integer between 1 and 1000000."}
            model = request.env["sale.order"]
            total = model.search_count(domain)
            orders = model.search(domain, limit=3, offset=(page - 1) * 3, order="id desc")
            return {"orders": [self._summary(order) for order in orders],
                    "page": page, "page_size": 3, "total": total}
        except AccessError:
            return self._denied()

    @http.route("/learning/order-detail", type="jsonrpc", auth="user", methods=["POST"])
    def order_detail(self, order_id=None, **extra):
        try:
            domain = self._domain()
            if extra or type(order_id) is not int or order_id < 1:
                return {"error": "Use only order_id, a positive integer."}
            order = request.env["sale.order"].search(domain + [("id", "=", order_id)], limit=1)
            if not order:
                return {"error": "Order not found."}
            result = self._summary(order)
            result.update({
                "amount_untaxed": order.amount_untaxed, "amount_tax": order.amount_tax,
                "lines": [{"product_name": line.name,
                           "quantity": line.product_uom_qty, "unit_price": line.price_unit,
                           "subtotal": line.price_subtotal}
                          for line in order.order_line if not line.display_type],
            })
            return result
        except AccessError:
            return self._denied()
```

Order reads use the caller's environment without `sudo()`. Missing and
inaccessible IDs share the same response, preventing the API from revealing
whether another customer's order exists.

The response allowlist excludes access tokens, internal notes and customer
addresses. Detail `product_name` is the stored sales-line description; older
records with an empty description can return an empty string.

## Postman practice

### 1. Authenticate

Send **POST** to `http://127.0.0.1:8069/web/session/authenticate` with
**Body → raw → JSON**:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "db": "odoo20dev",
    "login": "YOUR_ODOO_LOGIN",
    "password": "YOUR_ODOO_PASSWORD"
  },
  "id": 22
}
```

Enter credentials locally. Successful authentication returns `result.uid` and
sets the session cookie. Keep the same host for all requests: `localhost` and
`127.0.0.1` use separate cookie scopes.

### 2. List permitted orders

Send **POST** to `http://127.0.0.1:8069/learning/orders`:

```json
{"jsonrpc":"2.0","method":"call","params":{"page":1},"id":22}
```

The response contains `result.orders`, `page`, `page_size` and `total`.
The list returns at most three orders per page, newest ID first. `page` must be
an integer from 1 to 1,000,000; booleans and numeric strings are rejected.

The supplied Postman screenshot showed an authenticated response containing:

```json
{
  "id": 5,
  "name": "S00005",
  "state": "draft",
  "amount_total": 300.0,
  "currency": "BDT"
}
```

This confirms the user's order-list exercise and BDT response. Customer
ownership evidence comes from the separate role tests described below.

### 3. Read an order

Send **POST** to `http://127.0.0.1:8069/learning/order-detail`:

```json
{"jsonrpc":"2.0","method":"call","params":{"order_id":5},"id":22}
```

Replace `5` with an order visible to the signed-in account. A permitted order
returns its reference, state, currency, totals and line details.

### 4. Check missing, forbidden and signed-out requests

- A missing positive order ID returns `result: {"error":"Order not found."}`.
- A Customer trying another customer's order receives that same generic result.
- An unrelated internal user receives `You do not have permission to access orders.`.
- To test signed-out access, remove the `session_id` cookie or log out, then
  repeat the private request. Odoo returns a top-level JSON-RPC error with
  `error.code = 100`.

The Postman **No Auth** setting alone does not remove a login cookie. HTTP 200
can contain an application/authentication error, so inspect the JSON body.

The missing-order, signed-out and live-Customer detail exercises were provided
as manual practice. No additional user screenshot confirming those exact manual
steps is claimed here; automated coverage is recorded separately.

## BDT pricing and one-time shop reset

The initial BDT solution introduced **Learning ecommerce pricelist** on the
company. Public/private product responses and both learning quotation-creation
routes use that configured pricelist. New drafts receive its currency and
server-calculated prices.

The user chose to retain numeric demo prices as taka: for example, 300 means
300 BDT rather than converting USD 300 through an exchange rate. Fixed variant
rules preserve the configured ecommerce prices. Updating a product's base list
price does not automatically update an existing fixed-price rule.

The company's USD currency was initially blocked by two posted journal entries
belonging to the old **Bengali Rasoi** POS shop. The user explicitly requested
removal of that shop only, while keeping the ecommerce products and quotations.
The maintenance work included a verified database/filestore backup and a
rollback-only rehearsal before applying normal Odoo reset/delete methods.

| Development-data operation | Verified outcome |
|---|---|
| Remove Bengali Rasoi | One POS configuration, four closed sessions, five cancelled POS orders, five payments and two linked bank-difference entries removed |
| Set actual company currency | Normal Odoo company-currency change to BDT accepted after the shop entries were removed |
| Preserve ecommerce products | All seven product records and their numeric prices retained; product forms now use BDT |
| Preserve quotations | All five draft quotations retained with the same IDs, customer links, states, quantities, unit prices and numeric totals; currency/pricelist changed to BDT |
| Preserve other applications | University ERP and Ultima record counts unchanged |

The addon pricing configuration, the shop cleanup and the historical draft
currency update are separate operations. The cleanup was specific to this
development database. Other POS functionality remained installed.

## Verification evidence

The final checks were repeated before proceeding to Day 23. These runs have
overlapping coverage and should be read by scope rather than added as a count
of unique scenarios.

| Run | Result | Scope |
|---|---|---|
| Complete addon HTTP suite with BDT company currency | **31 passed, 0 failures, 0 errors** | Product/quotation regression tests plus catalogue, authentication, role, ownership, pricing, taxes and rollback tests in an isolated database |
| Live verification of the running development database | **101 passed, 0 failures** | Existing Manager, Sales Staff and unrelated internal roles; public/private requests; input rejection; pagination; BDT; retained data and shop removal |
| Fresh post-reset verification | **18 passed, 0 failures** | Company/product/quotation currencies, retained values, removed POS history, unrelated record counts and endpoint health |
| User-supplied Postman screenshot | **Order list confirmed** | `S00005`, draft, amount 300, currency BDT |

The live checks used short-lived server-issued sessions for existing users and
their unchanged permissions. They did not verify those users' passwords or
create live Customer accounts. The isolated `HttpCase` tests use the normal
credential/session flow and two disposable Customer accounts to prove own-order
access, cross-customer rejection and direct ORM rejection of another account's
order. Successful new quotation creation is exercised in isolated fixtures.

The live audit did not change products, quotations, users, passwords or roles.
Invalid live creation requests were rejected without adding quotations. Test
attachment storage was database-backed to avoid the previously observed Windows
filestore cleanup issue; this was an isolated-test setting.

## Source structure and running tests

The implementation is in the Odoo checkout; this learning repository contains
the lesson documentation.

```text
custom-addons/ecommerce_learning/
|-- controllers/
|   |-- main.py                 # Guided products and Sales-only draft creation
|   |-- api.py                  # Earlier alternate API
|   |-- catalogue.py            # Approved public product reads
|   `-- orders.py               # Role-aware private order reads
|-- models/
|   |-- product_template.py     # Manager-protected approval field
|   `-- res_company.py          # Learning pricelist and shared price helper
|-- views/
|   |-- product_template_views.xml
|   `-- res_company_views.xml
`-- tests/
    |-- test_api.py
    |-- test_catalogue.py
    `-- test_order_roles.py
```

Run the addon suite against a disposable, installed Odoo 20 test database:

```powershell
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d YOUR_TEST_DATABASE -u ecommerce_learning --test-enable --test-tags /ecommerce_learning --stop-after-init --http-interface=127.0.0.1 --http-port=8073 --max-cron-threads=0
```

The recorded full check used a separate database with BDT company currency and
database-backed attachments. The source API milestone was saved locally at
`1a85d77ec6ee8b4da760021260e788ccbd134a30`; that local code commit is separate
from publication of this documentation repository.

## Outcome and next lesson

Day 22's authentication, public/private separation, role gating, exact-customer
order reads and response-field restrictions are implemented and verified. The
current empty public catalogue reflects its approval settings. Ultima checklist
completion is not claimed by the README or GitHub publication.

Day 23 covers the Postman collection and fuller API documentation. Its collection
runner results and native Postman import status are separate from Day 22's
verification counts.

Reference: [Odoo 20 web controllers](https://www.odoo.com/documentation/20.0/developer/reference/backend/http.html).

[Previous: Intensive Day 21](../Day%2021/README.md) | [Back to learning index](../../README.md)

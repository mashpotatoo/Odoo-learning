# Intensive Day 26 - Owl with Live Products and Orders

- **Original roadmap:** Day 61
- **Learning period:** November 13-15, 2026
- **Practical completed and documented:** November 15, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL, modern browser
- **Inspected Owl build:** `3.0.0-alpha.49`
- **Addon:** `ecommerce_learning`
- **Practice currency:** Bangladeshi taka, **BDT**
- **Status:** Core practical completed. Live interface evidence, database checks, user confirmations and isolated browser checks are distinguished below. Ultima checklist completion was not updated or verified.

## What I built

Connected the [Day 25 Owl shop](../Day%2025/README.md) to existing Odoo
product and order APIs. The shop now loads live products, maintains a temporary
cart, loads accessible contacts into a customer dropdown, creates draft
quotations and displays recent quotations/orders.

The interface shows loading, empty and error states for product and order
requests. Quotation submission displays Odoo's reference, state, currency and
calculated total. The cart clears after confirmed success.

Manager, Sales Staff and portal Customer exercises checked different access
rules. The portal customer used the normal portal and authenticated API calls;
the backend Owl Shop was not made into a customer-facing portal application.

The working addon remains in the separate Odoo checkout. This repository
publishes the lesson documentation, not a copy or release of the addon.

## Roadmap requirements and outcome

| Requirement | Outcome |
|---|---|
| Retrieve live product and order records through secured APIs | Product cards use the product API; the recent-orders table uses the order-list API |
| Handle loading, empty and error states; submit cart contents | Product/order request states, retry behavior, customer selection and draft quotation submission implemented |
| Test Manager, Sales Staff and Customer access | Manager and staff workflows exercised; staff visibility and assignment checked; customer ownership and creation rejection checked |

Core practical completion is separate from tracker completion. No Ultima status
change is claimed.

## Open the exercise

Start the local Odoo server using its configuration and sign in:

~~~text
http://localhost:8069/web/login?db=odoo20dev
~~~

Internal users with the required Sales permissions open:

**Ecommerce Learning -> Owl Shop**

For JavaScript changes during learning:

~~~text
http://localhost:8069/odoo?debug=assets
~~~

Select Owl Shop after opening the backend. Keep asset-debug mode enabled when
editing the integrated JavaScript. A hard refresh does not always rebuild an
already generated production asset bundle.

Portal customers sign in to the same database and reach `/my`. Their custom API
checks were made from that signed-in browser session.

The standalone Day 25 HTML practice page has a separate implementation. It was
not converted into the live Day 26 shop.

## Implementation locations

Paths are relative to the separate `ecommerce_learning` addon unless noted.

| File | Responsibility |
|---|---|
| `static/src/day25/shop.js` | Integrated Owl components, inline templates, signals, requests and client-action registration |
| `views/ecommerce_shop_views.xml` | Owl Shop client action and internal-user application menus |
| `__manifest__.py` | Registers the JavaScript in `web.assets_backend` |
| `controllers/api.py` | Existing secured product API and multi-line draft quotation creation |
| `controllers/orders.py` | Existing order list/detail APIs and role/ownership domains |
| `controllers/catalogue.py` | Separate approved public catalogue; not the source used by this backend shop |
| `models/res_company.py` | Learning ecommerce pricelist configuration and product pricing helper |
| `odoo.conf` in the Odoo checkout | Local default database configuration |

The integrated JavaScript retains its Day 25 path because Day 26 extends that
same registered client action. There is no separate Day 26 addon entry point.

## Data flow and API contracts

~~~text
Owl Shop
  -> product API -> product cards -> cart
  -> ORM contact lookup -> selected customer
  -> order creation API -> Odoo draft quotation -> success message
  -> order list API -> recent-orders table
~~~

| Operation | Call | Result consumed by the interface |
|---|---|---|
| Load products | `rpc("/learning/api/products", { page: 1, page_size: 20 })` | `result.data.products` after checking `result.success` |
| Load contacts | `orm.searchRead("res.partner", domain, ["display_name"], options)` | Array of contact IDs and display names |
| Create quotation | `rpc("/learning/api/orders", { customer_id, lines })` | `result.data` after checking `result.success` |
| Load orders | `rpc("/learning/orders", { page: 1 })` | `result.orders` after checking `result.error` |
| Read one order | `/learning/order-detail` with `order_id` | Order detail or an error; used in the portal access exercise |

The response shapes differ. The older order-read endpoint does not wrap its
records in `success` and `data`. The client must follow each endpoint's actual
contract.

Odoo's `rpc()` helper handles the JSON-RPC envelope and returns its `result`.
A plain browser `fetch()` receives the entire envelope, so console exercises
read `response.result`.

## Owl state and services

The existing product-card and cart-summary components continue to receive props
and callbacks from `Shop`. The parent owns the shared state.

~~~javascript
import { Component, xml, signal, useProps, t } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
~~~

| State | Initial value | Purpose |
|---|---|---|
| `products`, `cart`, `customers`, `orders` | `signal([])` | Current records and temporary cart lines |
| `customerId` | `signal(0)` | Selected contact; zero means no selection |
| `loading`, `hasLoaded`, `error` | False, false, empty string | Product request state |
| `submitting`, `orderError`, `createdOrder` | False, empty string, null | Quotation creation state |
| `ordersLoading`, `ordersLoaded`, `ordersError` | False, false, empty string | Order-list request state |

Each signal is declared once. A template reads a signal with parentheses, such
as `this.products()`. An update uses `this.products.set(records)`.

The two similarly named error signals serve different operations:

- `orderError`: creating a quotation.
- `ordersError`: retrieving the order list.

## Live products

The hardcoded demo array was first replaced with the Ultima product names and
prices, then replaced by an initially empty signal. A successful request maps
the API's `list_price` field to the `price` field expected by the cards.

~~~javascript
async loadProducts() {
    if (this.loading()) {
        return;
    }

    this.loading.set(true);
    this.error.set("");

    try {
        const result = await rpc("/learning/api/products", {
            page: 1,
            page_size: 20,
        });

        if (!result.success) {
            this.error.set(
                result.error?.message || "Odoo could not load products."
            );
            return;
        }

        const products = result.data.products.map(product => ({
            id: product.id,
            name: product.name,
            price: product.list_price,
            currency: product.currency,
        }));

        this.cart.set([]);
        this.products.set(products);
        this.hasLoaded.set(true);
    } catch (error) {
        this.error.set(
            "Could not load products. Check your connection and try again."
        );
        console.error("Product request failed:", error);
    } finally {
        this.loading.set(false);
    }
}
~~~

Successful product reloads clear the cart. This was introduced while moving
from demo IDs to real product IDs and remains the behavior of the exercise.

The loading guard prevents overlapping product requests. The button is disabled
during loading and changes its text to **Loading products...**.

The empty state appears only after a successful response with no records:

~~~xml
<p t-if="this.hasLoaded() &amp;&amp; !this.loading() &amp;&amp; !this.error() &amp;&amp; this.products().length === 0">
    No products found.
</p>
~~~

Use `&amp;&amp;` in XML attributes. The browser evaluates the resulting logical
AND expression.

### Catalogue data used during the lesson

The following BDT prices were copied from the
[Ultima shop](https://www.ultima.care/shop) during the lesson. This is a dated
practice snapshot, not a promise of current storefront pricing.

| Product | Practice price, BDT |
|---|---:|
| Ultima Elite RO Hot & Cold Water Purifier | 44,900 |
| Ultima Light Commercial RO Gen 2.0 | 57,900 |
| Ultima TriShield RO (H7) Water Purifier | 32,900 |
| Ultima Fontessa RO (X2) Water Purifier | 35,900 |
| Ultima Zenith RO (X5) Water Purifier | 28,900 |
| Ultima Crystal RO Gen 2 (F6) Water Purifier | 22,900 |
| Ultima Hot & Cold Water Dispenser | 24,900 |

The Elite product already existed; six missing products and their learning
pricelist rules were added. Stored catalogue prices and the pricing helper's
BDT results were checked.

Sweet Rosmalai and Down Payment (POS) were archived at the user's request.
They were not permanently deleted. The live saleable-product list then had
nine records: the seven Ultima products plus Service Fee and Default Product
(POS). The shop does not filter the response down to the seven storefront
products.

## Customer lookup and selection

Contacts are read through the ORM service using the signed-in user's access.

~~~javascript
setup() {
    this.orm = useService("orm");
}
~~~

`setup()` must be a class method outside the inline XML template.

The lookup uses:

~~~javascript
const customers = await this.orm.searchRead(
    "res.partner",
    [
        ["active", "=", true],
        ["type", "=", "contact"],
    ],
    ["display_name"],
    { limit: 20, order: "name, id" }
);

this.customerId.set(0);
this.customers.set(customers);
~~~

These are up to 20 accessible active contacts that can be selected as a
quotation customer. The query is not a filtered list of contacts with previous
sales.

The UI displays `display_name` but sorts by the stored `name` field and then
`id`. Sorting on `display_name` failed in this checkout because that computed
field is not stored.

The dropdown is outside the Load customers button. Its event handler converts
the selected string value into a numeric ID:

~~~javascript
selectCustomer(event) {
    this.customerId.set(Number(event.target.value));
    console.log("Selected customer ID:", this.customerId());
}
~~~

The selection resets when contacts are reloaded, not before every selection.

Customer-load failures currently appear in the console. A dedicated visible
loading/error/empty treatment for the contact dropdown was not added.

## Cart payload and server pricing

The existing cart still supports adding products, merging matching lines,
increasing/decreasing quantities and removing a line.

For submission, only product IDs and quantities are mapped from the cart:

~~~javascript
prepareOrderLines() {
    const lines = this.cart().map(line => ({
        product_id: line.id,
        quantity: line.quantity,
    }));

    console.table(lines);
    return lines;
}
~~~

An example request payload has this shape:

~~~javascript
{
    customer_id: selectedCustomerId,
    lines: [
        { product_id: firstProductId, quantity: 2 },
        { product_id: secondProductId, quantity: 1 },
    ],
}
~~~

The variables above are illustrative. Record IDs must come from the current
database.

The browser sends no unit prices, taxes, totals or state. The existing backend
validates the customer, products and quantities, constructs order lines and
creates a `sale.order` in `draft`. It uses the configured learning ecommerce
pricelist when present and lets Odoo calculate line prices and totals.

The controller rejects unsupported input fields. Its create operation runs
inside a savepoint and uses the caller's normal ORM permissions. Elevation in
the separate pricing helper is limited to reading pricelist configuration; it
does not elevate order creation.

The cart total is a preview based on displayed product prices and quantities.
It does not calculate the quotation's taxes.

## Creating the draft quotation

The finished submission method is:

~~~javascript
async createQuotation() {
    if (this.submitting() || this.loading()) {
        return;
    }

    this.orderError.set("");

    const customerId = this.customerId();
    const lines = this.prepareOrderLines();

    if (!Number.isInteger(customerId) || customerId <= 0) {
        this.orderError.set("Select a customer first.");
        return;
    }

    if (lines.length === 0) {
        this.orderError.set("Add a product to your cart first.");
        return;
    }

    this.submitting.set(true);
    this.createdOrder.set(null);

    try {
        const result = await rpc("/learning/api/orders", {
            customer_id: customerId,
            lines: lines,
        });

        if (!result.success) {
            this.orderError.set(
                result.error?.message || "Odoo could not create the quotation."
            );
            return;
        }

        this.createdOrder.set(result.data);
        this.cart.set([]);
    } catch (error) {
        this.orderError.set(
            "Could not confirm quotation creation. Check Sales quotations before retrying."
        );
        console.error("Quotation request failed:", error);
    } finally {
        this.submitting.set(false);
    }
}
~~~

The submission button is disabled while submitting, during product loading,
when the cart is empty or when no customer is selected. The method also guards
submission and validates its inputs.

A fieldset wraps the Shop controls and is disabled during submission, keeping
the selected customer and cart controls from changing while the request is in
flight.

The success message displays `createdOrder().name`, `state`, `currency` and
`amount_total`. These values come from Odoo's response.

On a confirmed failure, the cart remains available. A lost response makes the
creation result uncertain: a quotation might already have been saved. The
message asks the user to check Sales quotations before retrying. No automatic
creation retry or server-side idempotency mechanism was implemented.

### Price and tax example verified in Odoo

For one Hot & Cold Water Dispenser:

| Value | BDT |
|---|---:|
| Cart preview / quotation untaxed subtotal | 24,900 |
| Odoo-calculated tax | 3,735 |
| Quotation total | 28,635 |

The difference demonstrates why the UI displays the server's final total
instead of treating its own cart calculation as authoritative. These values
describe the test customer's configuration and the lesson's records.

Older quotations retain their previously saved prices. For example, S00005's
BDT 300 total was historical test data; updating the catalogue did not reprice
that quotation.

## Live order list and request states

The order endpoint returns up to three records per page, sorted by descending
record ID. The current UI requests page 1.

~~~javascript
async loadOrders() {
    if (this.ordersLoading()) {
        return;
    }

    this.ordersLoading.set(true);
    this.ordersError.set("");
    this.orders.set([]);

    try {
        const result = await rpc("/learning/orders", {
            page: 1,
        });

        if (result.error) {
            this.ordersError.set(result.error);
            return;
        }

        this.orders.set(result.orders);
        this.ordersLoaded.set(true);
    } catch (error) {
        this.ordersError.set(
            "Could not load orders. Please try again."
        );
        console.error("Order request failed:", error);
    } finally {
        this.ordersLoading.set(false);
    }
}
~~~

Clearing previous rows at the beginning prevents old results from appearing
beside a failed new request. A successful empty response sets `ordersLoaded`
and displays **No orders found.** Errors are displayed separately.

The table is shown when `this.orders().length > 0`. Its loop uses each
`order.id` as the key and displays:

- `order.name`: quotation/order reference.
- `order.state`: current Odoo state.
- `order.currency`: currency code.
- `order.amount_total`: server-calculated total.

The list does not refresh automatically after quotation creation. The user
clicks **Load orders** to fetch it again.

## Scrollable backend layout

Odoo's action workspace has a fixed height and hides overflow. A long product
list therefore needs its own scroll container.

The Shop root and submission fieldset are:

~~~xml
<section class="o_action h-100 overflow-auto p-3" tabindex="0">
    <fieldset class="flex-shrink-0" t-att-disabled="this.submitting()">
        <!-- Product, customer, cart, submission and order-list controls -->
    </fieldset>
</section>
~~~

The height and overflow classes make the client action scrollable. Preventing
the fieldset from shrinking keeps the bottom controls reachable.

Template parsing and an isolated real-Owl browser check verified the structure,
scrolling and access to the quotation button and order table. The user also
confirmed the scrolling fix in the live backend.

## Role and ownership rules

A display name containing "Manager" does not establish Sales Manager access.
The lesson checked the actual Odoo groups of the accounts used.

| Role | Product/creation API | Order-read domain |
|---|---|---|
| Sales Manager | Sales-group check and normal ORM permissions apply | Orders in allowed companies, subject to normal ORM access |
| Sales Staff | May load private products and create draft quotations within normal permissions | Allowed-company orders assigned to that salesperson or with no salesperson |
| Portal Customer | Private Sales product/creation endpoints require a Sales role | Allowed-company orders with an exact `partner_id` match to the signed-in customer |

Managers take the manager branch before the staff branch. Backend menus require
an internal user. The portal customer's standard home remains `/my`.

Order reads derive identity from the session. They do not accept a caller's
customer ID or search domain. Order list and detail queries do not use `sudo()`.

A portal login was linked to the existing practice customer contact without
adding an internal-user or Sales role. Invitation email was suppressed during
local setup. Login credentials and password-setting scripts are not published
in this learning repository.

## Live role exercises and results

The references and IDs below describe synthetic records in the lesson database.
They are evidence, not IDs to assume on another installation.

| Exercise | Recorded result |
|---|---|
| Manager creates a quotation | S00010 saved as draft for one dispenser, total BDT 28,635; verified in the database |
| Manager order list | Interface showed recent drafts including S00011, S00010 and S00005 |
| Staff visibility | Before staff creation, the expected own order was S00005; Administrator's S00010/S00011 were excluded |
| Staff creates a quotation | Screenshot showed S00012, draft, BDT 28,635 and an empty cart |
| Staff assignment and isolation | Database check confirmed S00012 assigned to the staff user; staff-visible references were S00012 and S00005 |
| Customer reads own orders | Portal-session console screenshot returned S00012, S00011 and S00010 |
| Separate customer fixture | S00013 was created for My Company; database check verified a different customer contact |
| Customer list excludes another customer | Portal response still showed its own latest three records, excluding the newer S00013 |
| Customer requests another customer's order directly | Requesting S00013's record ID returned `{ error: "Order not found." }` in the screenshot |
| Customer tries staff quotation creation | User confirmed the rejection exercise; subsequent database check found zero quotations created by the portal account and S00013 still the latest record |

The customer's order visibility follows customer ownership, not salesperson
assignment. That is why the customer can read its own S00010/S00011 even though
those orders are hidden from the staff salesperson.

### Portal API exercise

From the signed-in customer portal session, the read-only list request was:

~~~javascript
fetch("/learning/orders", {
    method: "POST",
    credentials: "same-origin",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: { page: 1 },
        id: 1,
    }),
})
    .then(response => response.json())
    .then(response => {
        console.log(response);
        if (response.result?.orders) {
            console.table(response.result.orders);
        }
    });
~~~

The direct-detail check used `/learning/order-detail` and
`params: { order_id: 9 }`, where 9 was the verified record ID of S00013 in this
database. It returned no order details.

The staff-creation endpoint's configured denial shape is:

~~~javascript
{
    success: false,
    error: {
        code: "access_denied",
        message: "You do not have access to this operation."
    }
}
~~~

This is an application result inside the JSON-RPC envelope. An HTTP 200 by
itself does not prove the requested operation succeeded.

## Request-state testing

### Normal and empty results

The product and order request exercises temporarily used `page: 999` to obtain
an empty result without deleting records, then restored `page: 1`.

The saved final code uses page 1 for both requests. The product empty exercise
was user-confirmed and its code reviewed. Final order empty-state behavior was
also checked with controlled responses in the isolated browser.

### Failed request and recovery

Making the whole browser Offline prevented the intended click test: this Odoo
build's offline plugin disables buttons that are not marked as available
offline. Repeated failed `version_info` checks were Odoo's connectivity checks,
not evidence that the shop's product request had run.

The corrected manual exercise kept **No throttling** and blocked only the
specific API request in Chrome's Network/Request conditions tools. A screenshot
showed the visible product error, and recovery was user-confirmed after removing
the block.

The final isolated order-list checks covered:

- Loading text and a disabled button while a response is pending.
- Prevention of a repeated click.
- Successful row rendering.
- Successful empty response and its empty message.
- Visible access rejection, kept separate from an empty success.
- Visible connection failure and an available retry button.
- Clearing the error and restoring rows after a successful retry.

Restore normal request conditions and remove blocking rules after testing.

## Debugging lessons

| Symptom | Cause and correction |
|---|---|
| Edited products or headings did not appear | Odoo was serving an older generated JavaScript bundle; refreshed generated assets and verified the served code |
| Template called `products()` but the signal was missing | Fixed the accidental `pproducts` spelling |
| Error-state code could not parse | Replaced a malformed combined signal declaration with separate signal fields |
| Customer lookup had no ORM service | `setup()` had been pasted inside the template; moved it into the component class |
| Customer request returned an Odoo server error | Sorting on non-stored `display_name` failed; changed sorting to `name, id` |
| Customer selection behaved incorrectly | Dropdown was nested inside the load button; moved it outside and reset selection only on contact reload |
| Bottom controls could not be reached | Added the scrollable action root and non-shrinking fieldset |
| Orders appeared in the console but not on the page | Added the missing signal-driven order table inside the Shop template |
| Incognito database selector returned an internal server error | Server was scanning another local database with incompatible Windows collation settings; set the learning server's default database to `odoo20dev` and restarted |

The database-selector fix added:

~~~ini
[options]
db_name = odoo20dev
~~~

Selector, manager and direct-login endpoints subsequently returned HTTP 200.
This selected the intended learning database for this server; it did not repair,
delete or migrate the incompatible database.

## Verification evidence and limits

### Live evidence

- Screenshots showed live product responses, rendered product cards, blocked
  product-request errors, saved quotations, the staff order table and portal
  API responses.
- Read-only database checks verified catalogue/pricelist prices, archived
  products, quotation totals, staff assignment and customer ownership.
- The portal-created quotation count remained zero after the reported creation
  rejection exercise.
- The rebuilt asset bundle was fetched from the running server and checked for
  the current shop code.
- User confirmations supplemented screenshots for retry and other guided
  interactions. They are not represented as independent automated browser
  observations.

### Isolated checks

- JavaScript syntax checks passed.
- All three inline component templates parsed as XML.
- A controlled component check verified ORM initialization, contact lookup,
  numeric selection and selection reset behavior.
- Headless Chrome ran the real local Owl renderer with controlled API responses
  in a reproduction of Odoo's fixed-height action layout.
- That browser check passed scrolling, reachable bottom controls, submission
  locking, payload mapping, success rendering, cart clearing, order rendering
  and the order-list states listed above.
- These isolated checks made no real quotation during rendering tests. They
  did not sign into the live Odoo backend or replace the live role exercises.

No new full-addon regression test count, fresh-install result, production
deployment, multi-company role matrix or exhaustive permission audit is claimed.
The temporary verification harnesses were not packaged into this documentation
repository.

## Current limitations and follow-up work

- Product loading requests the first 20 records; orders show the latest three.
  There are no pagination controls.
- Contact selection reads up to 20 active contacts, with no search control.
  Contact-load errors remain console-only.
- The cart exists only in component memory. Refreshing the page or successfully
  reloading products clears it.
- Cards/cart still label prices as BDT directly. The product mapping retains the
  returned currency, but a general multi-currency display was not implemented.
- Cart totals exclude taxes and other quotation calculations. The returned Odoo
  total remains authoritative.
- No payment, order confirmation, delivery, invoice or stock operation is
  triggered by this exercise. Created records remain draft quotations.
- Submission has an in-flight guard and disabled controls, but no server
  idempotency key; an uncertain network result needs checking before retry.
- The order table needs a manual reload after creation. There is no order-detail
  view or polling in the Owl UI.
- The public catalogue remains separate. The new product records were not
  automatically approved for public catalogue publication by this exercise.
- Customer checks used the portal and API console, not an Owl portal checkout.
- Ultima completion remains unverified; this README records practical learning
  completion and its supporting evidence.

## References

- [Day 25: Owl product cards and cart component](../Day%2025/README.md)
- [Day 21: Product and order JSON API](../Day%2021/README.md)
- [Day 22: Ecommerce API authentication and roles](../Day%2022/README.md)
- [Owl 3 components](https://odoo.github.io/owl/documentation/v3/owl/reference/component.html)
- [Owl 3 reactivity](https://odoo.github.io/owl/documentation/v3/owl/reference/reactivity.html)
- [Chrome request conditions and request blocking](https://developer.chrome.com/docs/devtools/request-conditions)
- Local owning sources: `addons/web/static/lib/owl/owl.js`,
  `addons/web/static/src/core/orm_plugin.js`,
  `addons/web/static/src/core/offline/offline_plugin.js`,
  `addons/web/static/src/webclient/webclient_layout.scss` and the
  `ecommerce_learning` files listed above.

[Back to the learning repository](../../README.md)

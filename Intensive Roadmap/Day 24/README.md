# Intensive Day 24 - JavaScript with Products and Cart Calculations

- **Original roadmap:** Days 57-58
- **Completed and documented:** November 8, 2026
- **Environment:** Odoo 20 on Windows, modern browser, Node.js for isolated tests
- **Addon:** `ecommerce_learning`
- **Practice currency:** Bangladeshi taka, **BDT**
- **Status:** Implemented and verified; Ultima checklist **3/3**, task **Done**, task timer stopped

## What I built

Built a JavaScript product browser and temporary cart using the ecommerce APIs
from earlier lessons. The exercise covers functions, objects, arrays, events,
modules, promises, asynchronous requests, search, category filtering, quantity
changes, subtotal and discount calculations, and browser debugging.

The page can fetch practice JSON, Odoo's approved public catalogue, or private
Sales product data using an existing Odoo session. It shows loading, empty and
error states, supports retry, cancels superseded requests, and keeps final
quotation pricing on the server.

This README documents the completed lesson. Its working implementation is in
the separate Odoo checkout under
`custom-addons/ecommerce_learning/static/day24/`; this documentation publication
does not copy the addon source into the learning repository.

## Roadmap requirements and outcome

| Requirement | Completed work |
|---|---|
| Practice functions, arrays, objects and events using products and quantities | Product objects, combined search/category filtering, product selection, cart additions, quantity changes and removal |
| Use modules, promises and async/await to fetch products and handle loading/errors | ES modules, fetched practice JSON, public GET and private JSON-RPC sources, validation, pagination, loading/empty/error states, retry, cancellation and timeout |
| Build and debug subtotal/discount display while retaining server authority | Multi-line cart, subtotal and preview percentage discount, currency formatting, input validation, browser checks and exclusion of browser prices/discounts from future order-line payloads |

Live Ultima verification on November 8 confirmed all three items checked, task
status saved as **Done**, and the running Day 24 timer stopped. Later Owl and
live-order-submission lessons are separate work.

## Run the exercise

Start the existing Odoo development server, then open:

```text
http://127.0.0.1:8069/ecommerce_learning/static/day24/step1.html
```

The optional separate static preview on port 8074 serves practice JSON, but
does not implement Odoo API routes. Use the Odoo-served page for live sources.
Refresh if the browser displays a cached earlier checkpoint. Serve the page
over HTTP rather than opening the HTML file directly, so browser modules and
fetch follow normal HTTP loading rules.

The exercise defaults to **Practice JSON - BDT**. Private Sales products require
an existing signed-in Sales session on the same host. There are no passwords
or API keys in the exercise. Cookies for `localhost` and `127.0.0.1` are separate.

## File structure

```text
ecommerce_learning/static/day24/
|-- step1.html             # Finished page
|-- style.css              # Layout and styling
|-- app.js                 # State, events, loading and rendering
|-- products.js            # Fetch, response validation and filtering
|-- cart.js                # Cart operations and money calculations
|-- products.json          # Four BDT practice products
|-- LEARNING.md            # Detailed local explanation/debugging guide
|-- checkpoint1.html       # Preserved earlier basics page
|-- checkpoint1.js         # Preserved earlier basics script
|-- basics.js              # Previous source retained; final page uses app.js
|-- package.json           # ES module configuration; no external dependencies
`-- tests/day24.test.js    # Isolated product/cart tests
```

The source-path references above describe the separate Odoo checkout, not files
bundled alongside this README.

## Objects, arrays and functions

One product is an object; an array holds multiple products:

```json
{
  "products": [
    { "id": 1, "name": "Keyboard", "price": 2000, "currency": "BDT", "category": "Computing" },
    { "id": 2, "name": "Mouse", "price": 800, "currency": "BDT", "category": "Accessories" },
    { "id": 3, "name": "Monitor", "price": 12000, "currency": "BDT", "category": "Computing" },
    { "id": 4, "name": "Notebook", "price": 120, "currency": "BDT", "category": "Stationery" }
  ]
}
```

`product.price` reads an object's price. Functions receive inputs through
parameters and return results. Array positions start at zero, but the finished
page selects by product ID so filtering cannot change the meaning of a
selection. These practice IDs/prices are independent of live Odoo records.

The main array methods used are:

| Method | Use |
|---|---|
| `filter()` | Return matching products or remove a cart line |
| `find()` | Locate a product or existing cart line by ID |
| `map()` | Produce updated cart lines or collect category names |
| `some()` | Check whether a matching line exists |
| `reduce()` | Add quantities or monetary amounts into one result |

Spread syntax copies properties or entries into a new object/array. For example,
`{ ...product, quantity }` creates a cart line without changing the product object.

## Combined search and category filtering

The filtering function from `products.js` is:

```javascript
export function filterProducts(products, searchText = "", category = "") {
    const search = searchText.trim().toLowerCase();
    return products.filter(function (product) {
        const nameMatches = product.name.toLowerCase().includes(search);
        const categoryMatches = category === "" || product.category === category;
        return nameMatches && categoryMatches;
    });
}
```

`trim()` ignores surrounding search spaces; `toLowerCase()` ignores case;
`includes()` checks whether the name contains the search text. `||` means OR,
and `&&` requires both search and category conditions to pass.

An empty search matches every name. An empty category means all categories.
Searching `mouse` while choosing Computing returns no matches. Filters update
the product cards and picker without removing existing cart lines. Categories
are derived from loaded data using `map()` and `Set`.

## Modules, promises and async/await

The page starts an ES module:

```html
<script type="module" src="app.js"></script>
```

`app.js` imports the data functions:

```javascript
import { fetchProducts, filterProducts } from "./products.js";
```

`export` shares a function with other modules; `import` brings it into the
current file. Modules load their imports before executing the entry module and
are automatically deferred until HTML parsing has completed.

`fetch()` returns a **Promise**, which represents a result that arrives later.
An **async** function returns a Promise, and **await** waits inside that function
without freezing the page. One await receives the HTTP response; another reads
and parses its JSON body. The loader checks `response.ok` because fetch does
not automatically reject HTTP 404/500 responses.

## Product sources and API contracts

| Source | Request | Response used |
|---|---|---|
| Practice JSON | GET `products.json` | `products` array |
| Public catalogue | GET `/learning/catalogue?page=1` and following pages | Approved products plus pagination |
| Private Sales products | POST `/learning/api/products` | JSON-RPC `result.data.products` and pagination |

The private request body is:

```json
{"jsonrpc":"2.0","method":"call","id":1,"params":{"page":1,"page_size":100}}
```

The private endpoint is the existing Sales-only `/learning/api/products`
contract; it is different from the earlier `/learning/product-demo` response.
The loader checks top-level JSON-RPC errors and `result.success`, even when HTTP
status is 200. It normalizes `list_price` to the common `price` property and
uses `category_name` when supplied.

The public API deliberately excludes internal categories, so its products show
**Category not supplied**. An empty approved catalogue is a valid result. The
page does not publish products or substitute practice data after an API failure.

Pagination loads every returned page within limits of 100 pages and 10,000
products. Response checks reject invalid IDs, missing names, invalid prices,
malformed pagination, duplicate IDs and mixed-currency catalogues.

## Loading, errors, cancellation and retry

`loadProducts()` sets a loading state and clears the previous products/cart.
Controls cannot add unavailable products. `try` contains the request, `catch`
shows an actionable error and Retry button, and `finally` clears loading state.

An `AbortController` cancels the previous request when a new load begins. A
10-second timeout aborts requests that take too long. A load-version check also
prevents an older response from overwriting a newer source selection.

Switching or reloading the source clears the cart and preview discount, avoiding
mixed practice/live IDs or stale prices. Requests retain only same-origin
session cookies; credentials are not embedded in JavaScript.

## Events, state and rendering

The DOM is the browser's representation of HTML. `querySelector()` locates an
element; `.value` reads input text; `Number()` converts it before calculation.

```javascript
$("#discount").addEventListener("input", renderTotals);
```

The function is passed without parentheses so it runs when the event occurs.
`input` handles search/quantity/discount edits, `change` handles dropdowns, and
`click` handles adding, removing, retrying, reloading and clearing.

The main state variables are `products`, `cart` and `loading`. Render functions
display that state: product cards/picker, selected-product subtotal, cart rows
and totals. Product names are inserted with `textContent`, not interpreted as
HTML. Fixed-control event handlers are registered once; generated product/cart
controls receive handlers when their elements are created.

```text
HTML loads app.js
  -> imported modules load
  -> product request starts
  -> response is validated and stored
  -> product cards and picker render
  -> user event updates cart state
  -> totals recalculate
  -> displayed HTML updates
```

## Cart quantities and money calculations

Adding the same product merges quantities into one line. Quantities must be
whole numbers from 1 to 100 in this browser exercise. Invalid edits show a
message and preserve the last valid cart quantity; Remove deletes a line.
The server API independently enforces its own quantity rules.

Example:

| Calculation | BDT |
|---|---:|
| Keyboard: 2000 x 2 | 4,000.00 |
| Mouse: 800 x 1 | 800.00 |
| Subtotal | 4,800.00 |
| Preview discount: 10% | 480.00 |
| Estimated total | **4,320.00** |

Totals use whole minor currency units: BDT 4,800.00 becomes 480,000 poisha.
`Intl.NumberFormat` supplies currency decimal places and display formatting.
The preview rounds product prices to their currency's minor unit and rounds
the cart discount once, avoiding common floating-point display errors.

Discount must be numeric and between 0 and 100. Invalid discounts replace totals
with dashes until corrected. Empty-cart totals are zero; a 100% discount produces
zero. The cart is temporary and resets on refresh or product-source reload.

## Why Odoo totals remain authoritative

Browser values can be edited. The displayed total is therefore an estimate,
excluding taxes; the preview discount is not applied to Odoo quotations.

The existing `/learning/api/orders` endpoint accepts customer ID plus product
IDs and quantities. It rejects unsupported fields and creates quotation lines
through Odoo's ORM, which calculates prices, discounts, taxes and totals. The
Day 24 implementation leaves that controller unchanged and does not submit
orders.

The helper `buildOrderLines()` demonstrates the future permitted line shape:

```json
[{"product_id":1,"quantity":2}]
```

Browser prices, discounts, taxes and totals are excluded. Practice IDs must not
be submitted as live Odoo IDs. Live cart-to-quotation submission belongs to a
later lesson.

## Testing and browser debugging

Run from the separate Odoo checkout:

```text
node --test custom-addons/ecommerce_learning/static/day24/tests/day24.test.js
```

**25 isolated tests passed, with 0 failures**, on November 8, 2026. They cover
combined filters, immutable cart operations, duplicate-product merging,
quantity limits, mixed currencies, empty carts, subtotal/discount rounding,
zero/full/fractional discounts, unsafe amounts, permitted order-line payloads,
async loading, pagination, response validation, HTTP/network/JSON/session/role
errors and cancellation during requests or response-body reading.

Actual browser checks verified module/practice-JSON loading; combined filters;
the BDT 4,800/480/4,320 example; cart quantity changes; invalid quantity/discount
feedback; removal and empty carts; failed requests, retry and recovery; live
empty-public-catalogue handling; and live signed-out private rejection. Console
errors from deliberately failed requests were reviewed.

Additional checks confirmed unique HTML IDs, valid JavaScript element selectors,
local file references, and HTTP 200 responses for nine lesson/module/document
assets served by Odoo. JavaScript syntax and Git whitespace checks passed.

For manual debugging, inspect Network responses for `products.json`, public
catalogue GETs and private JSON-RPC POSTs. In Sources, set a breakpoint in
`addProduct()` or `calculateTotals()` and inspect product, quantity and cart
values. In Console, inspect the reported load errors. An HTTP 200 response alone
does not establish JSON-RPC success.

### Verification limits

- Authenticated private success and multi-page public loading were tested with
  controlled API responses, not a signed-in live Sales session or newly
  published products.
- The live approved public catalogue contained zero products during verification.
- No live quotations, public approval flags or authentication settings were changed.
- Browser behaviour, isolated tests and Ultima completion are separate evidence;
  each is recorded above without substituting one for another.

## Learning outcome

I can explain how product objects move from an asynchronous request into array
filters, how events update cart state, how render functions update HTML, and
how subtotal/discount calculations provide a browser preview while Odoo retains
authority over saved quotation totals.

[Back to the learning index](../../README.md)

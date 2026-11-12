# Intensive Day 25 - Owl Product Cards and Cart Component

- **Original roadmap:** Days 59-60
- **Learning completed and documented:** November 12, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL, modern browser
- **Local Owl build:** `3.0.0-alpha.49`
- **Addon:** `ecommerce_learning`
- **Practice currency:** Bangladeshi taka, **BDT**
- **Status:** Functional exercise completed; standalone browser checks and user-confirmed Odoo interface checks recorded. Ultima checklist/status was not updated or verified during this lesson.

## What I built

Built reusable Owl product cards and a cart summary, first in a standalone
practice page and then inside Odoo through a registered client action.

The shop displays three demo products. Users can add products, increase or
decrease quantities from the cart, and remove an entire product line. Product
cards, item count, line totals and cart total read from the same cart state.
An empty cart shows a message and a zero total.

This extends [Day 24's JavaScript and cart lessons](../Day%2024/README.md).
The working addon lives in the separate Odoo checkout under
`custom-addons/ecommerce_learning/`. This learning repository contains the
documentation; this publication does not copy the addon source into it.

## Roadmap requirements and outcome

| Requirement | Completed work |
|---|---|
| Learn components, props, state and templates | Reused one product-card class, passed typed props, used signals and callback functions, and rendered expressions and conditional content |
| Build and register product-list and cart components using demo data | `Shop` loops over products, hosts `QuantityCounter` and `CartSummary`, owns the cart and handles add/remove/quantity changes; the shop is registered as an Odoo client action |
| Display components in Odoo and verify totals, empty cart and asset loading | Backend asset entry, XML action and menus; standalone browser checks; user screenshot of the Odoo screen and confirmation of the final interaction checklist |

Functional lesson completion is separate from Ultima tracker completion. No
tracker update is claimed here.

## Open the exercise

With the addon upgraded and Odoo running, sign in and open:

**Ecommerce Learning -> Owl Shop**

For asset debugging, open:

```text
http://localhost:8069/odoo?debug=assets
```

The earlier standalone exercise is also available:

```text
http://127.0.0.1:8069/ecommerce_learning/static/day25/step1.html
```

The HTML page has its own copy of the practice components. The Odoo client
action uses `static/src/day25/shop.js`; edit that file when changing the
integrated shop. Each page/component instance has a separate temporary cart.
Refreshing or recreating the shop resets that cart.

## File structure

Paths below are relative to the separate `ecommerce_learning` addon:

```text
ecommerce_learning/
|-- __manifest__.py
|-- static/
|   |-- day25/
|   |   `-- step1.html                 # Standalone Owl practice page
|   `-- src/
|       `-- day25/
|           `-- shop.js               # Components and Odoo action registration
`-- views/
    `-- ecommerce_shop_views.xml      # Client action and application menus
```

The final JavaScript keeps its templates inline with the `xml` helper.
Templates were not moved into a separate asset XML file during this exercise.
No dedicated Day 25 stylesheet was added.

## What Owl is

Owl, the Odoo Web Library, is a JavaScript framework for interactive user
interfaces. A component combines display markup with behavior. The same
component class can create several instances, each displaying different data.

In Day 24, event handlers changed data and explicitly called rendering
functions. Here, templates read reactive values and Owl updates the display
when those values change.

| Concept | Meaning | Example in this lesson |
|---|---|---|
| Component | A reusable part of the interface | A product card or cart summary |
| Template | Markup describing what to display | Product name, price, quantity and buttons |
| Props | Inputs received from the parent/caller | Product, current quantity and callbacks |
| State | Data that changes during interaction | The cart array owned by `Shop` |
| Callback | A function passed to report an interaction | `onAdd`, `onRemove`, `onQuantityChange` |

### Match the installed Owl version

The inspected local Odoo checkout bundles **Owl 3.0.0-alpha.49**. This lesson
uses its `signal()`, `useProps()` and `t` type helpers. Examples based on older
Owl APIs such as `useState()` should be adapted to the installed build.
The version stated here describes this checkout, not every Odoo installation.

The standalone HTML loads `/web/static/lib/owl/owl.js` and reads the global
`owl` object. The integrated JavaScript imports through Odoo:

```javascript
import { Component, xml, signal, useProps, t } from "@odoo/owl";
import { registry } from "@web/core/registry";
```

## Component responsibilities and state ownership

```text
Shop: owns products and reactive cart state
|-- QuantityCounter: product card, repeated for each product
`-- CartSummary: cart lines, controls, empty message and total
```

The product card retains the learning-stage class name `QuantityCounter`.
It displays a product and its current quantity; it does not own a separate
quantity signal in the finished implementation.

Initially, each card had its own `quantity = signal(0)`. This demonstrated
independent component state. Before adding removal, quantities were lifted into
the parent's cart. This ensures that removing or changing a cart line also
updates its product card.

The final product-card props are:

```javascript
props = useProps({
    product: t.object(),
    quantity: t.number(),
    onAdd: t.function(),
});

addOne() {
    this.props.onAdd(this.props.product);
}
```

The child reports an action through its callback. `Shop` changes the cart and
passes the updated quantity back down through props.

## Signals and derived values

`Shop` holds the cart in a signal:

```javascript
cart = signal([]);
```

- `this.cart()` reads the current array.
- `this.cart.set(newLines)` writes a replacement array.
- Templates and methods that read the signal participate in reactive updates.

Quantity, item count and cart total are calculated from those same lines:

```javascript
quantityFor(productId) {
    const line = this.cart().find(line => line.id === productId);
    return line ? line.quantity : 0;
}

itemCount() {
    return this.cart().reduce(
        (count, line) => count + line.quantity,
        0
    );
}

cartTotal() {
    return this.cart().reduce(
        (total, line) => total + line.price * line.quantity,
        0
    );
}
```

Item count means total units, not the number of distinct product lines. Two
Keyboards and one Mouse therefore mean **3 items across 2 lines**.

## Product props and template loops

The demo catalogue is defined locally:

```javascript
products = [
    { id: 1, name: "Keyboard", price: 2000 },
    { id: 2, name: "Mouse", price: 800 },
    { id: 3, name: "Monitor", price: 15000 },
];
```

These IDs and prices are practice values, not assertions about live Odoo
product records. The Monitor price in this exercise is BDT 15,000.

`Shop` declares its child classes:

```javascript
static components = { QuantityCounter, CartSummary };
```

Its template creates a card for each product:

```xml
<t t-foreach="this.products" t-as="product" t-key="product.id">
    <QuantityCounter
        product="product"
        quantity="this.quantityFor(product.id)"
        onAdd="(product) => this.addToCart(product)"
    />
</t>
```

`t-foreach` selects the collection, `t-as` names the current item, and `t-key`
provides a stable unique identity. In `product="product"`, the left side names
the child's prop and the right side refers to the current loop item.

The product card displays values through `t-out`:

```xml
<h2 t-out="this.props.product.name"/>
<p>Price: BDT <t t-out="this.props.product.price"/></p>
<p>Quantity: <t t-out="this.props.quantity"/></p>
<button t-on-click="this.addOne">Add one</button>
<p>Total: BDT <t t-out="this.props.product.price * this.props.quantity"/></p>
```

## Adding, removing and changing quantities

Adding an existing product increases its line quantity. A new product creates
one line with quantity one:

```javascript
addToCart(product) {
    const lines = this.cart();
    const existing = lines.find(line => line.id === product.id);

    if (existing) {
        this.cart.set(
            lines.map(line =>
                line.id === product.id
                    ? { ...line, quantity: line.quantity + 1 }
                    : line
            )
        );
    } else {
        this.cart.set([
            ...lines,
            { ...product, quantity: 1 },
        ]);
    }
}

removeFromCart(productId) {
    this.cart.set(
        this.cart().filter(line => line.id !== productId)
    );
}

updateQuantity(productId, quantity) {
    if (!Number.isInteger(quantity) || quantity < 1) {
        return;
    }

    this.cart.set(
        this.cart().map(line =>
            line.id === productId
                ? { ...line, quantity }
                : line
        )
    );
}
```

`find()` locates an existing line. `map()` creates updated lines. Spread syntax
copies object fields before replacing quantity. `filter()` removes a selected
line. The quantity guard ignores non-integers and values below one.

## CartSummary and callbacks

`Shop` supplies the cart data and event handlers:

```xml
<CartSummary
    lines="this.cart()"
    total="this.cartTotal()"
    onRemove="(productId) => this.removeFromCart(productId)"
    onQuantityChange="(productId, quantity) => this.updateQuantity(productId, quantity)"
/>
```

The summary declares these inputs:

```javascript
props = useProps({
    lines: t.array(t.object()),
    total: t.number(),
    onRemove: t.function(),
    onQuantityChange: t.function(),
});
```

Conditional template content handles the empty cart:

```xml
<p t-if="this.props.lines.length === 0">Your cart is empty.</p>

<ul t-if="this.props.lines.length > 0">
    <t t-foreach="this.props.lines" t-as="line" t-key="line.id">
        <li>
            <t t-out="line.name"/>
            × <t t-out="line.quantity"/>
            — BDT <t t-out="line.price * line.quantity"/>

            <button type="button"
                    t-on-click="() => this.props.onRemove(line.id)">
                Remove
            </button>

            <button type="button"
                    t-on-click="() => this.props.onQuantityChange(line.id, line.quantity - 1)"
                    t-att-disabled="line.quantity === 1">
                Remove one
            </button>

            <button type="button"
                    t-on-click="() => this.props.onQuantityChange(line.id, line.quantity + 1)">
                Add one
            </button>
        </li>
    </t>
</ul>

<p>Cart total: BDT <t t-out="this.props.total"/></p>
```

All three buttons belong inside the line loop so their callbacks can access
that line's ID. At quantity one, **Remove one** is disabled. **Remove** stays
enabled because it deletes the entire line, including its final unit.

## Registering the Odoo client action

The integrated JavaScript ends with:

```javascript
registry.category("actions").add("ecommerce_learning.shop", Shop);
```

The parent class's `static components` declaration makes its children available
to its template. The action registry separately tells Odoo how to open the
whole shop. The child classes do not need separate client-action entries.

The standalone HTML uses `mount(Shop, document.querySelector("#app"))`.
The integrated `shop.js` omits that call: Odoo's action system mounts the shop.

The relevant manifest entries are:

```python
"data": [
    "views/product_template_views.xml",
    "views/res_company_views.xml",
    "views/ecommerce_shop_views.xml",
],
"assets": {
    "web.assets_backend": [
        "ecommerce_learning/static/src/day25/shop.js",
    ],
},
```

The existing addon depends on `web`. JavaScript under `static/src` is processed
as an Odoo module, enabling its `@odoo/owl` and `@web/core/registry` imports.
The asset entry must match the saved file's actual location.

`views/ecommerce_shop_views.xml` connects the action and menus:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="action_ecommerce_learning_shop" model="ir.actions.client">
        <field name="name">Owl Shop</field>
        <field name="tag">ecommerce_learning.shop</field>
    </record>

    <menuitem id="menu_ecommerce_learning_root"
              name="Ecommerce Learning"
              sequence="90"
              groups="base.group_user"/>

    <menuitem id="menu_ecommerce_learning_shop"
              name="Owl Shop"
              parent="menu_ecommerce_learning_root"
              action="action_ecommerce_learning_shop"
              sequence="10"/>
</odoo>
```

The XML action's tag must exactly match the JavaScript registry key.
The application menu is limited to internal users through `base.group_user`.
This menu restriction is not a replacement for server permissions when live
records and order submission are added later.

## Upgrade and asset-loading debugging

After changing manifest/XML configuration, stop the existing development
server before starting an upgrade. From the Odoo checkout, the lesson used:

```powershell
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d odoo20dev -u ecommerce_learning --http-interface=127.0.0.1 --http-port=8069 --max-cron-threads=0
```

Once the upgrade is complete, later normal starts can omit
`-u ecommerce_learning`. Use the existing local configuration; credentials do
not belong in this documentation. Refresh the browser with **Ctrl+Shift+R**
after restarting, then reopen the shop. Keep the same hostname as the signed-in
session; `localhost` and `127.0.0.1` use separate cookies.

### Registry error encountered

The menu initially failed with:

```text
Cannot find key "ecommerce_learning.shop" in the "actions" registry
```

Inspection confirmed that the file path, manifest entry and registry key
matched. Two Odoo launches were present, and the older process still owned
port 8069. The JavaScript bundle served by that process did not contain the
shop module or its registration.

The duplicate launches were stopped and one Odoo instance was restarted with
the current configuration. The user then supplied a screenshot showing the
shop inside Odoo and confirmed that the final interaction checklist worked.
The lesson demonstrates that loading XML menus successfully does not prove
that the browser has loaded the matching JavaScript module.

### Other mistakes corrected during the lesson

| Symptom | Cause and correction |
|---|---|
| Parent shop did not appear | The standalone page still mounted the child; changed it to mount `Shop` |
| Remove could not identify a product | Button was outside the line loop; moved it inside `<li>` |
| Final item could not be removed | Disabled condition was on Remove; moved it to Remove one |
| Integrated module retained standalone startup code | Removed the manual `mount()` call before action registration |
| Asset path did not match the saved file | Moved `shop.js` from `static/day25` into `static/src/day25` |
| XML file was not found under the manifest path | Corrected `ecomerce_shop_views.xml` to `ecommerce_shop_views.xml` |

## Verification and evidence limits

Browser interactions during the standalone exercise checked product props,
independent initial card state, product loops, shared counts, line merging,
cart totals, removal and quantity decreases/increases. Source review confirmed
the final disabled-button placement and integrated module configuration.

The user supplied a screenshot of **Ecommerce Learning -> Owl Shop** inside
Odoo, then reported that all five final backend checks below were working:

| Step | Expected result |
|---|---|
| Add two Keyboards and one Mouse | 3 items, Keyboard quantity 2, Mouse quantity 1, total BDT 4,800 |
| Use the cart's Mouse Add one button | 4 items, Mouse quantity 2, total BDT 5,600 |
| Use the cart's Mouse Remove one button | 3 items, Mouse quantity 1, total BDT 4,800 |
| Remove the Keyboard line | 1 item, total BDT 800, Keyboard card quantity 0 |
| At Mouse quantity 1, check Remove one and remove Mouse | Decrease disabled; Remove enabled; 0 items, BDT 0 and the empty-cart message |

The earlier Monitor loop check also showed quantity 2 and total BDT 30,000,
while the other product quantities stayed zero.

The final integrated backend interactions were user-confirmed. Automated
browser control could not independently verify that final backend screen
because browser control stopped when it could not establish the active Windows
browser URL. No Day 25 automated unit-test count, fresh-install test, role
matrix validation or Ultima status change is claimed.

## Current limits and Day 26 continuation

- Products and BDT prices are hardcoded demo data; no live product fetch is made.
- The cart exists only in browser memory and resets when the shop is recreated.
- The displayed total is a simple demo calculation; taxes, discounts, shipping,
  currency precision rules and final order pricing are outside this exercise.
- No quotation/order is created or submitted. Future server calls must validate
  products, quantities, access and authoritative prices independently.
- Quantities must be positive integers for updates. There is no explicit maximum
  quantity or error message for a rejected value in this button-based exercise.
- Layout is basic, with inline templates and no dedicated component stylesheet.

Day 26 will replace demo data with live Odoo products, add loading/empty/error
states for requests, and connect validated cart contents to draft quotations
while preserving server-side pricing and customer-order access rules.

## References

- [Owl 3 components](https://odoo.github.io/owl/documentation/v3/owl/reference/component.html)
- [Owl 3 reactivity](https://odoo.github.io/owl/documentation/v3/owl/reference/reactivity.html)
- Local owning sources: `addons/web/static/lib/owl/owl.js`,
  `addons/web/__manifest__.py` and `odoo/tools/js_transpiler.py` in the Odoo checkout.

[Back to the learning repository](../../README.md)

# Intensive Day 27 - Ecommerce Sales Dashboard

- **Original roadmap:** Days 62-63
- **Learning period:** November 15-18, 2026
- **Documented:** November 18, 2026
- **Environment:** Odoo 20 on Windows, PostgreSQL, Owl and Chart.js
- **Inspected chart library:** Chart.js 4.5.0
- **Addon:** `ecommerce_learning`
- **Practice currency:** Bangladeshi taka, **BDT**
- **Status:** Core dashboard practical completed and checked against the sample data. Browser evidence and server-side checks are distinguished below. Ultima completion was not updated or verified.

## What I built

Built a Sales Dashboard inside the existing ecommerce learning addon. It reads
real Odoo records and displays five KPI cards, optional date filters, a daily
sales chart and a horizontal top-products chart.

The dashboard handles loading, failed requests, invalid date ranges and empty
results. Sales Staff and Sales Managers can read it; other internal users and
portal customers are rejected by the server.

The working addon remains in the separate Odoo checkout. This repository
publishes the lesson documentation, not an installable copy or release of the
addon. Publishing this README does not commit the implementation repository or
change the Ultima tracker.

## Roadmap requirements and outcome

| Requirement | Outcome |
|---|---|
| Show product count, customer count, confirmed order count, sales total and average order value | Five live cards implemented, with explicit definitions below |
| Define date and status filters | Confirmed orders only; current company and its currency; optional local-date boundaries |
| Add sales-over-time and top-product charts | Daily vertical bars and up to five horizontal product bars |
| Provide a responsive layout | Responsive date inputs and card columns; chart labels adjusted and visually checked at 390 px |
| Compare results with sample orders and check role access | Sample totals reconciled; populated, empty and invalid browser states checked; role results recorded below |

## What is a KPI?

**KPI** means **Key Performance Indicator**: a measurement that summarizes
business activity. A useful dashboard starts by defining exactly which records
and values belong in each measurement.

### KPI definitions used in this lesson

All searches use the signed-in user's normal Odoo permissions and record rules.
The dashboard does not use `sudo()` to read sales or customer data.

| Card | Model and calculation | Scope |
|---|---|---|
| Product variants | `product.product.search_count()` | Active, saleable variants belonging to the current company or shared across companies |
| Customers | `res.partner.search_count()` | Active customer records with `customer_rank > 0`, in the current company or shared |
| Confirmed orders | `sale.order.search_count(domain)` | Status `sale`, current company, company currency and selected dates |
| Confirmed sales total | Sum of `amount_total` on matching orders | Includes tax; uses the same order domain |
| Average order value | Sales total divided by confirmed order count | Returns `0.0` when there are no matching orders |

Product variants are counted separately. Customer count measures matching
partner records, not deduplicated commercial organizations or customers who
purchased during the selected period.

**Date filters affect the three order KPIs and both charts. Product and customer
counts remain current snapshots.**

### Status and currency rules

The base order domain is:

~~~python
domain = [
    ("state", "=", "sale"),
    ("company_id", "=", request.env.company.id),
    ("currency_id", "=", request.env.company.currency_id.id),
]
~~~

| Order status | Included? |
|---|---|
| Quotation: `draft` | No |
| Quotation sent: `sent` | No |
| Sales order: `sale` | Yes, if the other filters also match |
| Cancelled: `cancel` | No |

Invoice and payment statuses are not additional filters. A confirmed order can
count whether it is uninvoiced or fully invoiced. This measures confirmed order
value, not cash received.

This version **filters to the company's currency**. It does not add USD and BDT
amounts together or convert foreign-currency orders. In the practice company,
the currency is BDT, so a USD order is excluded even if confirmed.

## BDT pricelist setup

During the exercise, a quotation selected `Default (USD)` even though the
company currency was BDT. That order could not serve as the BDT dashboard test.

The existing **Learning Ecommerce - Bangladeshi Taka** pricelist was already
configured for the learning API. Its priority was moved ahead of the generic
USD list, making it the default for new quotations for the inspected customers.
A new quotation was checked using the Sales user's permissions and selected BDT.
Existing orders were checked for unchanged references, states, currencies and
totals during this configuration change.

For a reproduction, configure an active BDT pricelist for the company and check
the selected customer's effective pricelist. A customer-specific pricelist can
override a generic default. Check the quotation's displayed currency before
confirming sample orders.

## Open and update the exercise

Sign in to the local Odoo database with an internal Sales account:

~~~text
http://localhost:8069/web/login?db=odoo20dev
~~~

Open **Ecommerce Learning -> Sales Dashboard**. Choose optional From and To
dates, then click **Load dashboard**. Leaving a boundary blank leaves that side
of the date range unrestricted.

After adding the asset and XML menu entries, upgrade the addon. Run these
commands in **PowerShell from the Odoo checkout**, after stopping the existing
Odoo server. Adapt the database name and configuration for another installation.

~~~powershell
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d odoo20dev -u ecommerce_learning --stop-after-init --no-http --max-cron-threads=0
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf
~~~

The first command updates the addon and exits. The second starts the server.
Keep one server instance on port 8069; starting another instance does not reload
the code in the instance already serving the browser.

For JavaScript development, open the backend with asset debugging and select
Sales Dashboard:

~~~text
http://localhost:8069/odoo?debug=assets
~~~

Restart/rebuild assets as needed and refresh the browser. A hard refresh alone
does not always regenerate a previously built production bundle.

**PowerShell commands belong in a terminal. Only the JavaScript request examples
below belong in the browser's DevTools Console.**

## Implementation locations

Paths below are relative to the separate Odoo checkout.

| File | Responsibility |
|---|---|
| `custom-addons/ecommerce_learning/controllers/main.py` | Authenticated dashboard route, validation, domains, KPIs and chart data |
| `custom-addons/ecommerce_learning/static/src/day27/dashboard.js` | Owl component, inline template, signals, RPC request, cards and charts |
| `custom-addons/ecommerce_learning/views/ecommerce_shop_views.xml` | Dashboard client action and restricted menu |
| `custom-addons/ecommerce_learning/__manifest__.py` | Backend JavaScript asset registration and existing XML data registration |
| `custom-addons/ecommerce_learning/models/res_company.py` | Existing learning-pricelist configuration used by the ecommerce APIs |
| `addons/web/static/src/core/utils/chart_hook.js` | Odoo's chart lifecycle helper |

The dashboard JavaScript is included in `web.assets_backend`. The action's tag
and the JavaScript registry key both use `ecommerce_learning.dashboard`.
The menu is restricted to `sales_team.group_sale_salesman`; Sales Managers
inherit the required Sales permission. The controller independently checks
that permission before validating dates or reading records.

## Dashboard JSON-RPC endpoint

| Setting | Value |
|---|---|
| URL | `/learning/dashboard` |
| Method | `POST` |
| Route type | `jsonrpc` |
| Authentication | Existing Odoo user session: `auth="user"` |
| Parameters | Optional `date_from` and `date_to` |
| Date format | Exact `YYYY-MM-DD`; omitted parameters or `null` mean unrestricted |

### Browser request

Run this JavaScript in the Console of an Odoo page where a Sales user is signed
in. It uses the existing same-origin login session.

~~~javascript
fetch("/learning/dashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
            date_from: "2026-11-16",
            date_to: "2026-11-16",
        },
        id: 27,
    }),
})
    .then(response => response.json())
    .then(data => console.log(JSON.stringify(data, null, 2)));
~~~

### Sample response

This is output for comparison, not code to paste into the Console as a request.
IDs and values belong to the learning database and are not installation defaults.

~~~json
{
  "jsonrpc": "2.0",
  "id": 27,
  "result": {
    "confirmed_order_count": 2,
    "product_count": 9,
    "customer_count": 1,
    "confirmed_sales_total": 134700.0,
    "currency": "BDT",
    "average_order_value": 67350.0,
    "sales_over_time": [
      {"date": "2026-11-16", "total": 134700.0}
    ],
    "top_products": [
      {
        "product_id": 3,
        "name": "Ultima Elite RO Hot & Cold Water Purifier",
        "total": 134700.0
      }
    ]
  }
}
~~~

### Error handling

| Condition | Controller error message |
|---|---|
| Signed-in user lacks Sales access | `Sales Staff or Manager access is required.` |
| Invalid type, impossible date or noncanonical date string | `Dates must use YYYY-MM-DD format.` |
| Start date is after end date | `Start date must not be after end date.` |
| Date boundary cannot be represented safely | `Date range is outside supported limits.` |

Controller business errors are dictionaries inside the JSON-RPC `result`, for
example `result.error`. They can arrive with HTTP 200. A signed-out request is
rejected by Odoo authentication with a top-level JSON-RPC error, such as
`Odoo Session Expired`; it does not reach the dashboard's Sales-group check.

## Date filtering and timezone handling

Dates are parsed with `datetime.strptime()` and compared with `isoformat()` to
require the exact input format. Parsing catches `TypeError` and `ValueError`;
boundary construction also catches unsupported extreme dates.

Odoo stores datetimes as naive UTC values. The controller obtains the effective
timezone from `request.env.tz`, which uses the context/user timezone and falls
back to UTC. For confirmed orders, `date_order` normally holds the confirmation
date and time.

- From means **at or after local midnight** on the selected start date.
- To means **before local midnight of the following day**, including the entire
  selected end date.
- Each local boundary is converted to UTC before it is added to the domain.
- With no date parameters, all otherwise accessible matching dates are included.

For the inspected `Asia/Karachi` user, November 16 corresponds to the UTC range
from **November 15 at 19:00 inclusive** to **November 16 at 19:00 exclusive**.
An end condition at midnight at the beginning of November 16 would incorrectly
exclude most of that day.

The same completed domain is used for order count and record retrieval:

~~~python
confirmed_order_count = request.env["sale.order"].search_count(domain)
confirmed_orders = request.env["sale.order"].search(domain)

confirmed_sales_total = sum(
    order.amount_total for order in confirmed_orders
)
average_order_value = (
    confirmed_sales_total / confirmed_order_count
    if confirmed_order_count
    else 0.0
)
~~~

## Chart data preparation

### Daily confirmed sales

The controller converts each matching order's `date_order` from UTC to the same
effective user timezone. It groups by local ISO date, adds `amount_total` and
returns rows sorted chronologically:

~~~python
sales_over_time = [
    {"date": day, "total": sales_by_date[day]}
    for day in sorted(sales_by_date)
]
~~~

Only dates with matching orders are returned. Dates without orders are not
zero-filled. Thus a November 16-17 range can show one bar for November 16.
An entirely empty range returns `[]`.

### Top five product variants

The controller traverses `confirmed_orders.order_line` and groups by product
variant ID. Sections, notes, down-payment lines and lines without a product are
skipped. It adds `line.price_total`, which includes tax and the line's discount,
then sorts by descending total, using product ID to break ties:

~~~python
top_products = sorted(
    product_sales.values(),
    key=lambda item: (-item["total"], item["product_id"]),
)[:5]
~~~

Rows contain `product_id`, `name` and `total`. They rank confirmed sales value,
not product quantity or paid/invoiced revenue. The top-five sum is not intended
to represent every product when more than five products match.

## Owl component and request flow

The component uses the signal-based Owl API already present in this Odoo
checkout:

~~~javascript
data = signal(null);
loading = signal(false);
error = signal("");
dateFrom = signal("");
dateTo = signal("");
~~~

The date inputs update their signals on change. The Load dashboard button sends
the selected values to the controller:

~~~javascript
const result = await rpc("/learning/dashboard", {
    date_from: this.dateFrom() || null,
    date_to: this.dateTo() || null,
});
~~~

Unlike a raw `fetch()` response, Odoo's `rpc()` helper returns the controller's
result dictionary directly. The component checks `result.error`, then stores
successful data with `this.data.set(result)`.

The component guards against duplicate in-flight loads, disables the button and
date inputs while loading, clears old data before a request and resets loading
in `finally`. Consequently an invalid-range response displays its error and
hides the previous cards and charts. A subsequent successful load can display
them again. Date changes are applied when Load dashboard is clicked.

The `kpiCards` getter converts the returned values into an array. A single
`t-foreach` template renders all five cards with stable keys. Bootstrap column
classes provide one column on narrow screens, two at the small breakpoint and
five on wide screens.

### Drawing both charts

Both charts use Odoo's existing helper:

~~~javascript
import { useChart } from "@web/core/utils/chart_hook";

salesChart = useChart(() => this.getSalesChartConfig());
topProductsChart = useChart(() => this.getTopProductsChartConfig());
~~~

The canvases use `t-ref="this.salesChart.ref"` and
`t-ref="this.topProductsChart.ref"`. The helper loads `web.chartjs_lib`, creates
the charts after mounting/patching and destroys previous instances and
unmounted charts. No external CDN script was added.

- Daily sales: vertical bars, ISO-date labels and daily totals.
- Top products: horizontal bars using `indexAxis: "y"` and product totals.
- Both use `responsive: true`, `maintainAspectRatio: false` and a 300 px container.
- Empty arrays show messages instead of canvases.

### Mobile chart correction

The first 390 px check showed a clipped product name and crowded numeric ticks.
`wrapProductLabel()` now groups words into lines of approximately 18 characters,
and the product chart receives arrays of label lines. The value-axis tick
callback uses `Intl.NumberFormat` with compact notation and up to four ticks,
producing labels such as `50K`, `100K` and `150K`.

A later user-supplied mobile screenshot showed the complete purifier name on
three lines and readable compact ticks. The numeric data was not reduced or
rounded by this display change.

## Sample orders and reconciliation

Two confirmed BDT orders used the same product variant:

| Reference | Quantity | Order total including tax | Included in the November 16 result? |
|---|---:|---:|---|
| S00015 | 1 | BDT 44,900 | Yes |
| S00016 | 2 | BDT 89,800 | Yes |

~~~text
Confirmed order count = 2
Confirmed sales total = 44,900 + 89,800 = BDT 134,700
Average order value = 134,700 / 2 = BDT 67,350
~~~

The divisor is **two orders**, not three product units. Daily sales for
November 16 and the purifier's product total both equal BDT 134,700.

S00014 was a cancelled USD order and was excluded. Draft BDT quotations also
remained outside the confirmed-order totals. The cancelled sample had both a
different status and a different currency; that sample alone does not isolate
the effect of the cancellation filter.

## Verification evidence

### Sample data and browser evidence

| Exercise | Observed result and evidence |
|---|---|
| Initial zero-order request | Zero order count, zero total and zero average without division errors |
| Product and customer cards | 9 eligible variants and 1 customer in the inspected user's scope |
| One confirmed BDT order | Saved-record/direct-controller check of S00015: count 1, total and average BDT 44,900 |
| Two confirmed orders | Native Sales view and dashboard request showed count 2, BDT 134,700 total and BDT 67,350 average |
| November 16 filter | Browser JSON response included the two orders and expected values |
| Daily chart | Desktop screenshot showed the November 16 bar; tooltip showed BDT 134,700 |
| Product chart | Desktop screenshot showed one horizontal purifier bar matching the sample total |
| November 17 empty range | Zero order KPIs, unchanged 9/1 snapshot counts and both empty-chart messages |
| Reversed range, November 18 to November 16 | Red validation message; old cards/charts hidden |
| Narrow chart layout | Initial clipping observed; later 390 px screenshot showed wrapped product text and compact ticks |
| Internal account without Sales permission | Browser JSON response returned only the Sales-access error |

The one-order numeric reconciliation included a direct controller/database check;
it is not presented as a separately captured browser dashboard response.
Desktop five-card layout and mobile chart readability were visually observed;
an exhaustive mobile review of every screen element was not performed.

### Server-side and file checks

- Python and JavaScript syntax checks passed after the final corrections.
- Inline templates parsed as XML; both canvas references and the configured
  asset, client action and menu links were checked.
- The addon upgrade succeeded and the menu/action records were inspected.
- Restarted servers served the updated JavaScript; unauthenticated dashboard
  requests returned the expected session-authentication rejection.
- The real saved controller was invoked with the existing accounts' normal
  environments against the database. Sample counts, totals, chart data and empty
  results matched expectations. These invocations used a request-context stub;
  they were not separate authenticated HTTP/browser sessions.
- Targeted date checks covered inclusive same-day selection, individual start
  or end boundaries, reversed ranges, impossible dates, noncanonical strings,
  wrong types, empty strings and unsupported extreme boundaries.
- Daily chart totals reconciled with the sample sales KPI; the sole product
  total also reconciled with it. Empty ranges returned empty chart arrays.

### Role results

| Role | Server-side controller result | Day 27 browser evidence |
|---|---|---|
| Sales Manager | Allowed; sample result 2 orders, BDT 134,700 | No separate Manager browser session claimed |
| Sales Staff | Allowed; sample result 2 orders, BDT 134,700 | Working dashboard, date filters and charts |
| Internal user without Sales access | Denied, with no KPI or chart data | Direct endpoint rejection shown |
| Portal customer | Denied, with no KPI or chart data | Server-side check only for this dashboard lesson |

A role named Manager in another addon does not automatically grant Sales
Manager permissions. Hiding a menu is also not sufficient authorization: the
route checks Sales membership independently, and normal ORM rules still apply.

No new full-addon automated regression count, fresh-install result, exhaustive
multi-company matrix, production deployment or tracker update is claimed.
The temporary verification commands/logs were not packaged as a reusable test
suite in this documentation repository.

## Debugging lessons

- **Route returned 404:** an older server still held port 8069. Restarting the
  verified serving instance loaded the new controller. The browser's subsequent
  JSON parse error came from trying to parse the HTML 404 page as JSON.
- **Unexpected token in the Console:** a PowerShell command or the sample JSON
  response was pasted as JavaScript. Use the correct terminal/request example.
- **Undefined name:** the returned `customer_count` needed its calculation
  assignment before the return dictionary.
- **Duplicate dashboard definition:** pasting a second decorator/method inside
  the existing one caused an indentation error. Replace the complete method
  rather than nesting another definition.
- **Extra indentation:** `product_sales = {}` needed to align with the other
  statements inside `dashboard()`.
- **Different count and total:** defining `domain` twice meant the first count
  missed the currency condition. A single shared domain fixed the mismatch.
- **Chart did not appear:** a hook and configuration need a matching canvas
  inside the template. The product-chart canvas was initially missing.
- **Mobile text clipping:** word-wrapped category labels and compact value ticks
  made the product chart readable at the inspected width.

## Current limits and Day 28 follow-up

- The implementation is a learning dashboard, with records loaded and grouped
  in Python. Large datasets need profiling and appropriate ORM aggregation.
- Count and matching records are fetched separately. Concurrent order changes
  could cause a temporary mismatch; no concurrency test was performed.
- Foreign-currency orders are excluded rather than converted.
- Product/customer snapshot definitions differ from period-based order metrics.
- Charts omit zero-sales dates. There is no continuous calendar-series filling.
- Top-five ranking was inspected in code and exercised with one sold product;
  multiple-product ordering, ties and the five-item cutoff need dedicated tests.
- Product-line totals can differ from order-level totals under some rounding or
  special-line configurations; the simple sample reconciled exactly.
- The label wrapper splits at word boundaries; unusually long unbroken names
  and a full cross-device matrix were not tested.
- Money cards currently interpolate the returned number; consistent decimal
  and locale formatting remain presentation improvements.
- A selected date change takes effect after a manual load; there is no polling,
  automatic refresh, saved filter preference or dashboard export.
- Loading guards and error branches exist, but no dedicated browser network-
  failure or slow-request matrix was recorded for the final chart component.
- Stronger Day 28 tests should include cancelled **BDT** orders independently of
  currency, sent quotations, tax/discount cases, timezone midnight boundaries,
  permission isolation and repeated chart loading/unmounting.

## References

- [Day 26: Owl with live products and orders](../Day%2026/README.md)
- [Day 25: Owl product cards and cart component](../Day%2025/README.md)
- [Day 22: Ecommerce API authentication and roles](../Day%2022/README.md)
- [Odoo dashboard tutorial](https://www.odoo.com/documentation/19.0/developer/tutorials/discover_js_framework/02_build_a_dashboard.html)
- [Odoo ORM and datetime reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Chart.js data structures and multiline labels](https://www.chartjs.org/docs/latest/general/data-structures.html)
- [Chart.js axis-label formatting](https://www.chartjs.org/docs/latest/axes/labelling.html)

The linked Odoo 19 documentation provides background. The implemented APIs and
signal/ref patterns were checked against the actual Odoo 20 checkout, especially
`odoo/orm/environments.py`, `odoo/orm/fields_temporal.py`,
`addons/sale/models/sale_order.py`, `addons/sale/models/sale_order_line.py` and
`addons/web/static/src/core/utils/chart_hook.js`.

[Back to the learning repository](../../README.md)

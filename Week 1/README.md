# Week 1 — Python Fundamentals & Odoo Development

**Status:** Completed ✅

## Daily Progress

| Day | Topic | Project / Achievement |
|---|---|---|
| Day 1 | Python Basics | Built a sales calculator with discounts and lead classification |
| Day 2 | Data Structures | Built a lead manager using lists, dictionaries, sets, and loops |
| Day 3 | Object-Oriented Programming | Built a sales management system using classes, inheritance, and method overriding |
| Day 4 | Developer Tools | Practiced Git, GitHub, VS Code debugging, and terminal commands |
| Day 5 | Odoo Environment | Set up Odoo 20, PostgreSQL, Python virtual environment, and custom addons |
| Day 6 | First Odoo Module | Built and installed the Ultima Lead Management module |
| Day 7 | Review & Computed Fields | Added automatic lead classification and tested recalculation |

## Final Project — Ultima Lead Management

Developed a working Odoo module with:

- Customer name, phone number, and budget fields
- Form and list views
- Navigation menus and access permissions
- Automatic lead classification using `fields.Selection` and `@api.depends()`
- Stored computed fields with PostgreSQL integration

### Classification Rules

| Budget | Category |
|---|---|
| ≥ 40,000 BDT | Premium |
| ≥ 25,000 BDT | Qualified |
| Below 25,000 BDT | Low Budget |

**Verified:** Changing a lead's budget from 35,000 to 45,000 BDT automatically updates its category from Qualified to Premium.

## Skills Acquired

Python fundamentals, OOP, Git, debugging, Odoo ORM, models, XML views, manifests, access rights, computed fields, PostgreSQL, and module upgrades.

## Outcome

Successfully completed Week 1 by progressing from basic Python programming to building, installing, debugging, and extending a functional Odoo module.
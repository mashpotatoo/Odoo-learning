# Day 6 – My First Odoo Module

## What I Built

Today I created my first working custom Odoo module:

**Ultima Lead Management**

The module allows users to create and view sales leads with:

- Customer Name
- Phone Number
- Budget

## Module Structure

```text
ultima_lead/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── lead.py
├── security/
│   └── ir.model.access.csv
└── views/
    └── lead_views.xml
# Week 2 — Odoo Models & ORM

**Status:** In Progress  
**Progress:** 5 of 7 days completed

## Learning Progress

| Day | Topic | Status |
|---|---|---|
| Day 8 | Models and Model Structure | Completed |
| Day 9 | Odoo Field Types | Completed |
| Day 10 | ORM Basics and CRUD | Completed |
| Day 11 | Recordsets | Completed |
| Day 12 | Model Relationships | Completed |
| Day 13 | Computed Fields and Onchange | Upcoming |
| Day 14 | University Student Module Practice | Upcoming |

## Completed Topics

### Day 8 — Models
- `models.Model`, `_name`, `_description`
- Student and Department model definitions
- Model naming and database table concepts

### Day 9 — Fields
- `Char`, `Text`, `Integer`, `Float`
- `Boolean`, `Date`, `Datetime`, `Selection`
- University Student model field definitions

### Day 10 — ORM Basics
- `env`, `create()`, `search()`, `browse()`
- `write()`, `unlink()`
- Basic CRUD operations

### Day 11 — Recordsets
- Iteration using `for`
- `mapped()`
- `filtered()`
- `sorted()`
- Combining recordset operations

### Day 12 — Relationships
- `Many2one` — Student to Department
- `One2many` — Department to Students
- `Many2many` — Student to Courses
- Inverse field concepts

## University Student Module Progress

**Completed as exercises:**
- Student and Department model definitions
- Basic student fields
- ORM CRUD syntax
- Recordset operations
- Relational field definitions

**Pending:**
- Computed and related fields
- Onchange behavior
- Integration of all model definitions
- Module installation and database testing

## Remaining Plan

### Day 13 — Business Logic
Practice `@api.depends`, `@api.onchange`, and related fields.

### Day 14 — University Student Practice
Integrate student information, department relationships, and CRUD operations into the module.

## Week 2 Goal

Build and test a working University Student module with student information, department relationships, and ORM operations.

**Current status:** Learning exercises completed through Day 12. Module integration and database testing remain pending.
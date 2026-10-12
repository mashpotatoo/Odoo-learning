# Week 2 — Odoo Models & ORM

**Status:** In Progress  
**Progress:** 6 of 7 days completed

## Learning Progress

| Day | Topic | Status |
|---|---|---|
| Day 8 | Models and Model Structure | Completed |
| Day 9 | Odoo Field Types | Completed |
| Day 10 | ORM Basics and CRUD | Completed |
| Day 11 | Recordsets | Completed |
| Day 12 | Model Relationships | Completed |
| Day 13 | Computed Fields and Onchange | Completed |
| Day 14 | University Student Module Practice | Upcoming |

## Completed Topics

### Day 8 — Models

- `models.Model`
- `_name` and `_description`
- Model naming and PostgreSQL table concepts
- Student and Department model definitions

### Day 9 — Field Types

- `Char`, `Text`, `Integer`, `Float`
- `Boolean`, `Date`, `Datetime`, `Selection`
- Student model field definitions

### Day 10 — ORM Basics

- `env`
- `create()`, `search()`, `browse()`
- `write()`, `unlink()`
- CRUD operations and search domains

### Day 11 — Recordsets

- Iteration
- `mapped()`
- `filtered()`
- `sorted()`
- Combining recordset operations

### Day 12 — Relationships

- `Many2one`
- `One2many`
- `Many2many`
- Inverse fields
- Student, Department, Teacher, and Course relationship examples

### Day 13 — Computed Fields and Business Logic

- Computed fields with `compute`
- Dependencies with `@api.depends`
- Stored computed fields
- Form updates using `@api.onchange`
- Related fields through `Many2one`
- Total marks, average marks, percentage, GPA performance, and department information exercises

## University Student Module Progress

**Completed as coding exercises:**
- Model definitions
- Basic field types
- ORM CRUD syntax
- Recordset operations
- Relational field definitions
- Computed fields
- Onchange methods
- Related fields

**Pending:**
- Integration into an installable Odoo module
- Required module structure and access permissions
- Student and Department records
- Database CRUD testing
- Relationship and computed-field verification

## Day 14 — Final Practice

Integrate and test the University Student module.

Planned student information:
- Name
- Roll number
- Email
- Phone
- Department
- GPA
- Date of birth

Verify model relationships and CRUD operations.

## Week 2 Goal

Build a working University Student module with student information, department relationships, and ORM operations.

**Current status:** Learning exercises completed through Day 13. Module integration and runtime verification are pending.
# Week 2 — Odoo Models & ORM

**Status:** In Progress  
**Progress:** 4 of 7 days completed

## Learning Progress

| Day | Topic | Status |
|---|---|---|
| Day 8 | Models and Model Structure | Completed |
| Day 9 | Odoo Field Types | Completed |
| Day 10 | ORM Basics and CRUD | Completed |
| Day 11 | Recordsets | Completed |
| Day 12 | Model Relationships | Upcoming |
| Day 13 | Computed Fields and Onchange | Upcoming |
| Day 14 | University Student Module Practice | Upcoming |

## Day 8 — Models

Learned:
- `models.Model`
- `_name`
- `_description`
- Model and database table naming
- Student and Department model definitions

## Day 9 — Field Types

Practiced eight field types:
- `Char`
- `Text`
- `Integer`
- `Float`
- `Boolean`
- `Date`
- `Datetime`
- `Selection`

Created a University Student model definition.

## Day 10 — ORM Basics

Practiced:
- `env`
- `create()`
- `search()`
- `browse()`
- `write()`
- `unlink()`

Understood CRUD operations and search domains.

## Day 11 — Recordsets

Practiced:
- Recordset iteration using `for`
- `mapped()` for field extraction
- `filtered()` for conditional filtering
- `sorted()` for ordering records
- Combining multiple recordset methods

### Combined Exercise

```python
students = env["university.student"].search([])

top_students = students.filtered(
    lambda student: student.gpa > 3.50
)

sorted_students = top_students.sorted(
    key=lambda student: student.gpa,
    reverse=True
)

names = sorted_students.mapped("name")
print(names)
```

## University Student Module Progress

**Completed as coding exercises:**
- Student and Department model definitions
- Eight student field types
- ORM CRUD syntax
- Recordset operations

**Still pending:**
- Relational fields
- Final model integration
- Module installation
- Database CRUD testing

## Remaining Plan

### Day 12 — Relationships
Learn `Many2one`, `One2many`, and `Many2many`.

### Day 13 — Computed Fields
Learn `@api.depends`, `@api.onchange`, and related fields.

### Day 14 — Practice
Integrate the University Student module, department relationships, and CRUD operations.

## Week 2 Goal

Build a working University Student module with student information, department relationships, and ORM operations.

**Current status:** Conceptual code exercises completed through Day 11. Odoo database testing is pending.
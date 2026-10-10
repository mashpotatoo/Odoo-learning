# Day 9 — Odoo Fields

**Week:** 2  
**Topic:** Odoo Field Types  
**Status:** Completed

## Learning Objectives

Understand how Odoo fields define and store different types of information in business models.

## Field Types Learned

| Field | Purpose | Example |
|---|---|---|
| Char | Short text | Student Name |
| Text | Long text | Student Address |
| Integer | Whole numbers | Age |
| Float | Decimal numbers | GPA |
| Boolean | True / False | Active Student |
| Date | Calendar date | Date of Birth |
| Datetime | Date and time | Admission Date |
| Selection | Predefined choices | Student Status |

## Practical Exercise — University Student Model

```python
from odoo import models, fields


class UniversityStudent(models.Model):
    _name = "university.student"
    _description = "University Student"

    name = fields.Char(string="Student Name", required=True)
    age = fields.Integer(string="Age")
    gpa = fields.Float(string="GPA")
    address = fields.Text(string="Student Address")
    is_active = fields.Boolean(string="Active Student")
    date_of_birth = fields.Date(string="Date of Birth")
    admission_date = fields.Datetime(string="Admission Date")

    status = fields.Selection(
        [
            ("active", "Active"),
            ("graduated", "Graduated"),
            ("suspended", "Suspended"),
        ],
        string="Student Status",
    )
```

## Key Learnings

- Defined eight different Odoo field types.
- Used `string` to specify display labels.
- Used `required=True` for mandatory fields.
- Learned the difference between Selection values and labels.
- Practiced writing and correcting an Odoo model.

## Outcome

Successfully wrote a University Student model containing eight fields.

**Testing:** Python code reviewed; Odoo installation and database testing pending.

**Next:** Day 10 — Odoo ORM Basics and CRUD Operations.
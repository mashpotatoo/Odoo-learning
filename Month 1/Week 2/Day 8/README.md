# Day 8 — Odoo Models

**Status:** Completed ✅

## Topics Learned

- `models.Model` — Base class for Odoo models
- `_name` — Technical model identifier
- `_description` — Human-readable model description
- `_table` — Custom PostgreSQL table name
- Difference between a model and a record
- Creating records with the Odoo ORM
- Default PostgreSQL table naming conventions

## Practical Exercises

### University Student Model

```python
from odoo import models, fields

class UniversityStudent(models.Model):
    _name = "university.student"
    _description = "University Student"

    name = fields.Char(string="Student Name", required=True)
```

### University Department Model

```python
from odoo import models, fields

class UniversityDepartment(models.Model):
    _name = "university.department"
    _description = "University Department"

    name = fields.Char(string="Department Name", required=True)
```

## Key Learnings

- Odoo model names conventionally use dots, such as `university.student`.
- PostgreSQL table names use underscores, such as `university_student`.
- `_table` can override the default table name.
- `create()` creates a new database record, not a new model.
- Python is case-sensitive: `models.Model` is correct.

## Result

Successfully wrote and corrected two Odoo model definitions.

**Note:** Models were practiced in Python code but have not yet been installed and tested in Odoo.

**Next:** Day 9 — Odoo Fields.
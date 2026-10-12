# Day 12 — Odoo Model Relationships

**Week:** 2  
**Status:** Completed

## Learning Objectives

- Understand relational fields in Odoo.
- Learn `Many2one`, `One2many`, and `Many2many`.
- Connect Student, Department, Teacher, and Course models.

## 1. Many2one

Many students can belong to one department.

```python
department_id = fields.Many2one(
    "university.department",
    string="Department"
)
```

## 2. One2many

One department can have multiple students.

Inside the Department model:

```python
student_ids = fields.One2many(
    "university.student",
    "department_id",
    string="Students"
)
```

The inverse field `department_id` must exist in the Student model.

## 3. Many2many

Students can enroll in multiple courses, and courses can have multiple students.

```python
course_ids = fields.Many2many(
    "university.course",
    string="Courses"
)
```

## 4. Final Coding Exercise

```python
from odoo import models, fields

class UniversityStudent(models.Model):
    _name = "university.student"
    _description = "University Student"

    name = fields.Char(string="Student Name")

    department_id = fields.Many2one(
        "university.department",
        string="Department"
    )

    course_ids = fields.Many2many(
        "university.course",
        string="Courses"
    )
```

## Key Learnings

| Field | Relationship |
|---|---|
| `Many2one` | Many records point to one record |
| `One2many` | One record references multiple records through an inverse Many2one |
| `Many2many` | Multiple records connect to multiple records |

## Outcome

- Practiced all three relationship types.
- Correctly defined Department and Course relationships.
- Understood the purpose of inverse fields.
- Completed the final coding exercise.

**Testing:** Syntax reviewed; related models and module integration have not yet been tested in Odoo.

**Next:** Day 13 — Computed Fields, `@api.depends`, `@api.onchange`, and Related Fields.
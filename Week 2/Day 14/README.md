# Day 14 — University Student Module Integration

## Objective
Integrate everything learned during Week 2 into a working Odoo 20 module with two related models.

## What I Built
**Module:** `university_student`

A University Student Management application with:

- Student and Department models
- `Many2one` and `One2many` relationships
- List and form views
- University Management navigation menus
- Access permissions for internal users
- PostgreSQL-backed record storage through the Odoo ORM

## Module Structure

```text
university_student/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── student.py
│   └── department.py
├── security/
│   └── ir.access.csv
└── views/
    ├── student_views.xml
    └── department_views.xml
```

## Key Concepts

**Many2one:** Each student belongs to one department.

```python
department_id = fields.Many2one(
    "university.department",
    string="Department"
)
```

**One2many:** A department can contain multiple students.

```python
student_ids = fields.One2many(
    "university.student",
    "department_id",
    string="Students"
)
```

Both fields describe the same relationship from opposite directions.

## Odoo 20 Security

The Odoo 20 source used in this project uses `ir.access.csv` with this format:

```csv
id,name,model_id,group_id/id,operation,domain
access_university_student,access.university.student,university.student,base.group_user,crud,
access_university_department,access.university.department,university.department,base.group_user,crud,
```

`crud` grants Create, Read, Update, and Delete permissions.

## Installation

```powershell
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d odoo20dev -i university_student --stop-after-init --no-http
```

**Result:** Module installed successfully.

## Functional Testing

- [x] Module installed without errors
- [x] University Management menu appeared
- [x] Student list view displayed records
- [x] Department list view displayed records
- [x] Created a Computer Science department
- [x] Created a student record
- [x] Assigned the student to Computer Science
- [x] Verified the student appeared inside the department's Students tab

## Challenges Solved

1. Identified the access-control format used by the local Odoo 20 source.
2. Replaced the older `ir.model.access.csv` format with `ir.access.csv`.
3. Corrected XML filenames referenced in the module manifest.
4. Successfully installed the module and verified its relationships.

## Outcome

Completed a functional University Student Management module integrating Python models, ORM relationships, XML views, menus, security permissions, and database persistence.

**Status:** Completed — October 12, 2026
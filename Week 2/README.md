# Week 2 — Odoo Module Development

**Status:** Completed

## Goal

Learn the fundamentals of Odoo module development and build a working application using the Odoo ORM, XML views, access permissions, and model relationships.

## Learning Progress

| Day | Topic | Status |
|---|---|---|
| 8 | Odoo module structure and manifest | Completed |
| 9 | Models and fields | Completed |
| 10 | XML views and menus | Completed |
| 11 | Access rights and security | Completed |
| 12 | Many2one relationships | Completed |
| 13 | One2many relationships | Completed |
| 14 | University Student Module Integration | Completed |

## Final Project — University Student Management

Built a working Odoo 20 application with two connected models:

- `university.student`
- `university.department`

### Features

- Student registration and management
- Department registration and management
- Student-to-department assignment
- Department-to-students relationship
- List and form interfaces
- Navigation menus
- Internal-user access permissions

### Technologies

- Python
- Odoo 20
- Odoo ORM
- XML
- PostgreSQL
- PowerShell
- Git and GitHub

## Important Lessons

1. Odoo models define database-backed business objects.
2. XML views control how records appear in the interface.
3. A manifest declares module metadata and files to load.
4. Security rules control which users can access records.
5. Many2one and One2many represent opposite sides of a relationship.
6. Odoo versions can introduce breaking changes, so checking the installed source is important.
7. Successful installation should be followed by functional testing in the UI.

## Week 2 Result

Successfully installed and tested the University Student Management module, including both directions of the Student–Department relationship.

**Next:** Week 3 — Continue the Odoo development roadmap.
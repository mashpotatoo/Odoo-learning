# Intensive Day 9 - Department and Course Modules

- **Original roadmap:** Days 32-33
- **Completed:** October 30, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Modules:** `university_student` and the new `university_course`
- **Status:** Complete - implementation and manual interface checks

## Overview

Created a separate Course addon that depends on University Student Management. Reused the existing Department model, extended it with a course relationship, and added a Courses tab to the Department form through view inheritance.

The original Month/Week/Day lessons remain separate from this intensive roadmap entry. The Department model already existed in `university_student`; this lesson extended it rather than creating or moving it into another addon. The Course addon has no dependency on a Teacher addon.

## Completed objectives

- [x] Create the `university.course` model with course name, code, credit hours, department, and active status.
- [x] Link each course to one department through a required `Many2one` field.
- [x] Extend the existing Department model with a reverse `One2many` relationship.
- [x] Add Course list and form views and a menu under University Management.
- [x] Display linked courses in a read-only Courses tab on the Department form.
- [x] Configure Administrator, Teacher, and Student permissions.
- [x] Install the addon and create a course in the live interface.
- [x] Check the department relationship and confirm role behavior manually.

## Addon structure

The addon lives under the local Odoo checkout's `custom-addons` directory:

```text
university_course/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   |-- course.py
|   `-- department.py
|-- security/
|   `-- ir.access.csv
`-- views/
    |-- course_views.xml
    `-- department_views.xml
```

The root `__init__.py` imports `models`. The model package imports both `course` and `department`.

## Course model

`models/course.py`:

```python
from odoo import fields, models


class UniversityCourse(models.Model):
    _name = "university.course"
    _description = "University Course"
    _order = "code, name"

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code", required=True)
    credit_hours = fields.Integer(string="Credit Hours", default=3)

    department_id = fields.Many2one(
        "university.department",
        string="Department",
        required=True,
        ondelete="restrict",
    )

    active = fields.Boolean(default=True)
```

Each course belongs to one department. `ondelete="restrict"` configures protection against deleting a department while courses reference it. This deletion restriction was not exercised during the manual checks.

Course name, code, and department are required. Credit hours default to 3. The model does not yet enforce unique course codes or a positive range for credit hours.

## Department extension

`models/department.py`:

```python
from odoo import fields, models


class UniversityDepartment(models.Model):
    _inherit = "university.department"

    course_ids = fields.One2many(
        "university.course",
        "department_id",
        string="Courses",
    )
```

Using `_inherit` without a new `_name` extends the existing Department model. `course_ids` retrieves courses whose `department_id` points to that department; it does not require maintaining a second independent department assignment.

## Views and menus

`views/course_views.xml` defines:

- A Course list showing code, name, department, and credit hours.
- A Course form showing name, code, department, credit hours, and active status.
- The `action_university_course` window action with `list,form` modes.
- A Courses menu under `university_student.menu_university`, after Departments.

`views/department_views.xml` extends the existing Department form:

```xml
<odoo>
    <record id="view_department_form_courses" model="ir.ui.view">
        <field name="name">university.department.form.courses</field>
        <field name="model">university.department</field>
        <field name="inherit_id"
               ref="university_student.view_university_department_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page name="courses" string="Courses">
                    <field name="course_ids" readonly="1">
                        <list>
                            <field name="code"/>
                            <field name="name"/>
                            <field name="credit_hours"/>
                        </list>
                    </field>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

The existing Students tab remains. The Courses tab displays the department's linked courses; administrators manage those records through the Courses menu. The tab's read-only setting controls the interface, while the access CSV defines model permissions.

## Role permissions

Reused the three existing groups from `university_student`:

| Role | Create | Read | Edit | Delete |
|---|---|---|---|---|
| University Administrator | Yes | Yes | Yes | Yes |
| University Teacher | No | Yes | No | No |
| University Student | No | Yes | No | No |

`security/ir.access.csv` uses the Odoo 20 format already present in the Student addon:

```csv
id,name,model_id,group_id/id,operation,domain
access_course_admin,Course Administrator,university.course,university_student.group_university_admin,crud,
access_course_teacher,Course Teacher,university.course,university_student.group_university_teacher,r,
access_course_student,Course Student,university.course,university_student.group_university_student,r,
```

The empty domains add no per-user or per-department course restriction. Teacher and Student roles can read courses under these declarations. Students' existing own-record restriction on student records is separate from Course access.

## Manifest and installation

The addon depends on `university_student`, which supplies the Department model, role groups, and parent menu. The manifest loads data in this order:

```python
"depends": ["university_student"],
"data": [
    "security/ir.access.csv",
    "views/course_views.xml",
    "views/department_views.xml",
],
"application": False,
"installable": True,
```

Upgrading Student Management alone does not install this separate addon. The lesson's installation procedure was to restart Odoo for the Python changes, enable Developer Mode, update the Apps List, remove the default Apps search filter, and install University Course Management. Removing the filter is relevant because `application` is `False`.

The user confirmed installation, and the supplied screenshots show the Courses menu and the inherited Department tab in the live application.

## Verification evidence

### File checks

Before installation, static checks passed for Python syntax, manifest data-file existence, XML syntax, menu/action/view references, the inherited notebook target, and the three role-access rows. The saved addon source was inspected again while preparing this README.

These are file-level checks, not an automated Odoo installation or security test suite.

### Screenshots supplied during the lesson

| Screenshot | Observed result |
|---|---|
| University Management > Courses | The list contains course code **CS1101**, linked to **Computer Science**, with **3** credit hours. |
| Computer Science > Courses tab | The same **CS1101** course appears with **3** credit hours, demonstrating the reverse department relationship for this record. |

### User-confirmed manual role checks

| Account | Exercise | Reported result |
|---|---|---|
| Teacher | Open Courses and inspect create, edit, and delete availability. | Can view courses; cannot create, edit, or delete. |
| Student | Repeat the course access check. | User confirmed the requested read-only behavior. |
| University Administrator | Create temporary course TEST001, change credit hours from 3 to 4, save, then delete the temporary course while keeping CS1101. | User confirmed completion. |

Teacher behavior was explicitly described by the user. Student and Administrator checks were confirmed with "done" after the respective exercises. These confirmations establish the manual interface results reported during the lesson; no separate screenshots were supplied for them.

### Verification limits

No new automated ORM permission tests, direct unauthorized API attempts, installation-log audit, or department-deletion test were performed for Day 9. The role declarations were inspected, and the user confirmed interface behavior. Earlier Student-addon test counts are not Course-addon test results.

## Outcome

Installed a separate Course addon, linked courses to existing departments, added Course views and a Department Courses tab, and completed manual checks for Administrator, Teacher, and Student roles.

**Activity log:** Built and installed the Course addon, extended Departments with linked courses, added views and role permissions, and verified course creation, department display, and role behavior through screenshots and user-confirmed exercises.

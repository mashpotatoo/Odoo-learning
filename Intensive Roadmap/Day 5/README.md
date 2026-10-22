# Intensive Day 5 - View Inheritance and Module Interaction

- **Completed:** October 22, 2026
- **Extension addon:** `university_student_custom`
- **Dependency:** `university_student`
- **Environment:** Odoo 20 on Windows
- **Status:** Complete - implementation, installation, automated checks, and interface verification

## Overview

Created and installed a separate customization addon that depends on University Student Management and extends its student list view. The inherited view displays the existing **Status** field immediately after **GPA**.

This lesson follows the intensive checklist **View Inheritance and Module Interaction (Original Days 26-27)**. It is tracked separately from the original Month/Week/Day lessons.

## Objectives and completed work

- [x] Create a separate addon with an explicit dependency on `university_student`.
- [x] Extend the existing list view through `inherit_id` and XPath.
- [x] Install the addon and verify the Status column and existing permissions.

## Addon structure

```text
custom-addons/
└── university_student_custom/
    ├── __init__.py
    ├── __manifest__.py
    └── views/
        └── student_views.xml
```

### 1. Python initializer

`__init__.py` is empty. This addon contains an XML view extension and does not define Python models.

### 2. Manifest and module dependency

Complete `__manifest__.py`:

```python
{
    "name": "University Student Customizations",
    "version": "1.0.0",
    "summary": "Extend University Student views",
    "depends": ["university_student"],
    "data": [
        "views/student_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

The dependency makes the parent module's model, fields, and view external IDs available before the customization is loaded. The Status field is the existing `state` field introduced during the workflow lesson.

`application=False` identifies this addon as a customization rather than a standalone application. It does not add a separate app menu or define additional access grants.

### 3. Inherited student list view

Complete `views/student_views.xml`:

```xml
<odoo>
    <record id="view_university_student_list_custom" model="ir.ui.view">
        <field name="name">university.student.list.custom</field>
        <field name="model">university.student</field>
        <field name="inherit_id"
               ref="university_student.view_university_student_list"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='gpa']" position="after">
                <field name="state"/>
            </xpath>
        </field>
    </record>
</odoo>
```

| Element | Purpose |
|---|---|
| `model="university.student"` | Applies the view to the existing student model. |
| `inherit_id` | References the original list view by its module-qualified external ID. |
| `//field[@name='gpa']` | Locates GPA in the parent view. |
| `position="after"` | Inserts the new column immediately after GPA. |
| `<field name="state"/>` | Displays the existing field using its label, Status. |

The parent view record remains unchanged. Odoo combines the parent and extension when preparing the list view for each user.

## Resulting interface

The composed list has this field order:

```text
Student Name → Roll Number → Department → GPA → Status → Email → Phone
```

Phone retains the original optional/hidden behavior. The existing GPA sorting, row decorations, form workflow, guardian information, and search configuration remain available.

## Installation and deployment

The completed deployment used the existing native Windows Odoo checkout and database `odoo20dev`:

1. Tested the addon in the disposable database `university_security_test_20261021`.
2. Verified the intended Odoo process and stopped the running service.
3. Created a PostgreSQL custom-format backup and checked its archive listing.
4. Installed `university_student_custom` with Odoo's command-line installer.
5. Checked the composed view and permissions using the existing University test accounts.
6. Restarted Odoo and verified one listener on `127.0.0.1:8069` and login HTTP 200.

The installation command, run from the Odoo checkout after stopping the existing service, was equivalent to:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf -d odoo20dev -i university_student_custom --no-http --http-port=0 --stop-after-init
```

The installation log confirmed:

```text
Module university_student_custom loaded
Modules loaded.
```

## Verification and results

### Automated regression tests

Reran the 20 existing University Student tests with the new addon installed:

```text
0 failed, 0 error(s) of 20 tests
```

These tests cover the previously implemented role permissions, own-record access, workflow methods, GPA constraint, and guardian-field inheritance. They are existing regression tests, not 20 new tests written for the view extension.

### Additional integration and live checks

| Check | Result |
|---|---|
| Custom addon installed and its parent dependency available | Passed |
| Status appears exactly once, directly after GPA | Passed for Student, Teacher, and University Administrator |
| Stored parent list view remains unchanged | Passed |
| Student sees only their linked student record | Passed |
| Student cannot edit Status, invoke Confirm, or edit guardian details | Direct server operations denied |
| Student cannot directly read another student's record | Denied |
| Teacher and Administrator retain visibility of existing student records | Passed |
| Four existing student records and their values are preserved | Passed; verification changes were rolled back |
| Restarted Odoo login page | HTTP 200 |

### Interface confirmation

The user's screenshot confirmed **Status immediately after GPA** in the student list. It showed the existing Confirmed and Draft status labels. This completed the final interface check for the lesson.

## Observations requiring separate follow-up

- The screenshot also showed an existing test record with GPA `5.00`. The GPA constraint does not automatically correct existing values; correction of that record was not verified during Day 5.
- After the initial installation health check, a later auto-vacuum job logged a Windows `PermissionError` while deleting a temporary upload file. That attachment-cleanup issue was not repaired or retested as part of this view-inheritance lesson.

## Learning outcome

Used an addon dependency and a module-qualified view reference to extend another module's interface. Practised targeting a specific field with XPath while preserving the parent view and existing access behavior.

## Next step

Continue with **Intensive Day 6 - Month 1 Review**. The review has not been marked complete by this README.

**Activity log:** Created and installed a dependent Odoo addon, extended the student list with a Status column through view inheritance, and verified the result with regression tests, live permission checks, and interface confirmation.

# Intensive Day 7 - Improve the Student Module

- **Completed:** October 24, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Modules:** `university_student` and `university_student_custom`
- **Status:** Complete

## Overview

Extended University Student Management with a computed Age field, a constraint that rejects future birth dates, and an inherited form view. Fixed a timezone-related computed-field cache bug discovered during testing, then upgraded both addons and verified the live application.

This lesson follows **Improve the Student Module (Original Days 29-30)** in the intensive checklist. It remains separate from the original Month/Week/Day lessons.

## Completed objectives

- [x] Calculate age from Date of Birth, accounting for whether this year's birthday has occurred.
- [x] Recompute age when Date of Birth changes, without storing a value that becomes outdated each year.
- [x] Reject future birth dates through a server-side constraint.
- [x] Insert a read-only Age field immediately after Date of Birth using view inheritance.
- [x] Hide Age when Date of Birth is empty.
- [x] Preserve guardian fields, the Status column, workflow, and role permissions.
- [x] Fix timezone-sensitive age caching and pass all 27 automated tests.
- [x] Upgrade the live addons, verify permissions and data preservation, and complete the interface exercise.

## Model extension

Updated `custom-addons/university_student/models/student_extension.py`. Using `_inherit` without a new `_name` extends the existing student model. The existing guardian fields remain in the same extension.

```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UniversityStudentExtension(models.Model):
    _inherit = "university.student"

    guardian_name = fields.Char(string="Guardian Name")
    guardian_phone = fields.Char(string="Guardian Phone")

    age = fields.Integer(
        string="Age",
        compute="_compute_age",
        store=False,
    )

    @api.depends("date_of_birth")
    @api.depends_context("tz", "uid")
    def _compute_age(self):
        today = fields.Date.context_today(self)

        for student in self:
            birth_date = student.date_of_birth

            if birth_date:
                birthday_pending = (
                    today.month,
                    today.day,
                ) < (
                    birth_date.month,
                    birth_date.day,
                )

                student.age = (
                    today.year - birth_date.year - birthday_pending
                )
            else:
                student.age = 0

    @api.constrains("date_of_birth")
    def _check_date_of_birth(self):
        today = fields.Date.context_today(self)

        for student in self:
            if student.date_of_birth and student.date_of_birth > today:
                raise ValidationError(
                    "Date of birth cannot be in the future."
                )
```

### Calculation and validation

The calculation subtracts one year when the birthday is still ahead. For example, on October 24, 2026, someone born October 25, 2000 is 25; someone born October 24, 2000 is 26.

`fields.Date.context_today(self)` uses the current user's timezone. An empty birth date produces an age of zero internally; the form hides that field until a birth date is supplied. Today's date is allowed and gives age zero.

`store=False` calculates age when needed instead of persisting it in the database. A later fresh read can show the new age after a birthday without editing Date of Birth. An already-open form does not automatically refresh at midnight. The field has no custom search method, so this lesson does not add Age filters or grouping.

The constraint runs when Date of Birth is supplied during creation or changed during an update. It rejects future dates at the server, including direct ORM calls. It does not automatically audit every historical record during an addon upgrade.

### Bug fixed: timezone-dependent cache

The first timezone-boundary test failed: after computing an age in UTC, reading the same record in a western timezone reused the cached UTC age even though the local calendar date was different.

Added `@api.depends_context("tz", "uid")` so the computed value's cache accounts for the timezone and user context. The regression test fixes the clock at October 24, 2026, 00:30 UTC and checks that a person born October 24, 2000 is 26 in UTC and 25 in Los Angeles. The final test run passed.

## Inherited student views

Updated the complete `custom-addons/university_student_custom/views/student_views.xml`, retaining the existing Status column extension:

```xml
<odoo>
    <!-- Add Status after GPA in the student list -->
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

    <!-- Add Age after Date of Birth in the student form -->
    <record id="view_university_student_form_custom" model="ir.ui.view">
        <field name="name">university.student.form.custom</field>
        <field name="model">university.student</field>
        <field name="inherit_id"
               ref="university_student.view_university_student_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='date_of_birth']" position="after">
                <field name="age"
                       readonly="1"
                       invisible="not date_of_birth"/>
            </xpath>
        </field>
    </record>
</odoo>
```

The customization addon continues to depend on `university_student`. Its manifest already loads this XML file. The parent views remain the inheritance targets; the Age insertion is defined in the dependent addon.

## Automated verification

Added `custom-addons/university_student/tests/test_student_day7.py` and imported it through the existing test package.

| New test coverage | Verified behavior |
|---|---|
| Birthday boundaries and batch calculation | Yesterday's birthday, today's birthday, and tomorrow's birthday produce the expected ages. |
| Birth-date change and clearing | Age updates after changing or removing Date of Birth. |
| Today's date and empty values | Both are accepted and produce zero internally. |
| Future-date creation and updates | Invalid single and mixed-batch operations fail; rejected updates roll back. |
| Birthday rollover | A fresh calculation advances age without changing Date of Birth. |
| Timezone boundary | UTC and Los Angeles use their respective local dates without sharing the wrong cached value. |
| Student access | A Student can read their own age, cannot change Date of Birth, and cannot read another student's age or birth date. |

**Final result: 27 tests passed, 0 failures, 0 errors** — seven new tests plus the existing 20 security, workflow, GPA, and guardian tests. The run used a separate test database, not the live student database. These results were obtained during Day 7 implementation, before writing this README.

## Deployment and live checks

- Created a PostgreSQL backup and verified that its archive could be listed before upgrading.
- Upgraded both addons; the upgrade log confirmed both modules loaded and the registry finished loading.
- Checked real visible records for the Student, Teacher, and Administrator roles against an independent age calculation.
- Confirmed the Student's existing own-record access and read-only Date of Birth permissions through direct ORM calls.
- Confirmed future birth dates are rejected on creation and update.
- Inspected the compiled views for all three roles: Age appears once after Date of Birth, is read-only, and is hidden when no birth date exists. Status remains after GPA.
- Rolled back temporary live verification changes and confirmed the five existing student records were preserved.
- Restarted the native Windows server and verified one listener on port 8069 and a successful login-page HTTP response. The inspected upgrade and startup logs had no ERROR, CRITICAL, or traceback entries at verification time.

## User-confirmed interface exercise

Using a Teacher or Administrator account, the user confirmed the requested exercise:

1. Set a test student's Date of Birth to January 1, 2000 and observe Age 26 on October 24, 2026.
2. Save and reopen the record to check the calculated age.
3. Attempt to save tomorrow's date and receive the validation error.
4. Restore a valid date and save.

The interface exercise is user-confirmed; no Day 7 screenshot was supplied. Automated and direct server checks are recorded separately above.

## Remaining maintenance

The Day 7 preflight found one existing out-of-range GPA value. Although the [Day 6 review](../Day%206/README.md) recorded a user confirmation of earlier cleanup, the later database check showed an invalid value still present. Day 7 did not correct that value; the existing GPA constraint and its regression tests remain in place.

The historical Windows attachment-cleanup permission issue noted in [Day 5](../Day%205/README.md) was not investigated or resolved by this lesson. Successful Day 7 startup checks do not establish that this separate background issue is fixed.

## Outcome

Completed automatic age calculation, future birth-date validation, inherited form placement, and the timezone cache fix, with all 27 tests passing and live and user-confirmed interface checks completed.

**Activity log:** Improved the Student module with automatic age calculation and birth-date validation, extended the form through inheritance, fixed a timezone cache bug, and verified the changes with 27 passing tests and live application checks.

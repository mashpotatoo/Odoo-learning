# Intensive Day 13 - Attendance Workflow

- **Original roadmap:** Days 38-39
- **Verified through:** November 1, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon / model:** `university_attendance` / `university.attendance`
- **Status:** Complete - attendance recording, result actions, lifecycle workflow, calculations, role checks, and live upgrade verified

## Overview

Built and installed an Attendance addon linking a student, a course, a date, and an attendance result. Each record has a separate lifecycle status with Confirm, Cancel, and Reset to Draft actions. Added dedicated Record Present/Absent actions, Student attendance totals and percentages, duplicate protection, views, and role-based access with own-attendance reads for Students.

This documentation records the implemented work and its verification. It remains separate from the original Month/Week/Day lessons and builds on the [Enrollment workflow lesson](../Day%2012/README.md).

## Roadmap scope

The live Ultima Day 13 checklist was inspected while preparing this README. It also lists:

- Add Record Present and Absent actions.
- Calculate attended classes, total classes, and attendance percentage.
- Test calculations and missing-data cases.

These requirements are implemented in the final addon. The original 52 regression checks pass against the updated source, and 41 additional checks cover the result actions, summaries, invalidation, and missing-data cases: 93 passing checks in total.

## Verified implementation

- Required student and course links with restricted deletion.
- Required attendance date defaulting to the current user's local date.
- Required attendance result: Present, Absent, or Late, without an automatic default.
- Draft, Confirmed, and Cancelled lifecycle states.
- Status checks within each workflow action.
- Draft-only Record Present and Record Absent actions.
- Per-student total classes, attended classes, and attendance percentage based on confirmed records.
- One attendance record per student/course/date combination.
- Administrator, Teacher, and Student permissions.
- Own-attendance read domain for Students.
- Role-limited form buttons and a read-only workflow status bar.
- Installation and runtime checks, plus the manual exercises described below.

## Addon structure

```text
university_attendance/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   |-- attendance.py
|   `-- student.py
|-- security/
|   `-- ir.access.csv
`-- views/
    |-- attendance_views.xml
    `-- student_views.xml
```

The root package imports `models`; `models/__init__.py` imports `attendance` and `student`.

## Attendance result and lifecycle

The two selection fields have different purposes:

| Field | Values | Meaning |
|---|---|---|
| `status` | Present, Absent, Late | The student's recorded attendance result |
| `state` | Draft, Confirmed, Cancelled | The lifecycle of the attendance record |

Confirming, cancelling, or resetting the record changes its lifecycle; these methods do not change its Present/Absent/Late result.

| Starting state | Action | Result |
|---|---|---|
| Draft | Confirm | Confirmed |
| Draft | Cancel | Cancelled |
| Confirmed | Cancel | Cancelled |
| Cancelled | Reset to Draft | Draft |

Other starting states are rejected by the respective action method. Each method uses `ensure_one()` and writes through the current user's ORM permissions, without `sudo()`.

Record Present and Record Absent update `status` on a Draft record and keep it in Draft. Confirm remains the explicit step that includes the record in attendance totals. The required attendance result still has no automatic default: select an initial result before saving a new Draft. The dedicated actions can then change a saved Draft's result. Teachers and Administrators can use these actions; Student calls are denied by ORM write access.

## Complete model

`models/attendance.py`:

```python
from odoo import fields, models
from odoo.exceptions import UserError


class UniversityAttendance(models.Model):
    _name = "university.attendance"
    _description = "University Attendance"
    _rec_name = "student_id"
    _order = "attendance_date desc, id desc"

    student_id = fields.Many2one(
        "university.student",
        string="Student",
        required=True,
        ondelete="restrict",
        index=True,
    )

    course_id = fields.Many2one(
        "university.course",
        string="Course",
        required=True,
        ondelete="restrict",
        index=True,
    )

    attendance_date = fields.Date(
        string="Attendance Date",
        default=fields.Date.context_today,
        required=True,
        index=True,
    )

    status = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
        ],
        string="Attendance Status",
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        string="Workflow Status",
        default="draft",
        required=True,
        copy=False,
    )

    _student_course_date_unique = models.Constraint(
        "UNIQUE(student_id, course_id, attendance_date)",
        "Attendance already exists for this student, course, and date.",
    )

    def action_confirm(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft attendance can be confirmed.")
        self.write({"state": "confirmed"})

    def action_record_present(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft attendance can be recorded as present.")
        self.write({"status": "present"})

    def action_record_absent(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft attendance can be recorded as absent.")
        self.write({"status": "absent"})

    def action_cancel(self):
        self.ensure_one()
        if self.state not in ("draft", "confirmed"):
            raise UserError(
                "Only draft or confirmed attendance can be cancelled."
            )
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state != "cancelled":
            raise UserError("Only cancelled attendance can be reset to draft.")
        self.write({"state": "draft"})
```

The SQL uniqueness constraint covers every lifecycle state. A cancelled record still reserves its student/course/date combination; resetting that record allows it to be reused. Separate dates, courses, or students can each have distinct records.

## Attendance totals and percentage

The inherited Student model displays an Attendance Summary with `total_classes`, `attended_classes`, and `attendance_percentage`.

- Total Classes counts confirmed attendance records for that student, across all courses and dates.
- Attended Classes counts confirmed Present or Late records. Late counts as attended for this lesson.
- Attendance (%) is `100 * attended_classes / total_classes`, displayed to two decimal places.
- Draft and Cancelled records are excluded. No confirmed records yields zero totals and 0%, without division by zero.

For example, one confirmed Present, one confirmed Absent, and one confirmed Late record produce 3 total classes, 2 attended classes, and 66.67% attendance.

`models/student.py`:

```python
from odoo import api, fields, models


class UniversityStudent(models.Model):
    _inherit = "university.student"

    attendance_ids = fields.One2many(
        "university.attendance",
        "student_id",
        string="Attendance Records",
    )

    total_classes = fields.Integer(
        string="Total Classes",
        compute="_compute_attendance_summary",
    )

    attended_classes = fields.Integer(
        string="Attended Classes",
        compute="_compute_attendance_summary",
    )

    attendance_percentage = fields.Float(
        string="Attendance (%)",
        compute="_compute_attendance_summary",
        digits=(5, 2),
    )

    @api.depends("attendance_ids", "attendance_ids.state", "attendance_ids.status")
    @api.depends_context("uid")
    def _compute_attendance_summary(self):
        attendance = self.env["university.attendance"]
        student_ids = self.ids
        totals = dict.fromkeys(student_ids, 0)
        attended = dict.fromkeys(student_ids, 0)

        if student_ids:
            rows = attendance._read_group(
                [("student_id", "in", student_ids), ("state", "=", "confirmed")],
                ["student_id", "status"],
                ["__count"],
            )
            for student, status, count in rows:
                totals[student.id] += count
                if status in ("present", "late"):
                    attended[student.id] += count

        for student in self:
            total = totals.get(student.id, 0)
            count = attended.get(student.id, 0)
            student.total_classes = total
            student.attended_classes = count
            student.attendance_percentage = 100.0 * count / total if total else 0.0
```

The fields are non-stored computed values. Their dependencies cover record membership, lifecycle state, and attendance result, so creating, editing, cancelling, resetting, reassigning, or deleting attendance invalidates the summaries. `depends_context("uid")` separates the calculation cache by user. The grouped ORM query uses the acting user's permissions and does not use `sudo()`.

## Permissions

`security/ir.access.csv`:

```csv
id,name,model_id,group_id/id,operation,domain
access_attendance_admin,Attendance Administrator,university.attendance,university_student.group_university_admin,crud,
access_attendance_teacher,Attendance Teacher,university.attendance,university_student.group_university_teacher,cru,
access_attendance_student,Attendance Student,university.attendance,university_student.group_university_student,r,"[('student_id.user_id', '=', user.id)]"
```

| Role | Create | Read | Edit | Delete | Record scope |
|---|---|---|---|---|---|
| University Administrator | Yes | Yes | Yes | Yes | All attendance |
| University Teacher | Yes | Yes | Yes | No | All attendance |
| University Student | No | Yes | No | No | Own attendance |

The Student domain follows `student_id.user_id` to the current login. The related student must have the correct Login User assigned. The three workflow buttons are limited to the Administrator and Teacher groups; direct Student calls were also checked against server-side access rules.

## Views and menu

`views/attendance_views.xml`:

```xml
<odoo>
    <record id="view_university_attendance_list" model="ir.ui.view">
        <field name="name">university.attendance.list</field>
        <field name="model">university.attendance</field>
        <field name="arch" type="xml">
            <list string="Attendance">
                <field name="student_id"/>
                <field name="course_id"/>
                <field name="attendance_date"/>
                <field name="status"/>
                <field name="state"/>
            </list>
        </field>
    </record>

    <record id="view_university_attendance_form" model="ir.ui.view">
        <field name="name">university.attendance.form</field>
        <field name="model">university.attendance</field>
        <field name="arch" type="xml">
            <form string="Attendance">
                <header>
                    <button
                        name="action_record_present"
                        string="Record Present"
                        type="object"
                        invisible="state != 'draft'"
                        groups="university_student.group_university_admin,university_student.group_university_teacher"
                    />

                    <button
                        name="action_record_absent"
                        string="Record Absent"
                        type="object"
                        invisible="state != 'draft'"
                        groups="university_student.group_university_admin,university_student.group_university_teacher"
                    />

                    <button
                        name="action_confirm"
                        string="Confirm"
                        type="object"
                        class="oe_highlight"
                        invisible="state != 'draft'"
                        groups="university_student.group_university_admin,university_student.group_university_teacher"
                    />

                    <button
                        name="action_cancel"
                        string="Cancel"
                        type="object"
                        invisible="state not in ('draft', 'confirmed')"
                        groups="university_student.group_university_admin,university_student.group_university_teacher"
                    />

                    <button
                        name="action_reset_to_draft"
                        string="Reset to Draft"
                        type="object"
                        invisible="state != 'cancelled'"
                        groups="university_student.group_university_admin,university_student.group_university_teacher"
                    />

                    <field
                        name="state"
                        widget="statusbar"
                        statusbar_visible="draft,confirmed,cancelled"
                        readonly="True"
                    />
                </header>

                <sheet>
                    <group>
                        <group string="Student and Course">
                            <field
                                name="student_id"
                                options="{'no_create': True}"
                            />
                            <field
                                name="course_id"
                                options="{'no_create': True}"
                            />
                        </group>

                        <group string="Attendance Information">
                            <field name="attendance_date"/>
                            <field name="status"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_university_attendance"
            model="ir.actions.act_window">
        <field name="name">Attendance</field>
        <field name="res_model">university.attendance</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem
        id="menu_university_attendance"
        name="Attendance"
        parent="university_student.menu_university"
        action="action_university_attendance"
        sequence="60"
    />
</odoo>
```

The list shows student, course, attendance date, attendance result, and lifecycle status. The form separates student/course selection from attendance information. Its object buttons call the model methods, and `invisible` expressions select the buttons appropriate to each lifecycle state.

The Attendance action opens `university.attendance` in list/form modes. Its menu sits under `university_student.menu_university` with sequence 60. Student/course selectors use `no_create` to select existing records from this form.

`views/student_views.xml` adds the summary to the existing Student form:

```xml
<odoo>
    <record id="view_university_student_form_attendance" model="ir.ui.view">
        <field name="name">university.student.form.attendance</field>
        <field name="model">university.student</field>
        <field name="inherit_id" ref="university_student.view_university_student_form"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet" position="inside">
                <group string="Attendance Summary">
                    <field name="total_classes"/>
                    <field name="attended_classes"/>
                    <field name="attendance_percentage"/>
                </group>
            </xpath>
        </field>
    </record>
</odoo>
```

## Manifest

`__manifest__.py`:

```python
{
    "name": "University Attendance Management",
    "version": "1.1.0",
    "summary": "Manage student attendance and its workflow",
    "category": "Education",
    "depends": ["university_student", "university_course"],
    "data": [
        "security/ir.access.csv",
        "views/attendance_views.xml",
        "views/student_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

Student and Course are explicit dependencies. The access CSV loads before the views. Because `application` is False, a manual Apps search must remove the default Apps filter to find this addon.

## Automated verification - 93 passing checks

Created an isolated database from `template0` with both Windows PostgreSQL locales set to `C`. Installed Attendance and its dependencies with HTTP and cron workers disabled, then ran an Odoo-shell verification script against the real ORM using separate Administrator, Teacher, and Student accounts.

| Check group | Passed |
|---|---:|
| Draft/date defaults and no automatic attendance result | 3 |
| Administrator and Teacher: all three actions from all three starting states | 18 |
| Student: all three workflow actions rejected from valid starting states | 3 |
| Teacher can save Present, Absent, and Late results | 3 |
| Duplicate rejection and distinct date/course/student combinations | 4 |
| Student own/foreign reads, search isolation, and denied create/edit/delete | 6 |
| Teacher delete denied and Administrator delete allowed | 2 |
| Empty and multiple-record action calls rejected | 6 |
| Attendance result required | 1 |
| Stored form, status bar, role-specific compiled forms, and menu/action link | 6 |
| **Regression subtotal** | **52** |

Expected duplicate and missing-required-field failures were checked in savepoints; these expected failures are not installation failures. Invalid transitions were checked for `UserError` and unchanged state. Student action/write failures were checked for `AccessError`. Empty and multiple-record calls were checked for singleton rejection.

The updated regression checks verify all five stored Attendance buttons and the compiled forms for each role. The additional check set passed 41 checks covering:

- Administrator and Teacher result actions from Draft, Confirmed, and Cancelled states, including unchanged lifecycle on a successful result action.
- Student denial and singleton validation for both new result actions.
- Empty/unsaved students, Draft exclusion, all-cancelled records, and an Absent-only case.
- 100%, 50%, and 66.67% examples, including Late and multiple courses.
- Summary updates after creation, result edits, cancellation, reset/reconfirmation, reassignment, and deletion.
- Batch calculation, Teacher and Student reads, user-context cache separation, and summary fields in each role's Student form.

The verification transactions were rolled back, and the temporary test database was removed after verification. The 52 regression checks plus 41 additional checks total 93 Attendance checks; they are separate from the 26 Enrollment workflow checks in Day 12.

## Installation and runtime evidence

After the isolated checks passed:

1. Identified the existing Odoo listener and verified its command line before stopping it.
2. Installed `university_attendance` into the learning database `odoo20dev` using the existing configuration, with `--stop-after-init --no-http`.
3. Verified `Module university_attendance loaded` and `Modules loaded.` in the installation log, with no ERROR, CRITICAL, or traceback entries.
4. Restarted Odoo and verified one intended listener on port 8069.
5. Requested `/web/login?db=odoo20dev` and received HTTP 200.
6. Verified the server log's module-load marker and a clear actionable-error scan at that check.
7. Ran a read-only live ORM check confirming the installed module, three lifecycle methods, three original stored form buttons, and the Attendance menu/action link.

After adding the result actions and summaries, upgraded the same addon to version 1.1.0 in `odoo20dev`. Repeated module-load, single-listener, HTTP 200, and actionable-error checks. A read-only live check verified all five action methods/buttons and the Student summary fields and inherited view.

The live ORM check reported zero attendance records immediately after installation. The user subsequently created records during the manual exercises; that initial count is not a current record-count claim.

The initial local evidence folder is `artifacts/day13-20261031` in the Mashrafi project workspace. Final completion evidence is in `artifacts/day13-complete-20261101`, including the 52-check regression report, 41-check completion report, upgrade log, live ORM results, and server-health result. Runtime logs and test databases are not included in this documentation commit.

## Manual interface evidence

| Exercise | Evidence |
|---|---|
| Saved attendance | Supplied screenshot shows a saved row with attendance result Present and workflow status Confirmed. The image does not independently establish the acting account. |
| Confirmed -> Cancelled | User confirmed the requested cancellation and appearance of Reset to Draft. |
| Cancelled -> Draft | User confirmed the reset exercise, including retaining the Present attendance result. |
| Teacher role | User confirmed creating attendance, changing lifecycle status, and Delete being unavailable. |
| Student role | User confirmed own-attendance visibility, read-only records, and absence of Create, Delete, and workflow buttons. |

Role identity and the full interaction sequence are based on user confirmation. Only the saved Present/Confirmed list result was supplied as a screenshot. Manual duplicate rejection and a manual Draft -> Cancelled exercise were not separately recorded; relevant model behavior was covered by the automated checks.

The later result buttons and summary calculations were verified by automated and read-only live checks. A separate user-confirmed browser exercise of those additions was not recorded when this README was prepared.

## Limits and remaining work

- Lifecycle and result-action guards apply to their action methods. The model does not override `write()` to enforce a lifecycle matrix for every direct state write.
- Confirmed and cancelled attendance details remain editable by roles with write access. The form does not lock those fields by lifecycle state.
- A Course enrollment prerequisite is not enforced; Attendance links directly to Student and Course and does not depend on the Enrollment addon.
- The model represents at most one attendance entry per student/course/date. Multiple class sessions on one date would require a session field and a revised uniqueness constraint.

## Recorded outcome

Attendance recording, dedicated result actions, lifecycle workflow, totals and percentages, duplicate protection, role permissions, and views are implemented and verified. All 93 focused automated checks passed, the final live upgrade and server checks succeeded, and the user confirmed the described original manual exercises.

**Activity log:** Built and upgraded Attendance with student/course/date links, Present/Absent/Late results, Record Present/Absent and lifecycle actions, confirmed-record attendance totals and percentage, duplicate protection, own-attendance Student access, 93 passing checks, live verification, and the recorded manual role confirmations.

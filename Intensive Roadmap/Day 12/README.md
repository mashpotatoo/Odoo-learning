# Intensive Day 12 - Enrollment Workflow

- **Original roadmap:** Days 36-37
- **Completed:** October 31, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_enrollment`
- **Model:** `university.enrollment`
- **Status:** Complete - implementation, automated workflow checks, live upgrade, and user-confirmed interface checks

## Overview

Extended the [Day 10 Enrollment addon](../Day%2010/README.md) with Enroll, Cancel, and Reset to Draft actions. The form now shows a read-only status bar and displays the workflow buttons appropriate to the current status. Each action checks the starting status before writing the new value through the ORM.

This intensive lesson remains separate from the original Month/Week/Day lessons. It modifies the existing Enrollment addon rather than creating another addon.

## Completed objectives

- [x] Add Python methods for Enroll, Cancel, and Reset to Draft.
- [x] Reject unsupported starting statuses with `UserError`.
- [x] Require one enrollment per action with `ensure_one()`.
- [x] Add form-header buttons linked to the Python methods.
- [x] Replace the editable form status selector with a read-only status bar.
- [x] Restrict workflow-button visibility to University Administrators and Teachers.
- [x] Verify allowed transitions, invalid transitions, and Student write restrictions against the real ORM.
- [x] Upgrade the learning database and verify the running Odoo server.
- [x] Complete the requested manual Administrator and Teacher exercises through user confirmation.

## Files involved

```text
university_enrollment/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   `-- enrollment.py          # Workflow methods
|-- security/
|   `-- ir.access.csv         # Existing role permissions retained
`-- views/
    `-- enrollment_views.xml  # Header buttons and status bar
```

The manifest already loads `security/ir.access.csv` and `views/enrollment_views.xml`, so no additional data file or dependency was needed. Existing student/course relationships, enrollment date, list view, menu, and duplicate-pair constraint were retained.

## Workflow transitions

| Current status | Action | Resulting status | Buttons shown before the action |
|---|---|---|---|
| Draft | Enroll | Enrolled | Enroll, Cancel |
| Draft | Cancel | Cancelled | Enroll, Cancel |
| Enrolled | Cancel | Cancelled | Cancel |
| Cancelled | Reset to Draft | Draft | Reset to Draft |

The initial status remains Draft. Enroll rejects Enrolled and Cancelled records; Cancel rejects Cancelled records; Reset to Draft rejects Draft and Enrolled records.

## Python methods

`models/enrollment.py` imports the exception used for unsupported transitions:

```python
from odoo.exceptions import UserError
```

The following methods are defined inside `UniversityEnrollment`:

```python
def action_enroll(self):
    self.ensure_one()
    if self.state != "draft":
        raise UserError("Only a draft enrollment can be enrolled.")
    self.write({"state": "enrolled"})

def action_cancel(self):
    self.ensure_one()
    if self.state not in ("draft", "enrolled"):
        raise UserError("Only draft or enrolled records can be cancelled.")
    self.write({"state": "cancelled"})

def action_reset_to_draft(self):
    self.ensure_one()
    if self.state != "cancelled":
        raise UserError("Only a cancelled enrollment can be reset to draft.")
    self.write({"state": "draft"})
```

`ensure_one()` requires a single record. The status check runs before the write. `write()` uses the current user's ORM permissions; the methods do not use `sudo()`.

The guards above apply when these action methods are called. The model does not override `write()` to enforce a transition matrix for every direct state write. Users with write permission can still change `state` through another permitted API or interface. The read-only status bar and hidden buttons control the form interface; they do not replace server-side access permissions.

## Form header

`views/enrollment_views.xml` adds this header immediately inside the enrollment form:

```xml
<header>
    <button
        name="action_enroll"
        string="Enroll"
        type="object"
        class="oe_highlight"
        invisible="state != 'draft'"
        groups="university_student.group_university_admin,university_student.group_university_teacher"
    />

    <button
        name="action_cancel"
        string="Cancel"
        type="object"
        invisible="state not in ('draft', 'enrolled')"
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
        statusbar_visible="draft,enrolled,cancelled"
        readonly="True"
    />
</header>
```

`type="object"` calls the model method named by `name`. The `invisible` expressions determine which buttons appear for each status. The comma-separated groups allow Administrators or Teachers to see the buttons. The old editable `state` field was removed from the form's Enrollment Information group; the list view still displays Status.

## Existing permissions

The access CSV was retained:

```csv
id,name,model_id,group_id/id,operation,domain
access_enrollment_admin,Enrollment Administrator,university.enrollment,university_student.group_university_admin,crud,
access_enrollment_teacher,Enrollment Teacher,university.enrollment,university_student.group_university_teacher,cru,
access_enrollment_student,Enrollment Student,university.enrollment,university_student.group_university_student,r,"[('student_id.user_id', '=', user.id)]"
```

Administrators have create/read/update/delete access. Teachers have create/read/update access. Students have read access to enrollments linked through `student_id.user_id` to their own login. Student calls to each workflow action were tested in a valid starting status and rejected by the ORM's write-access checks.

## Automated verification

The saved Python files passed syntax parsing, the XML passed parsing, each object button matched a model method, and the manifest's data files existed.

A temporary copy of `odoo20dev` was created as `day12_workflow_20261031_225621`. Enrollment was upgraded in that copy with HTTP and cron workers disabled. An Odoo-shell verification script then exercised the real ORM using separate test Administrator, Teacher, and Student users.

| Check group | Passed |
|---|---:|
| New enrollment defaults to Draft | 1 |
| Administrator: all three actions from all three starting statuses | 9 |
| Teacher: all three actions from all three starting statuses | 9 |
| Student: each action denied from a valid starting status | 3 |
| Empty recordset: each action rejected | 3 |
| Stored form: method names, button groups, and read-only status bar | 1 |
| **Total** | **26** |

Allowed transitions were checked for the resulting status. Invalid action calls were checked for `UserError` and an unchanged status. Student action calls were checked for `AccessError` and an unchanged status. Empty recordsets were checked for `ValueError` from `ensure_one()`.

The verification transaction was rolled back, and the temporary database was removed after the checks. These 26 checks are specific to the Day 12 workflow; they are not an inherited test count from another addon.

## Live upgrade and server verification

After the isolated checks passed:

1. Upgraded `university_enrollment` in `odoo20dev` with `--stop-after-init --no-http`.
2. Verified `Module university_enrollment loaded` and `Modules loaded.` in the upgrade log.
3. Confirmed the upgrade log had no ERROR, CRITICAL, or traceback entries.
4. Started Odoo with the existing configuration and database.
5. Verified exactly one listener on port 8069, belonging to the intended Odoo process.
6. Requested `/web/login?db=odoo20dev` and received HTTP 200.
7. Verified module loading and a clear actionable-error scan in the server log at that check.

The local evidence folder is `artifacts/day12-20261031` in the Mashrafi project workspace. It contains `verify_workflow.py`, `validate.py`, `test-results.txt`, the test and live upgrade logs, and `live-health.json`. These local runtime artifacts are not included in this documentation commit.

## Manual interface verification

| Exercise | User-confirmed result |
|---|---|
| Administrator: Draft -> Enrolled | Status changed to Enrolled, Enroll disappeared, and Cancel remained. |
| Administrator: Enrolled -> Cancelled | Status changed to Cancelled; Reset to Draft was the available workflow button. |
| Administrator: Cancelled -> Draft | Status returned to Draft; Enroll and Cancel appeared. |
| Administrator: Draft -> Cancelled | Cancellation worked directly from Draft. |
| Teacher button visibility and a saved transition | After the role and refresh exercises were requested, the user confirmed all checks. |

These manual results are based on the user's confirmations during the lesson. No Day 12 interface screenshots were supplied. The Teacher's exact tested transition was not separately named in the confirmation. Student write restrictions were verified by the automated ORM checks; a separate Student-interface exercise was not recorded for Day 12.

## Verification limits

- Direct `write()` transition enforcement is not implemented; the action methods enforce their own starting-status rules.
- Multi-record action calls were not separately exercised; empty-recordset rejection was tested and the methods use `ensure_one()`.
- Day 10 duplicate protection and own-enrollment visibility remain configured, but their full regression exercises were not repeated in these 26 workflow checks.
- Student action rejection was tested using the Student's own enrollment; this lesson did not repeat all cross-user read checks.

## Outcome

Enrollment now has guarded action methods, status-dependent form buttons, and a read-only status bar. All 26 focused workflow checks passed, the learning database was upgraded successfully, and the user confirmed the requested Administrator and Teacher exercises.

**Activity log:** Added and verified the Enrollment workflow with Enroll, Cancel, and Reset to Draft actions, role-limited buttons, a read-only status bar, 26 passing ORM/view checks, a successful live upgrade, and user-confirmed interface exercises.

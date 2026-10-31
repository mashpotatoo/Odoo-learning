# Intensive Day 14 - Automation and Security

- **Original roadmap:** Days 40-41
- **Completed:** November 1, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_attendance`, version `1.2.0`
- **Status:** Completed at the user's request; implementation and 64 focused checks verified, with manual verification limits recorded below

## Overview

Extended the [Day 13 Attendance addon](../Day%2013/README.md) with a daily scheduled summary, an automated confirmation log, and stronger Teacher permissions. The form reflects the server rules: Teachers can edit Draft attendance, while confirmed and cancelled details are read-only. Administrators retain edit access, and Students retain read-only access to their own attendance.

The live Day 14 checklist called for one scheduled action, one automated action, improved Administrator/Teacher/Student permissions, and automation/security tests for each role. This lesson remains separate from the original Month/Week/Day documentation.

## Files involved

```text
university_attendance/
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   |-- attendance.py
|   |-- student.py
|   `-- automation.py
|-- security/
|   `-- ir.access.csv
|-- data/
|   `-- ir_cron.xml
`-- views/
    |-- attendance_views.xml
    |-- attendance_automation.xml
    `-- student_views.xml
```

`models/__init__.py` imports `attendance`, `student`, and `automation`. The event-rule XML is saved under `views/attendance_automation.xml`; the manifest registers that actual path. XML data records can load from that location even though the file describes an automation rather than a visual view.

## Scheduled action

The daily job counts yesterday's Draft, Confirmed, and Cancelled attendance records. It writes one summary to the Odoo server log and returns the counts. It sends no messages and changes no attendance records.

Yesterday is determined by `fields.Date.context_today(self)` in the scheduler user's context. A UTC scheduler user can therefore report a different calendar day than a user whose timezone is Asia/Karachi. The logged date is the date actually counted.

`data/ir_cron.xml`:

```xml
<odoo noupdate="1">
    <record id="ir_cron_daily_attendance_summary" model="ir.cron">
        <field name="name">University: Daily Attendance Summary</field>
        <field name="model_id" ref="model_university_attendance"/>
        <field name="state">code</field>
        <field name="code">model._cron_log_daily_attendance()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

The job repeats every day; no specific local execution hour was configured. `noupdate="1"` preserves the stored job settings on later module upgrades.

## Event-triggered automated action

The confirmation rule watches `state`. Its before-update domain excludes already-confirmed records, and its after-update domain selects Confirmed records. Odoo does not apply the before-update domain to record creation, so an Administrator creating attendance directly in Confirmed also triggers the rule.

`views/attendance_automation.xml`:

```xml
<odoo noupdate="1">
    <record id="automation_attendance_confirmed" model="base.automation">
        <field name="name">University: Log Attendance Confirmation</field>
        <field name="model_id" ref="model_university_attendance"/>
        <field name="trigger">on_create_or_write</field>
        <field name="trigger_field_ids"
               eval="[(6, 0, [ref('field_university_attendance__state')])]"/>
        <field name="filter_pre_domain">
            [('state', '!=', 'confirmed')]
        </field>
        <field name="filter_domain">
            [('state', '=', 'confirmed')]
        </field>
        <field name="active" eval="True"/>
    </record>

    <record id="action_log_attendance_confirmation"
            model="ir.actions.server">
        <field name="name">Log Attendance Confirmation</field>
        <field name="model_id" ref="model_university_attendance"/>
        <field name="base_automation_id"
               ref="automation_attendance_confirmed"/>
        <field name="usage">base_automation</field>
        <field name="state">code</field>
        <field name="code">records._log_attendance_confirmation()</field>
    </record>
</odoo>
```

The logging method first checks read access, then logs the confirmed record's identifiers, attendance date, and result. It does not write records or call `sudo()`. Result-only edits, cancellation, resetting to Draft, and writing Confirmed over an already-Confirmed state do not produce a new confirmation event. Resetting and confirming again does produce one new event.

Both methods are implemented in `models/automation.py`, which inherits `university.attendance`.

## Role permissions and server enforcement

| Operation | Administrator | Teacher | Student |
|---|---|---|---|
| Read attendance | All | All | Own attendance only |
| Create attendance | Any valid lifecycle state | Draft only | Denied |
| Edit attendance details | Any lifecycle state | Draft only | Denied |
| Use workflow/result actions | Subject to action state checks | Subject to action state checks | Denied |
| Write lifecycle state directly | Allowed | Denied | Denied |
| Delete attendance | Allowed | Denied | Denied |

The existing `security/ir.access.csv` still grants Administrator `crud`, Teacher `cru`, and Student `r` with the domain `[('student_id.user_id', '=', user.id)]`. The model adds the Teacher-specific restrictions without granting extra CRUD access.

### Teacher creation

The `@api.model_create_multi` override requires every Teacher-created record to start in Draft. It checks both explicit `state` values and defaults resolved through `default_get`. A forged `default_state` or a mixed create batch containing a non-Draft record is rejected.

### Teacher writes and workflow actions

`write()` rejects Teacher changes to student, course, date, or result when any affected record is Confirmed or Cancelled. It also rejects direct state writes unless an internal workflow action supplies the module's private token:

```python
_WORKFLOW_TOKEN = object()
```

The state-write guard compares object identity with `is not _WORKFLOW_TOKEN`. Workflow methods pass that exact object internally:

```python
self.with_context(
    attendance_workflow_action=_WORKFLOW_TOKEN
).write({"state": "confirmed"})
```

A caller-supplied boolean, string, or dictionary cannot reproduce that Python object identity. The earlier boolean-context design was replaced before testing and deployment. No `sudo()` is used to perform workflow writes, so ORM permissions continue to apply. University Administrators and superuser environments are exempt from the Teacher-specific restrictions.

### Matching form behavior

The non-stored `can_edit_details` Boolean uses the current user's role and record state. Its compute depends on `state` and the user context (`uid`), so role changes and state transitions use the appropriate editing rules.

The form includes the Boolean invisibly and applies this expression to Student, Course, Attendance Date, and Attendance Status:

```xml
readonly="not can_edit_details"
```

Administrators can edit those fields in every state. Teachers can edit them in Draft, and resetting attendance to Draft restores editing. Students have read-only details and no workflow/result buttons. The model enforces the restrictions independently of these visual controls.

## Manifest and dependencies

`__manifest__.py`:

```python
{
    "name": "University Attendance Management",
    "version": "1.2.0",
    "summary": "Manage student attendance and its workflow",
    "category": "Education",
    "depends": [
        "university_student",
        "university_course",
        "base_automation",
    ],
    "data": [
        "security/ir.access.csv",
        "views/attendance_views.xml",
        "views/student_views.xml",
        "data/ir_cron.xml",
        "views/attendance_automation.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

`base_automation` provides the automated-rule model and linked server-action integration. The cron XML uses the Odoo 20 fields verified against the local Odoo source.

## Automated verification - 64 passing checks

Installed the saved addon and its dependencies in an isolated PostgreSQL database created from `template0` with `LC_COLLATE=C` and `LC_CTYPE=C`. HTTP and cron workers were disabled for installation and verification.

The focused checks exercised the real ORM and Odoo automation engine using separate Administrator, Teacher, and Student users. A patched logger captured the model's logging calls to verify event counts without relying on visual button state alone.

The 64 passing checks covered:

- Teacher Draft creation and editing, result actions, and rejection of explicit/default non-Draft creation and mixed create batches.
- Rejection of direct state writes with missing, boolean, string, or dictionary workflow flags, including a combined state/detail attempt.
- Teacher Confirm, Cancel, and Reset to Draft, with form editability changing appropriately.
- Rejection of Teacher edits to every protected field in Confirmed, and edits to Cancelled attendance.
- Confirmation-rule configuration and its linked server action.
- Exactly one log on confirmation, no extra log on invalid repeats, cancellation, reset, result-only edits, or same-state writes, and one new log on reconfirmation.
- Administrator editing, creation directly in Confirmed with logging, and deletion.
- Student own-record reads, search isolation, foreign-record read rejection, denied create/delete, denied workflow/result actions, and rejection of a forged workflow flag.
- Teacher deletion rejection, duplicate attendance rejection, and continued summary calculation.
- Daily job configuration, exact yesterday counts, one log from the method, execution through its configured server action, and unchanged attendance data.
- Compiled form buttons and detail-edit modifiers for all three roles.

The verification transaction was rolled back. After success, the temporary test database was removed and the evidence files retained. These 64 Day 14 checks are a separate focused set; they are not a claim that all 93 Day 13 checks were rerun unchanged after the new Teacher restrictions.

## Live upgrade and runtime evidence

Upgraded `university_attendance` in the learning database `odoo20dev`, then restarted Odoo. The upgrade log contains `Module university_attendance loaded` and `Modules loaded.` without ERROR, CRITICAL, or traceback entries.

At the post-upgrade readiness check, the login URL returned HTTP 200, exactly one intended Odoo listener served port 8069, and the initial server error scan was clear. These are results from that check, not a claim that no later background job logged an error.

The running daily scheduler subsequently logged a summary for `2026-10-30` with zero Draft, Confirmed, and Cancelled records, and its job completed successfully. That date came from the scheduler's context; it must not be relabelled as October 31 to match the user's local calendar.

## Manual checks and verification limits

| Exercise | Evidence |
|---|---|
| Automatic Student summaries | Supplied screenshot showed 1 total class, 1 attended, and 100%. User then confirmed 2 total, 1 attended, 50% after an Absent confirmation, and a return to 1/1/100% after cancelling that Absent record. |
| Student interface | User confirmed own summary visibility, read-only attendance, and unavailable result/workflow buttons. |
| Teacher confirmed attendance | User confirmed Student, Course, Date, and Attendance Status were read-only, with Cancel available. |
| Teacher reset | User confirmed Cancel followed by Reset to Draft restored detail editing. |
| Manual confirmation logging | User reported confirming as Administrator, but the inspected live log did not contain a corresponding confirmation event or Confirm-button request. This specific manual live-event check remains unverified. |
| Scheduled action | Live log independently shows execution and successful completion of the daily summary job. |

The event-triggered rule is proven by the isolated ORM checks. The missing manual live event is recorded separately and is not presented as a confirmed live trigger.

A separate background attachment-cleanup job logged `PermissionError: [WinError 5]` while accessing an upload in the learning database's filestore. The daily attendance job still completed. No filestore permission repair was performed in this lesson.

The user requested that Day 14 be marked done. The attempted Ultima completion click failed, and computer control was subsequently stopped with Escape. No successful tracker status update was verified; this README does not claim that Ultima was updated.

## Local evidence

The local `day14-validation` folder under the Codex visualization workspace contains `checks.py`, `run.py`, `results.txt`, `install.log`, `live-upgrade.log`, `live-server.log`, and `live-health.json`. Test/runtime artifacts and database credentials are not published with this documentation.

## Outcome

Implemented the scheduled attendance summary, event-triggered confirmation log, Teacher creation/write restrictions, an internal workflow token, and matching form editability. All 64 focused checks passed, the addon was upgraded successfully, and the daily summary ran in the learning environment. Manual confirmation logging, the unrelated filestore cleanup issue, and Ultima status remain subject to the limits recorded above.

**Activity log:** Added and verified daily and event-triggered attendance automations, hardened Teacher permissions against direct API/context bypasses, matched form behavior to server rules, passed 64 focused checks, deployed the upgrade, and recorded manual role confirmations and outstanding verification limits.

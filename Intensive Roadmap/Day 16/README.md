# Intensive Day 16 - QWeb and Report Actions

- **Original roadmap:** Days 43-44
- **HTML exercise verified:** November 2, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_reports`, version `1.0.0`
- **Status:** HTML reporting verified during Day 16; PDF output subsequently verified in the Day 17 follow-up

> **November 2 follow-up:** [Day 17](../Day%2017/README.md) records the completed Windows PDF-engine setup and successful Student Summary/Profile PDF downloads. The sections below preserve the original Day 16 implementation and verification scope, including its then-pending PDF work.

## Overview

Built a separate University Reports addon with a Student Summary QWeb template and a report action bound to the Student Print menu. The HTML report displays the Student name and roll number, handles a missing roll number, and repeats for multiple selected Students.

Added a custom report provider that explicitly checks Student read access before rendering. Verified rendering, bindings, escaping, and role access with 27 focused checks, then installed the addon in the learning database and completed the manual exercises recorded below.

This lesson follows [Day 15 - ERP Review](../Day%2015/README.md) and remains separate from the original Month/Week/Day lessons. The Day 15 findings are not resolved by this reporting addon.

## Scope and lesson status

The saved intensive roadmap identifies Day 16 as QWeb and Report Actions. The live task title and running timer were visible, but the full task checklist was not inspected. The user chose to handle the Ultima task manually and requested this documentation.

This README records the completed HTML-reporting scope. It does not claim PDF generation, a full live-checklist sign-off, or an automated tracker status update.

## Addon structure

```text
university_reports/
|-- __init__.py
|-- __manifest__.py
`-- reports/
    |-- __init__.py
    |-- student_report_templates.xml
    |-- student_report_actions.xml
    `-- student_summary.py
```

The addon folder was corrected from `university-report` to `university_reports` so the technical addon name matches its external identifiers and Python package.

Root `__init__.py`:

```python
from . import reports
```

`reports/__init__.py`:

```python
from . import student_summary
```

The root initializer was initially empty for the XML-only exercise. The Python imports were added when the explicit report access check was introduced.

## QWeb template

`reports/student_report_templates.xml`:

```xml
<odoo>
    <template id="report_student_summary">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Student Summary</h2>

                        <p>
                            <strong>Student Name:</strong>
                            <span t-field="o.name"/>
                        </p>

                        <p t-if="o.roll_number">
                            <strong>Roll Number:</strong>
                            <span t-field="o.roll_number"/>
                        </p>

                        <p t-else="">
                            <strong>Roll Number:</strong>
                            Not provided
                        </p>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

| Instruction | Purpose in this report |
|---|---|
| `t-call="web.html_container"` | Includes Odoo's report HTML container. |
| `t-foreach="docs" t-as="o"` | Repeats the report body for each selected Student. |
| `t-call="web.external_layout"` | Includes the standard company report layout. |
| `t-field` | Renders a field from the current Student record. |
| `t-if` / `t-else` | Shows the roll number or the Not provided fallback. |
| `class="page"` | Creates a report section for each selected Student. |

The template uses field rendering rather than raw HTML output. The automated checks confirmed that script-like Student names and special characters in roll numbers remain text.

## Report action and Print binding

`reports/student_report_actions.xml`:

```xml
<odoo>
    <record id="action_report_student_summary"
            model="ir.actions.report">
        <field name="name">Student Summary</field>
        <field name="model">university.student</field>
        <field name="report_type">qweb-html</field>
        <field name="report_name">university_reports.report_student_summary</field>
        <field name="binding_model_id"
               ref="university_student.model_university_student"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

- `model` identifies the records being reported.
- `report_name` resolves the fully qualified QWeb template identifier.
- `binding_model_id` and `binding_type` expose Student Summary through the Student Print menu.
- `qweb-html` renders the report as HTML. This action is not configured as `qweb-pdf`.

The initial multiline `report_name` retained whitespace in the stored identifier and failed an exact-name check. It was corrected to a single-line value before deployment. The final tests verify the exact stored template name.

The action uses the Odoo 20 fields inspected in the local source. It does not use the obsolete `report_file` field.

## Explicit access check

`reports/student_summary.py`:

```python
from odoo import api, models


class StudentSummaryReport(models.AbstractModel):
    _name = "report.university_reports.report_student_summary"
    _description = "Student Summary Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        students = self.env["university.student"].browse(docids)
        students.check_access("read")
        return {
            "doc_ids": docids,
            "doc_model": "university.student",
            "docs": students,
        }
```

The report provider name follows `report.<report_name>`, allowing Odoo to obtain its rendering values through `_get_report_values`.

The first role test did not reject a Student rendering another login's record. The explicit `check_access("read")` was therefore added before passing any records to the template. It checks the acting user's model and record access without `sudo()`.

Administrators and Teachers can report on Students they can read. Student accounts can report on their own linked records. Another login's record, an unlinked Student, or a mixed own/foreign batch is rejected. No new Student CRUD permissions or access CSV were added by the report addon.

## Manifest

`__manifest__.py`:

```python
{
    "name": "University Reports",
    "version": "1.0.0",
    "summary": "Printable reports for University Management",
    "category": "Education",
    "depends": ["web", "university_student"],
    "data": [
        "reports/student_report_templates.xml",
        "reports/student_report_actions.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

`web` provides the report layouts, and `university_student` provides the model and its access rules. The template loads before the report action. Since `application` is False, a manual Apps search must remove the default Apps filter to locate this addon.

## Automated verification - 27 passing checks

Installed the addon and dependencies in a disposable PostgreSQL database created from `template0` with matching `C` collation and character-type locales. The test processes used HTTP and cron workers disabled. An Odoo-shell script exercised the actual report renderer using separate Administrator, Teacher, Student, and ordinary internal users.

| Check group | Passed |
|---|---:|
| Exact template identifier, model/type, Print binding, and QWeb view | 4 |
| Administrator, Teacher, and Student: name, roll, page, and Print binding | 12 |
| Missing roll-number fallback | 1 |
| Multi-Student pages/content and a Student's multiple own records | 3 |
| Escaped Student name and roll-number characters | 2 |
| Empty record selection | 1 |
| Rejected foreign, unlinked, mixed-batch, and no-role rendering | 4 |
| **Total** | **27** |

Expected access failures were accepted only when the exception or its cause/context chain contained `AccessError`, rather than accepting an arbitrary rendering failure as a security pass.

The final rendering and access checks all passed. The first cleanup attempt found open connections to the temporary database. After stopping the verified learning Odoo process during the planned installation restart, cleanup succeeded. Only the temporary report-test database was removed, and the test evidence was retained.

These are 27 report checks, separate from the earlier Attendance and ERP review results. They do not include PDF conversion or visual PDF inspection.

## Live installation and verification

Before restarting the learning server, verified its process, command line, and working directory against the intended Odoo checkout. Installed `university_reports` in `odoo20dev`, then started one Odoo instance explicitly targeting that database.

The installation log contained `Module university_reports loaded` and `Modules loaded.` without ERROR, CRITICAL, or traceback entries. The login URL returned HTTP 200, one listener served port 8069, and the initial server error scan was clear at that check.

A read-only live ORM check verified:

- Reports was installed.
- The action used the exact template identifier and `qweb-html` type.
- The action was bound to the Student model.
- The explicit-access report provider was registered.
- Rendering the D15-001 review Student produced HTML containing Student Summary and D15-001.

## Manual interface evidence

| Exercise | Evidence |
|---|---|
| Administrator single report | Supplied screenshot shows Student Summary with Day 15 Review Student and roll D15-001, using the standard company layout. |
| Teacher report | User confirmed rendering the same name and roll number. |
| Student report | User confirmed rendering the linked review Student and continued hiding of other users' Student records. |
| Missing roll fallback | Supplied screenshot shows Day 15 Review Student with Roll Number: Not provided. The screenshot uses the existing review Student rather than establishing creation of a separate No Roll Test record. |
| Restore and batch render | User then confirmed restoring the review Student's roll number to D15-001 and rendering separate summaries for two selected Students. |

Role identity and complete action sequences are based on the guided user confirmations. The screenshots directly establish the displayed single-record and missing-roll results. The final restored database value and the batch interface output were not independently captured in a screenshot.

## PDF status and verification limits

The first report screenshot displayed Odoo's warning that no PDF engine was found and the report would be shown in HTML. The HTML report itself rendered successfully.

No PDF engine was installed or configured during this lesson, no PDF report action was added, and no PDF output was generated or visually verified. PDF configuration and testing remain pending. The observation does not by itself establish whether every possible engine package or executable is absent; it establishes that Odoo reported an unavailable engine in that session.

The full Day 16 checklist was not read from Ultima. The user chose to handle the tracker manually, so this document does not claim the task was marked done or certify any uninspected checklist requirement.

The outstanding Day 15 Teacher-module and GPA findings remain separate follow-up work.

## Local evidence

The `day16-validation` folder under the Codex visualization workspace contains the isolated-test script and result report, installation/server logs, `live-results.txt`, and `live-health.json`. Runtime artifacts, test databases, and credentials are not published with this documentation.

## Outcome

Implemented and installed a Student Summary HTML report with QWeb field rendering, conditionals, looping, a Print-menu action, and explicit Student read-access enforcement. All 27 focused checks passed, the live report rendered successfully, and the user confirmed the described role, fallback, and batch exercises. PDF output remains pending.

**Activity log:** Built University Reports, connected a QWeb Student Summary to the Print menu, corrected the template identifier, enforced read access before rendering, passed 27 report checks, installed the addon, and verified single/multiple Student and missing-roll behavior while recording the pending PDF engine setup.

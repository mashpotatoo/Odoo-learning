# Intensive Day 18 - Result Card Report

- **Original roadmap:** Day 46
- **Verified:** November 2, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_reports`, version `1.4.0`
- **Status:** Basic Result Card PDF implemented and verified

## What I built

Added a Student Result Card to the Student Print menu, building on [Day 17's reporting addon and PDF setup](../Day%2017/README.md). The report displays Student Name, Roll Number, Department, and the Student record's existing GPA in Odoo's company layout.

The report reuses the explicit Student read-access check from Day 16. Missing roll numbers and departments have readable fallbacks, and GPA zero remains visible.

This implementation displays the stored GPA. It does not calculate GPA from course marks or implement per-course results, letter grades, or pass/fail rules.

## Files and registration

The new files are:

- `reports/student_result.py`
- `reports/student_result_template.xml`
- `reports/student_result_action.xml`

The XML filenames use singular `template` and `action`, matching the files saved during the lesson and the manifest paths. The existing Summary and Profile files remain registered.

Root `__init__.py`:

```python
from . import reports
```

`reports/__init__.py`:

```python
from . import student_summary
from . import student_profile
from . import student_result
```

## Report provider

`reports/student_result.py`:

```python
from odoo import models


class StudentResultReport(models.AbstractModel):
    _name = "report.university_reports.report_student_result"
    _inherit = "report.university_reports.report_student_summary"
    _description = "Student Result Card Report"
```

The provider's technical name is `report.` followed by the action's `report_name`. Inheriting the Summary provider reuses its `_get_report_values` method, which calls `students.check_access("read")` before returning `docs`.

No `sudo()` is introduced. Administrator and Teacher accounts can render Students they can read. Student accounts can render their own linked records; foreign, unlinked, mixed own/foreign, and no-role requests are denied.

## QWeb template

`reports/student_result_template.xml`:

```xml
<odoo>
    <template id="report_student_result">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Student Result Card</h2>

                        <p>
                            <strong>Student Name:</strong>
                            <span t-field="o.name"/>
                        </p>

                        <p>
                            <strong>Roll Number:</strong>
                            <span t-if="o.roll_number"
                                  t-field="o.roll_number"/>
                            <span t-else="">Not provided</span>
                        </p>

                        <p>
                            <strong>Department:</strong>
                            <span t-if="o.department_id"
                                  t-field="o.department_id"/>
                            <span t-else="">Not assigned</span>
                        </p>

                        <h4>Academic Result</h4>
                        <p>
                            <strong>GPA:</strong>
                            <span t-field="o.gpa"/>
                        </p>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

| Instruction | Purpose |
|---|---|
| `web.html_container` | Provides Odoo's report container. |
| `t-foreach="docs"` | Repeats the card for each selected Student. |
| `web.external_layout` | Adds the company layout, including its header and footer. |
| `div.page` | Separates each Student's report content. |
| `t-field` | Renders the Student's field values. |
| `t-if` / `t-else` | Supplies missing roll-number and department fallbacks. |

GPA is rendered directly, so a value of zero is retained. The report uses field rendering instead of raw HTML; script-like names were tested and remained escaped text.

## PDF action and Print menu

`reports/student_result_action.xml`:

```xml
<odoo>
    <record id="action_report_student_result"
            model="ir.actions.report">
        <field name="name">Student Result Card</field>
        <field name="model">university.student</field>
        <field name="report_type">qweb-pdf-wkhtmltopdf</field>
        <field name="report_name">university_reports.report_student_result</field>
        <field name="binding_model_id"
               ref="university_student.model_university_student"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

The `binding_model_id` and `binding_type` expose Student Result Card in the Student Print menu. The exact `report_name` matches the template and provider.

`qweb-pdf-wkhtmltopdf` is the engine-specific report type supplied by `base_report_wkhtmltox` in this Odoo 20 checkout. The working Windows engine configuration from Day 17 is reused.

## Manifest

```python
{
    "name": "University Reports",
    "version": "1.4.0",
    "summary": "Printable reports for University Management",
    "category": "Education",
    "depends": [
        "web",
        "university_student",
        "university_enrollment",
        "base_report_wkhtmltox",
    ],
    "data": [
        "reports/student_report_templates.xml",
        "reports/student_report_actions.xml",
        "reports/student_profile_templates.xml",
        "reports/student_profile_actions.xml",
        "reports/student_result_template.xml",
        "reports/student_result_action.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

The template loads before its action. All declared data files were checked before installation. The version was increased from 1.3.0 to 1.4.0 for the Result Card addition.

## Automated verification - 27 passing checks

Installed the addon in a disposable PostgreSQL database created from `template0` with matching `C` collation and character-type locales. The validation processes used HTTP and cron disabled, leaving the live server available during isolated testing.

| Check group | Passed |
|---|---:|
| Exact template identifier, model/PDF type, binding, and provider registration | 4 |
| Administrator, Teacher, and Student: report content, GPA, and Print visibility | 9 |
| Missing roll, missing department, and zero GPA | 3 |
| Separate batch pages and a Student's multiple own records | 2 |
| Escaped Student name | 1 |
| Foreign, unlinked, mixed-batch, and no-role access rejection | 4 |
| Existing Summary and Profile reports still render | 2 |
| PDF engine detected | 1 |
| Empty selection has no Student pages | 1 |
| **Total** | **27** |

Expected access failures counted as passes only when an `AccessError` was present in the exception chain. The temporary database was removed after all checks passed.

These are the Day 18 checks, separate from Day 17's earlier test runs. They verify the basic Result Card scope described here.

## Live deployment and PDF verification

After confirming the port-8069 listener belonged to the intended Odoo checkout and database, stopped that process, upgraded `university_reports` in `odoo20dev`, and restarted the server.

The upgrade exited successfully and logged both `Module university_reports loaded` and `Modules loaded.`. The login URL returned HTTP 200, with one listener on port 8069.

The live authenticated checks produced:

| Check | Result |
|---|---|
| Administrator: Result Card for the review Student | HTTP 200, valid single-page PDF |
| Teacher: Result Card for the review Student | HTTP 200, valid single-page PDF |
| Student: Result Card for its existing linked Student | HTTP 200, valid single-page PDF |
| Student: actual Print-menu download controller | HTTP 200, PDF attachment |

The checks validated the PDF signature, parsed its pages, and confirmed the Student name, available roll number, report headings, and stored GPA. They used existing accessible records and deleted their temporary validation sessions afterward.

The saved Administrator PDF was rendered to an image and visually inspected. It showed the Student details and GPA clearly, with the company header and a Page 1 / 1 footer.

## Manual confirmation

The user confirmed the guided interface check after deployment: refreshing Odoo, opening a Student, choosing **Print > Student Result Card**, and checking the name, roll number, department, and GPA.

That confirmation records the manual exercise. The three-role download results above come from the separate authenticated checks; the manual confirmation did not identify a specific account role.

## Scope and remaining verification

Ultima's live task title identified Day 18 as Result Card Report (Original Day 46). Its three detailed checklist items were not successfully opened. This README records the implemented and tested basic Result Card; it does not certify uninspected checklist requirements or claim a tracker status change.

The existing filestore garbage-collection PermissionError appeared in a background maintenance log and remains separate from this work. It did not prevent the verified report downloads. Earlier Day 15 review findings also remain separate follow-up work.

## Local evidence

The local `day18-validation` folder contains the test runner and results, deployment logs, `live-health.json`, authenticated download results, and the saved PDF and preview. Runtime artifacts, database contents, sessions, and credentials are not included in this documentation publication.

## Learning outcome

Learned to register a report provider, reuse model-level access checks through inheritance, match provider/template/action identifiers, load XML files in manifest order, handle missing and zero values, expose a PDF through Print, and validate role access and real PDF downloads.

**Activity log:** Added the Student Result Card provider, QWeb template, and PDF action; upgraded University Reports to 1.4.0; passed 27 isolated checks; verified live PDF generation and the Student download controller; completed the manual report check.

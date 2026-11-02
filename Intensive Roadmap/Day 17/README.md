# Intensive Day 17 - Student Profile Report

- **Original roadmap:** Day 45
- **Verified:** November 2, 2026
- **Environment:** Odoo 20, PostgreSQL, native Windows
- **Addon:** `university_reports`, version `1.3.0`
- **Status:** Student Profile HTML and PDF output verified, including enrollments

## What I built

Extended the reporting addon from [Day 16](../Day%2016/README.md) with a Student Profile report. The report combines personal details, academic details, contact and guardian details, and course enrollments. It uses Odoo's company layout and appears in the Student Print menu.

Configured a working PDF engine and enabled direct PDF output for both Student Profile and the existing Student Summary. Verified the final profile with 62 isolated checks and live PDF downloads using Administrator, Teacher, and Student accounts.

## Day 17 checklist

The live Ultima task was inspected before publication. Its three items were:

| Requirement | Implemented and verified |
|---|---|
| Create the Student Profile PDF | Direct PDF conversion and download, with visual page inspection. |
| Show student department contact and enrollment information | Four sections, including an enrollment table with Course, Code, Enrollment Date, and Status. |
| Test different students and fix missing data | Role-based rendering, multiple selected Students, missing-value fallbacks, escaping, and correct per-Student enrollment grouping. |

The checklist displayed 100%, while the task status still displayed To do when inspected. No automated change to the task status is claimed here.

## Report content

| Section | Fields |
|---|---|
| Personal Information | Student Name, Roll Number, Date of Birth, Age |
| Academic Information | Department, GPA, Student Status |
| Contact and Guardian Information | Email, Phone, Guardian Name, Guardian Phone |
| Enrollment Information | Course, Course Code, Enrollment Date, Enrollment Status |

Missing roll number, birth date, and contact details display `Not provided`. A missing department displays `Not assigned`; a missing birth date makes Age display `Not available`. A valid age of zero and a GPA of zero remain visible.

Students without enrollments display `No enrollments found.` The enrollment table shows Draft, Enrolled, and Cancelled entries with their status labels, in the enrollment model's date order. A multi-Student report keeps each Student's enrollments on that Student's page.

## Addon structure

```text
university_reports/
|-- __init__.py
|-- __manifest__.py
`-- reports/
    |-- __init__.py
    |-- student_summary.py
    |-- student_report_templates.xml
    |-- student_report_actions.xml
    |-- student_profile.py
    |-- student_profile_templates.xml
    `-- student_profile_actions.xml
```

The root initializer imports the package:

```python
from . import reports
```

The reports initializer imports the two providers:

```python
from . import student_summary
from . import student_profile
```

An initial import error was caught during isolated installation. Importing the report files directly from the addon root was corrected before the live deployment.

## Report provider and access control

`reports/student_profile.py`:

```python
from odoo import api, models


class StudentProfileReport(models.AbstractModel):
    _name = "report.university_reports.report_student_profile"
    _inherit = "report.university_reports.report_student_summary"
    _description = "Student Profile Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = super()._get_report_values(docids, data=data)
        enrollments = self.env["university.enrollment"].search(
            [("student_id", "in", values["docs"].ids)]
        )
        grouped = enrollments.grouped("student_id")
        values["enrollments_by_student"] = {
            student.id: grouped.get(student, enrollments.browse())
            for student in values["docs"]
        }
        return values
```

The inherited Summary provider calls `students.check_access("read")` before returning `docs`. The profile therefore keeps the explicit read-access check introduced on Day 16.

Enrollment retrieval uses one ORM search for the selected Students, under the acting user's permissions. It does not use `sudo()`. Grouping the result supplies a separate recordset for each Student, including an empty recordset when needed.

Administrators and Teachers can report on readable Students. Student accounts can report on their own linked records; foreign, unlinked, and mixed own/foreign selections are rejected. The report adds no new business-record write permissions.

## QWeb template

`student_profile_templates.xml` calls `web.html_container`, loops over `docs`, and uses `web.external_layout` with a `div.page` for each Student. The first three sections use tables and `t-field` to render the fields listed above.

The Age condition checks whether the birth date exists, rather than testing the computed age's truthiness. This preserves a valid zero age. GPA is rendered directly for the same reason.

The final enrollment section inside each Student's page is:

```xml
<h4>Enrollment Information</h4>
<t t-set="student_enrollments"
   t-value="enrollments_by_student[o.id]"/>
<table t-if="student_enrollments"
       class="table table-sm"
       name="student_enrollments">
    <thead>
        <tr>
            <th>Course</th>
            <th>Code</th>
            <th>Enrollment Date</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr t-foreach="student_enrollments" t-as="enrollment">
            <td><span t-field="enrollment.course_id.name"/></td>
            <td><span t-field="enrollment.course_id.code"/></td>
            <td><span t-field="enrollment.enrollment_date"/></td>
            <td><span t-field="enrollment.state"/></td>
        </tr>
    </tbody>
</table>
<p t-else="">No enrollments found.</p>
```

Field rendering keeps Student, guardian, roll-number, and course values as escaped text. Script-like names and markup-like course names were included in the isolated tests.

## Report action

`reports/student_profile_actions.xml`:

```xml
<odoo>
    <record id="action_report_student_profile"
            model="ir.actions.report">
        <field name="name">Student Profile</field>
        <field name="model">university.student</field>
        <field name="report_type">qweb-pdf-wkhtmltopdf</field>
        <field name="report_name">university_reports.report_student_profile</field>
        <field name="binding_model_id"
               ref="university_student.model_university_student"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

The exact report type is supported by the `base_report_wkhtmltox` addon in this Odoo 20 checkout. The Summary action was also changed from `qweb-html` to `qweb-pdf-wkhtmltopdf`. Both Print bindings remain available, and HTML preview rendering still works.

## Manifest

```python
{
    "name": "University Reports",
    "version": "1.3.0",
    "summary": "Printable reports for University Management",
    "category": "Education",
    "depends": ["web", "university_student", "university_enrollment", "base_report_wkhtmltox"],
    "data": [
        "reports/student_report_templates.xml",
        "reports/student_report_actions.xml",
        "reports/student_profile_templates.xml",
        "reports/student_profile_actions.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

The enrollment dependency supplies Enrollment and Course models and their role access declarations. The PDF-engine dependency registers the engine-specific report type. Templates load before their actions.

## Fixing PDF generation on Windows

The initial report displayed Odoo's warning that the PDF engine could not be found. HTML rendering worked, but direct PDF output was unavailable.

Installed the official portable Windows 64-bit wkhtmltopdf 0.12.6 build with patched Qt from the [wkhtmltopdf downloads page](https://wkhtmltopdf.org/downloads.html). The executable's `--version` output and Odoo's engine-state check were verified.

Set its binary directory inside the configuration's `[options]` section:

```ini
[options]
bin_path = C:\path\to\wkhtmltox\bin
```

Use the actual installed directory. An initial placement below the logging section was caught by the engine-detection check and corrected; a `bin_path` entry in the wrong section is ignored.

After isolated validation, stopped the verified learning Odoo process, upgraded `university_reports` in `odoo20dev`, and restarted one server with the same configuration. A representative upgrade command, run from the Odoo checkout after stopping its server, is:

```powershell
& .\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf -d odoo20dev -u university_reports --no-http --max-cron-threads=0 --stop-after-init
```

The executable and private configuration are local runtime dependencies; this documentation publication does not include them or any credentials.

## Automated verification

The final addon was installed in a disposable PostgreSQL database created from `template0` with matching `C` locales. HTTP and cron were disabled for isolated checks.

| Final check group | Passed |
|---|---:|
| Profile metadata, four-section rendering across three roles, missing values, zero values, batches, escaping, rejected access, and Summary regression | 44 |
| PDF-engine detection and Summary PDF action type | 2 |
| Enrollment content, dates/status, escaping, exclusion of foreign data, empty state, and batch/provider grouping | 16 |
| **Final total** | **62** |

The original three-section HTML implementation passed 44 checks. The PDF follow-up passed 46 checks. These were superseded by the final 62-check run; the counts overlap and must not be added together. The final disposable database was removed after success.

## Live and manual verification

- Initial screenshots confirmed the first three sections, missing-value fallbacks, Age 21, GPA 3.5, and Confirmed status.
- A later screenshot confirmed the restored D15-001 roll number and the supplied test contact/guardian values. The displayed birth date was January 20, 2005.
- The user confirmed Teacher and Student manual report exercises. Screenshots alone do not prove the acting user's role.
- During the PDF fix, both Summary and Profile returned valid single-page PDF files for Administrator, Teacher, and Student. The actual Student Print-menu download controller also returned a PDF attachment: seven successful live requests.
- After adding enrollments, the final Profile PDF was checked again for all three roles, including the Student download controller and visual page inspection. The Student check used its existing linked record; the review Student was not linked to a login at that inspection. No business records were changed for these live checks.
- The final deployment log recorded the module upgrade, the login URL returned HTTP 200, and one Odoo listener served port 8069.

The final profile adds a fourth section beyond the user's earlier three-section screenshots. Enrollment grouping, dates/status, empty behavior, and permissions are supported by the final isolated checks and live PDF verification.

## Remaining separate issues

The earlier Day 15 missing Teacher business module and legacy invalid GPA finding remain separate work. An existing filestore garbage-collection `PermissionError` also remains; it did not prevent the verified PDF downloads. No claim is made that every background maintenance log is error-free.

## Local evidence and learning outcome

Local `day17-validation`, `pdf-fix`, and `day17-final` evidence folders contain the test scripts/results, upgrade/server logs, live download results, and PDF previews. Runtime artifacts and database contents are not included in this documentation commit.

Learned how to reuse a report provider through model inheritance, enforce record access before rendering, group related records for multi-document reports, handle missing fields, bind reports to Print, configure a native Windows PDF engine, and verify real downloads and page layout.

**Activity log:** Built and verified the Student Profile report, completed its enrollment section against the live checklist, enabled direct PDF output for both student reports, passed 62 final isolated checks, and verified role-based PDF downloads.

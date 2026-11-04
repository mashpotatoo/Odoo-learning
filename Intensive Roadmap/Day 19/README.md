# Intensive Day 19 - Report Design and Extra Report

- **Original roadmap:** Days 47-49
- **Verified:** November 4, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_reports`, version `1.5.0`
- **Installed version:** `20.0.1.5.0`
- **Status:** Report implementation and PDF verification complete; manual interface and tracker sign-off pending

## What I built

Added an **Enrollment Register** to the Enrollment Print menu and applied shared formatting to all four university reports: Student Summary, Student Profile, Student Result Card, and Enrollment Register. This builds on [Day 18's Result Card](../Day%2018/README.md) and [Day 17's working PDF setup](../Day%2017/README.md).

The extra report uses the existing Enrollment model. It includes only the selected records, ordered by enrollment date and then record ID. Its totals count selected Draft, Enrolled, and Cancelled enrollments; they are not institution-wide totals or attendance figures.

| Column | Content |
|---|---|
| Student / Roll Number | Student name and roll number, with a missing-roll fallback |
| Course / Code | Course name and course code |
| Enrollment Date | Date formatted by Odoo |
| Status | Draft, Enrolled, or Cancelled |

The configured company logo, header, footer, and page numbering are preserved through Odoo's external layout. The work reuses that branding rather than replacing the company's settings.

## Print the new report

1. Refresh Odoo after the module upgrade.
2. Open **University Management > Enrollments**.
3. Open one enrollment, or select multiple accessible records in the list.
4. Choose **Print > Enrollment Register**.
5. Review the selected rows, state totals, company branding, and page numbering.

Student Summary, Profile, and Result Card remain available from the Student Print menu. A batch of two Students produces separate pages for the two records.

## Files and registration

New report files:

- `reports/enrollment_report.py`
- `reports/enrollment_report_templates.xml`
- `reports/enrollment_report_actions.xml`
- `reports/report_layout.xml`

Updated the report package imports, manifest, existing Student report templates, and existing Student report actions. Each Student template now calls `university_reports.external_layout` and uses `class="page university-report"`; each action references `paperformat_university`.

The following code blocks reproduce the implemented files. They document the addon source; this learning-repository update publishes Markdown only.

## Enrollment report provider

`reports/enrollment_report.py`:

```python
from odoo import api, models


class EnrollmentRegisterReport(models.AbstractModel):
    _name = "report.university_reports.report_enrollment_register"
    _description = "University Enrollment Register"

    @api.model
    def _get_report_values(self, docids, data=None):
        enrollments = self.env["university.enrollment"].browse(docids)
        enrollments.check_access("read")
        enrollments.student_id.check_access("read")
        enrollments.course_id.check_access("read")
        enrollments = enrollments.sorted(
            key=lambda enrollment: (enrollment.enrollment_date, enrollment.id)
        )
        return {
            "doc_ids": enrollments.ids,
            "doc_model": "university.enrollment",
            "docs": enrollments,
            "state_counts": {
                state: len(enrollments.filtered(lambda row: row.state == state))
                for state in ("draft", "enrolled", "cancelled")
            },
        }
```

The provider checks read access on the selected enrollments and their related Student and Course records before returning report values. It supplies `doc_ids`, `doc_model`, and `docs`, plus the totals used by the template.

There is no access elevation in the provider. Existing university roles and own-record restrictions apply:

| Role | Report access |
|---|---|
| University Administrator | Accessible university records under the existing role |
| University Teacher | Accessible university records under the existing role |
| University Student | Own linked records only |
| No university role | Denied |

A Student request containing a foreign record is rejected, including a mixed own/foreign selection. Unlinked records are also denied to a Student. Existing Student report providers retain their read-access checks.

## Enrollment QWeb template

`reports/enrollment_report_templates.xml`:

```xml
<odoo>
    <template id="report_enrollment_register">
        <t t-call="web.html_container">
            <t t-call="university_reports.external_layout">
                <div class="page university-report">
                    <h2>Enrollment Register</h2>
                    <p class="report-note">Selected enrollment records, ordered by enrollment date.</p>
                    <table class="table table-sm" name="enrollment_totals">
                        <tbody>
                            <tr>
                                <th>Total</th><th>Draft</th><th>Enrolled</th><th>Cancelled</th>
                            </tr>
                            <tr>
                                <td><span t-out="len(docs)"/></td>
                                <td><span t-out="state_counts['draft']"/></td>
                                <td><span t-out="state_counts['enrolled']"/></td>
                                <td><span t-out="state_counts['cancelled']"/></td>
                            </tr>
                        </tbody>
                    </table>
                    <h4>Enrollment Details</h4>
                    <table t-if="docs" class="table table-sm" name="enrollment_register">
                        <thead>
                            <tr>
                                <th style="width: 23%">Student / Roll Number</th>
                                <th style="width: 36%">Course / Code</th>
                                <th style="width: 23%">Enrollment Date</th>
                                <th style="width: 18%">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr t-foreach="docs" t-as="enrollment">
                                <td>
                                    <span t-field="enrollment.student_id.name"/><br/>
                                    <span class="report-note" t-if="enrollment.student_id.roll_number"
                                          t-field="enrollment.student_id.roll_number"/>
                                    <span class="report-note" t-else="">Roll number not provided</span>
                                </td>
                                <td>
                                    <span t-field="enrollment.course_id.name"/><br/>
                                    <span class="report-note" t-field="enrollment.course_id.code"/>
                                </td>
                                <td><span t-field="enrollment.enrollment_date"/></td>
                                <td><span t-field="enrollment.state"/></td>
                            </tr>
                        </tbody>
                    </table>
                    <p t-else="">No enrollments selected.</p>
                </div>
            </t>
        </t>
    </template>
</odoo>
```

`t-field` renders field values using Odoo's formatting and escaping. `t-out` renders the computed counts. The empty-selection message and missing-roll fallback are explicit. The detail table uses a real `<thead>` so its column headings can repeat on continuation pages.

## PDF action and Print binding

`reports/enrollment_report_actions.xml`:

```xml
<odoo>
    <record id="action_report_enrollment_register" model="ir.actions.report">
        <field name="name">Enrollment Register</field>
        <field name="model">university.enrollment</field>
        <field name="report_type">qweb-pdf-wkhtmltopdf</field>
        <field name="report_name">university_reports.report_enrollment_register</field>
        <field name="binding_model_id" ref="university_enrollment.model_university_enrollment"/>
        <field name="binding_type">report</field>
        <field name="paperformat_id" ref="paperformat_university"/>
        <field name="print_report_name">'Enrollment Register'</field>
    </record>
</odoo>
```

The binding exposes the action for `university.enrollment`. The action's `report_name` matches both the QWeb template and the provider name after the `report.` prefix.

This Odoo 20 checkout uses the `qweb-pdf-wkhtmltopdf` engine-specific report type supplied by `base_report_wkhtmltox`, with the existing native Windows wkhtmltopdf installation.

## Shared report design and the layout fix

`reports/report_layout.xml`:

```xml
<odoo>
    <template id="external_layout">
        <t t-call="web.external_layout">
            <style>
                .university-report { font-size: 12px; line-height: 1.45; color: #243247; }
                .university-report h2 { font-size: 24px; color: #203c5a;
                    border-bottom: 2px solid #203c5a; padding-bottom: 10px; margin-bottom: 20px; }
                .university-report h4 { font-size: 15px; color: #203c5a;
                    margin-top: 20px; margin-bottom: 8px; page-break-after: avoid; }
                .university-report table { width: 100%; table-layout: fixed; border-collapse: collapse; }
                .university-report thead { display: table-header-group; }
                .university-report tfoot { display: table-row-group; }
                .university-report tr { page-break-inside: avoid; }
                .university-report th, .university-report td { padding: 7px 8px;
                    vertical-align: top; word-wrap: break-word; overflow-wrap: break-word;
                    border-bottom: 1px solid #dce3ea; }
                .university-report th { background-color: #edf2f7; font-weight: 600; }
                .university-report p { word-wrap: break-word; overflow-wrap: break-word; }
                .university-report .report-note { color: #5a6878; font-size: 11px; }
            </style>
            <t t-out="0"/>
        </t>
    </template>

    <record id="paperformat_university" model="report.paperformat">
        <field name="name">University A4</field>
        <field name="format">A4</field>
        <field name="orientation">Portrait</field>
        <field name="margin_top">40</field>
        <field name="margin_bottom">25</field>
        <field name="margin_left">15</field>
        <field name="margin_right">15</field>
        <field name="header_spacing">35</field>
        <field name="dpi">96</field>
    </record>
</odoo>
```

The wrapper calls `web.external_layout`, retaining company branding while sharing body styles. It standardizes headings, table width, cell padding, text wrapping, repeated column headings, and row page-break behavior.

The first rendered long-table review revealed that continuation-page headings overlapped the company logo. The final paper format corrected the header spacing and reserved footer space. All affected PDFs were regenerated and reviewed after that change.

| Final setting | Value |
|---|---|
| Paper size / orientation | A4 / Portrait |
| Top margin | 40 mm |
| Bottom margin | 25 mm |
| Left / right margins | 15 mm / 15 mm |
| Header spacing | 35 mm |
| Resolution | 96 DPI |

The layout keeps ordinary table rows together and avoids separating section headings from their following content. These behaviors were checked with the test data described below; arbitrarily tall rows or future company-layout changes may need another PDF review.

## Package imports and manifest

`reports/__init__.py`:

```python
from . import student_summary
from . import student_profile
from . import student_result
from . import enrollment_report
```

`__manifest__.py`:

```python
{
    "name": "University Reports",
    "version": "1.5.0",
    "summary": "Printable reports for University Management",
    "category": "Education",
    "depends": [
        "web",
        "university_student",
        "university_enrollment",
        "base_report_wkhtmltox",
    ],
    "data": [
        "reports/report_layout.xml",
        "reports/student_report_templates.xml",
        "reports/student_report_actions.xml",
        "reports/student_profile_templates.xml",
        "reports/student_profile_actions.xml",
        "reports/student_result_template.xml",
        "reports/student_result_action.xml",
        "reports/enrollment_report_templates.xml",
        "reports/enrollment_report_actions.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

The shared layout loads first. Each report template loads before its action. The existing Student Summary, Profile, and Result Card registrations remain in the manifest.

## Automated verification - 42 passing checks

Used a disposable copy of the development database, with a separate data directory and a local test server for the actual PDF engine's assets. Upgrade and verification shell processes used HTTP and cron disabled. Synthetic users, students, courses, and enrollments were rolled back.

| Check group | Passed |
|---|---:|
| Enrollment action, model/engine binding, and A4 format | 2 |
| Three roles: own enrollment content, Print binding, and selected totals | 9 |
| Student foreign/unlinked/mixed denial and no-role denial | 4 |
| Empty selection, missing roll, and escaped names | 3 |
| Three existing Student reports: role rendering, foreign denial, valid PDF, and missing fields | 18 |
| Enrollment PDF and Student-account PDF generation | 2 |
| Long-table totals, every row in HTML, and both long PDF outputs | 4 |
| **Total** | **42** |

Expected denial cases passed only when an `AccessError` was found in the exception chain. Python syntax, XML syntax, and every manifest data path were also checked. These checks are separate from the earlier Days 16-18 test counts.

## PDF parsing and visual review

Generated and parsed **12 PDF variants**, rendered **22 pages** to images, and visually reviewed the final output after the spacing correction.

| PDF case | Variants | Pages |
|---|---:|---:|
| Enrollment Register: single record and 73-record table | 2 | 6 |
| Student Profile: standard, missing fields, two-student batch, and long enrollment table | 4 | 8 |
| Student Result Card: standard, missing fields, and two-student batch | 3 | 4 |
| Student Summary: standard, missing fields, and two-student batch | 3 | 4 |
| **Total** | **12** | **22** |

The long Enrollment Register spanned five pages. All 70 synthetic course codes were found in the parsed PDF, and its table headings repeated on every page. The long Student Profile spanned four pages and retained its final course entry. Each two-student batch remained two pages. The missing-value Result Card retained GPA zero.

The final page images showed the company logo clear of the table headings, readable wrapped content, complete rows, footer separation, and page numbering.

## Live upgrade and downloads

Upgraded `university_reports` in the main development database. The upgrade exited successfully and logged both `Module university_reports loaded` and `Modules loaded.`. Odoo recorded the installed version as `20.0.1.5.0`.

The login page returned HTTP 200 with one verified Odoo listener on port 8069.

Authenticated checks used existing accessible records and the actual `/report/download` controller used by Print downloads:

| Report | Administrator | Teacher | Student |
|---|---|---|---|
| Student Summary | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 |
| Student Profile | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 |
| Student Result Card | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 |
| Enrollment Register | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 | PDF attachment, HTTP 200 |

All **12 downloads** returned PDF content and attachment headers. The four saved Administrator PDFs were parsed, and the live Enrollment Register was rendered and visually inspected. Temporary verification sessions were deleted afterward. The two disposable test databases were removed; copied test files were retained locally.

## Verification limits and remaining items

The supplied Day 19 checklist screenshot showed the branding item checked and the extra-report and PDF-testing items open. This work implements the Enrollment option and verifies all four reports as described above.

The live Ultima task was not successfully reopened, and its checklist was not changed. Programmatic Print-binding checks and real controller downloads do not constitute a user-confirmed visual check of the Print menu. That manual interface exercise remains pending; no tracker completion is claimed.

The existing background attachment file-cleanup job still logged a `WinError 5` permission error. It did not prevent the verified report downloads. Existing unrelated manifest and optional-markdown warnings remain separate follow-up work.

The Result Card continues to display the stored GPA. This day does not add course marks, letter grades, attendance calculations, or a Teacher module.

## Local evidence

The local `artifacts/day19-validation` folder contains `checks.json`, `pdf-checks.json`, `live-download-results.json`, `live-pdf-checks.json`, `live-health.json`, the verification scripts, upgrade/server logs, saved PDFs, rendered previews, and the original-addon backup.

This publication includes only the Day 19 README and the root roadmap index update. Database copies, filestores, sessions, credentials, PDFs containing record data, and runtime logs are not published.

## Learning outcome

Learned to create an aggregate report from selected records, preserve record permissions, share QWeb styling and paper formats, retain company branding, fix a layout problem found only on continuation pages, and verify real PDF downloads across roles.

**Activity log:** Added Enrollment Register, upgraded University Reports to 1.5.0, standardized four report layouts, corrected continuation-page header overlap, passed 42 automated checks, reviewed 22 PDF pages, and verified 12 live role-based downloads. Manual interface and tracker sign-off remain pending.

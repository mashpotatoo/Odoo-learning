# Intensive Day 10 - Enrollment Module

- **Original roadmap:** Day 34
- **Completed:** October 30, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Addon:** `university_enrollment`
- **Dependencies:** `university_student` and `university_course`
- **Status:** Complete - implementation and manual interface checks

## Overview

Created a separate Enrollment addon that links existing students to existing courses. Each enrollment stores a student, a course, an enrollment date, and a status. A database constraint prevents duplicate student/course pairs, and role permissions limit students to reading their own enrollments.

This lesson builds on [Day 9 - Department and Course Modules](../Day%209/README.md). It remains separate from the original Month/Week/Day lessons.

## Completed objectives

- [x] Create the `university.enrollment` model in a separate addon.
- [x] Link students and courses through required `Many2one` fields.
- [x] Default the enrollment date to the current user's local date.
- [x] Add Draft, Enrolled, and Cancelled statuses.
- [x] Prevent duplicate student/course pairs using `models.Constraint`.
- [x] Add Enrollment list and form views and a menu under University Management.
- [x] Configure Administrator, Teacher, and Student access.
- [x] Restrict Student reads to enrollments linked to their Login User.
- [x] Install the addon and save an enrollment through the interface.
- [x] Observe duplicate rejection and complete the manual role exercises described below.

## Addon structure

The addon is located under the local Odoo checkout's `custom-addons` directory:

```text
university_enrollment/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   `-- enrollment.py
|-- security/
|   `-- ir.access.csv
`-- views/
    `-- enrollment_views.xml
```

The root `__init__.py` imports `models`:

```python
from . import models
```

`models/__init__.py` imports the enrollment model:

```python
from . import enrollment
```

## Enrollment model

`models/enrollment.py`:

```python
from odoo import fields, models


class UniversityEnrollment(models.Model):
    _name = "university.enrollment"
    _description = "University Enrollment"
    _rec_name = "student_id"
    _order = "enrollment_date desc, id desc"

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

    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )

    _student_course_unique = models.Constraint(
        "UNIQUE(student_id, course_id)",
        "This student already has an enrollment for this course.",
    )
```

### Relationships and defaults

Each enrollment connects one student to one course. Multiple enrollment records allow a student to take several courses and a course to contain several students.

`ondelete="restrict"` configures protection against deleting a student or course that still has enrollment records. This deletion behavior was not exercised during the lesson.

`fields.Date.context_today` provides a creation-time default using the user's timezone. It does not continually replace the date on existing records. `_rec_name = "student_id"` uses the student's display name for the enrollment, and the ordering shows newer enrollment dates first.

Status defaults to Draft and is selected directly in the form. The addon does not add transition buttons or rules governing transitions between statuses.

### Duplicate protection

The `UNIQUE(student_id, course_id)` constraint is enforced in the database. It allows different students in the same course and the same student in different courses, while rejecting a repeated pair.

The restriction applies to Draft, Enrolled, and Cancelled records. To reuse a cancelled student/course pair in this lesson, update the existing record's status. Supporting separate enrollments for different semesters would require a semester field and a revised uniqueness rule.

The constraint API was checked against the local Odoo source before it was added. The supplied live-interface screenshot shows this error when saving a duplicate:

> The operation cannot be completed: This student already has an enrollment for this course.

## Role permissions

Reused the existing University groups from `university_student`:

| Role | Create | Read | Edit | Delete | Record scope |
|---|---|---|---|---|---|
| University Administrator | Yes | Yes | Yes | Yes | All enrollments |
| University Teacher | Yes | Yes | Yes | No | All enrollments |
| University Student | No | Yes | No | No | Own enrollments only |

`security/ir.access.csv`:

```csv
id,name,model_id,group_id/id,operation,domain
access_enrollment_admin,Enrollment Administrator,university.enrollment,university_student.group_university_admin,crud,
access_enrollment_teacher,Enrollment Teacher,university.enrollment,university_student.group_university_teacher,cru,
access_enrollment_student,Enrollment Student,university.enrollment,university_student.group_university_student,r,"[('student_id.user_id', '=', user.id)]"
```

The file uses the Odoo 20 access format already present in the Student and Course addons. The Student domain follows `student_id` to the student's `user_id` field and compares it with the current login user. The student record must be linked to the intended Login User for that account to see its enrollment. Records linked to another user, or to a student with no Login User, do not satisfy this Student domain.

The table describes the access declarations. Manual observations are recorded separately below; direct unauthorized ORM/API attempts were not tested for this addon.

## Views and menu

`views/enrollment_views.xml` defines:

| Component | Definition |
|---|---|
| List view | `view_university_enrollment_list`; student, course, enrollment date, and status columns |
| Form view | `view_university_enrollment_form`; Student and Course and Enrollment Information groups |
| Window action | `action_university_enrollment`, targeting `university.enrollment` in `list,form` modes |
| Menu | `menu_university_enrollment`, named Enrollments, under `university_student.menu_university` with sequence 50 |

The student and course fields use `options="{'no_create': True}"`, so the dropdowns select existing records rather than creating students or courses from the enrollment form. This is an interface setting; model permissions remain in the access CSV.

The form displays the enrollment date and an editable Status selector for users with write permission. Students view the form without edit access under their configured role.

## Manifest and installation

`__manifest__.py`:

```python
{
    "name": "University Enrollment Management",
    "version": "1.0.0",
    "summary": "Manage student course enrollments",
    "category": "Education",
    "depends": ["university_student", "university_course"],
    "data": [
        "security/ir.access.csv",
        "views/enrollment_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
```

Both dependencies load before Enrollment. The manifest registers the access file before the views. During the file checks, the manifest still had an empty `data` list after the access CSV was created; it was corrected to include both data files before installation.

The installation procedure was:

1. Restart Odoo to load the Python files.
2. Enable Developer Mode and update the Apps List.
3. Remove the default Apps search filter because `application` is `False`.
4. Search for University Enrollment Management and install it separately.
5. Open University Management > Enrollments.

The user confirmed installation and saving the first enrollment. The supplied screenshots show the installed Enrollment screens and saved records.

## Verification evidence

### File checks

Before installation, the six addon files passed checks for Python and XML syntax, package imports, dependencies, manifest data entries, required student/course relationships, the uniqueness declaration, menu/action references, and role access declarations. The Student domain was checked against the intended expression.

The saved addon source was inspected again when preparing this README. File checks establish the structure and declarations; they are separate from the live exercises.

### Live screenshots and user confirmations

| Exercise | Evidence and result |
|---|---|
| Installation and first enrollment | User confirmed installation, then confirmed saving an enrollment for the student linked to the Student login, using CS1101 and status Enrolled. |
| Duplicate student/course pair | Screenshot shows the expected Validation Error rejecting a second enrollment for the same pair. |
| Teacher deletion restriction | User explicitly reported that Delete was unavailable while following the Teacher exercise. |
| Teacher create/edit exercise | After being asked to create a second student's enrollment and save Draft > Enrolled, the user supplied a list screenshot containing Ahmed Mashrafi and Test student A, both Enrolled in the same course. This shows the saved result; the image alone does not establish the acting account or the exact edit sequence. |
| Student form | Screenshot shows Ahmed Mashrafi's enrollment, status Enrolled, date Oct 30, a 1/1 counter, and read-only form fields. |
| Student list isolation | After opening the list, the user confirmed that only Ahmed's enrollment appeared and Test student A was hidden. |

The two-record list demonstrates that the same course can have different students. The duplicate-error screenshot verifies rejection of the repeated pair through the live interface. The Student form and subsequent list confirmation support the manual own-enrollment visibility check.

### Verification limits

No new automated Odoo test suite, direct unauthorized API/ORM attempts, installation-log audit, or student/course deletion-restriction test was performed for Day 10. Administrator edit/delete permissions are configured in the CSV but were not separately exercised. The Teacher screenshot records the result of the requested exercise without independently proving its account identity or each operation.

Earlier Student-addon automated test counts are not Enrollment-addon test results. The results above are the static checks, screenshots, and user confirmations obtained during this lesson.

## Outcome

Installed the Enrollment addon, linked existing students and courses, added date and status fields, prevented duplicate student/course pairs, and configured role-based access with own-enrollment visibility for Students. Manual checks showed duplicate rejection, the Teacher deletion restriction, and the Student's read-only view and restricted list.

**Activity log:** Built and installed the Enrollment addon with student/course links, date and status fields, database uniqueness, list/form views, and role permissions; checked duplicate rejection and Student visibility using screenshots and user-confirmed exercises.

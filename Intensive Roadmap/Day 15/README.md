# Intensive Day 15 - ERP Review

- **Original roadmap:** Day 42
- **Reviewed:** November 2, 2026
- **Environment:** Odoo 20 on native Windows, PostgreSQL
- **Learning database:** `odoo20dev`
- **Status:** Review documented; final sign-off pending two open findings

## Overview

Reviewed the installed University ERP through a connected Student -> Department -> Course -> Enrollment -> Attendance exercise, then checked Administrator, Teacher, and Student behavior. The user confirmed the requested interface exercises. A separate read-only source/database audit found a missing Teacher module and one older Student record with an invalid GPA.

This lesson builds on [Day 14 - Automation and Security](../Day%2014/README.md). It remains separate from the original Month/Week/Day lessons. Publishing this review records the evidence and outstanding work; it does not resolve the two findings or certify every Week 5-6 deliverable as complete.

## Live task checklist

The Day 15 task in Ultima was inspected at the start of the lesson:

| Requirement | Review result |
|---|---|
| Test all University ERP models and workflows | Exercised the available Student, Department, Course, Enrollment, and Attendance features described below; Teacher model is missing. |
| Fix functional, security, and interface problems | Recorded two open findings. No corrective source or business-data changes were made during this review. |
| Confirm the Week 5 and Week 6 deliverables, then commit | Documentation prepared for publication; full deliverable sign-off remains pending the findings. |

The task timer was already running when the lesson started. No successful task-completion update is claimed by this README.

## Dedicated review records

The user created the following data through the Administrator interface:

| Record | Review values |
|---|---|
| Student | Name `Day 15 Review Student`; roll number `D15-001`; an existing Department; GPA `3.5`; birth date January 1, 2005 |
| Course | Name `Day 15 Review Course`; code `D15-101`; the same Department; 3 credit hours |
| Enrollment | The review Student linked to `D15-101`; left Enrolled after the workflow check |
| Attendance | The review Student in `D15-101`; date selected during the November 2 exercise; Present and Confirmed |

For the Student-role check, the user was instructed to link the review Student's Login User to the existing Student test account before signing in with that account. No account credentials or login addresses are included here.

## Student model review

The user confirmed:

1. The review Student saved correctly and retained its values after refresh.
2. A January 1, 2005 birth date displayed Age 21 on the review date.
3. Changing GPA to 4.5 was rejected with the 0.0-4.0 validation message; GPA was restored to 3.5.
4. Changing the birth date to November 3, 2026 was rejected as a future date; the original birth date was restored and Age returned to 21.
5. The selected Department's Students tab showed the review Student, roll number D15-001, and GPA 3.5.

The Department tab check exercises the reverse relationship from `university.department.student_ids` to the Student's `department_id`.

## Department and Course review

The user saved D15-101 with the same Department as the review Student, then confirmed the Department's Courses tab showed that course with 3 credit hours.

Source inspection confirmed that the base Department form contains the Students tab. The Course addon inherits the Department form to add its Courses tab. These checks cover both the Student/Department and Course/Department relationships through the interface.

## Enrollment workflow and duplicates

The user created the review Enrollment and confirmed this sequence:

```text
Draft -> Enrolled -> Cancelled -> Draft -> Enrolled
```

After refresh, the Enrollment remained Enrolled. A second Enrollment for the same Student/Course pair was rejected with:

> This student already has an enrollment for this course.

The duplicate attempt was discarded. This verifies the pair restriction through the interface; the model's existing uniqueness constraint is independent of lifecycle status.

## Attendance and summary review

The user created Present attendance for the review Student/Course, saved it, and confirmed it. After refreshing the Student form, the user confirmed:

| Summary field | Expected and user-confirmed value |
|---|---:|
| Total Classes | 1 |
| Attended Classes | 1 |
| Attendance (%) | 100 |

A second record using the same Student, Course, and attendance date was attempted with result Absent. Saving was rejected, and the attempt was discarded. Changing the attendance result therefore does not bypass the student/course/date uniqueness restriction.

## Teacher-role review

The user confirmed the following while following the Teacher exercises:

| Area | User-confirmed behavior |
|---|---|
| Departments and Courses | Existing records could be opened; Create, Edit, and Delete were unavailable. |
| Student | GPA could be changed from 3.5 to 3.6 and persisted after refresh; Delete was unavailable. GPA was restored to 3.5. |
| Enrollment | Cancel -> Reset to Draft -> Enroll worked; Enrolled persisted after refresh; Delete was unavailable. |
| Confirmed Attendance | Student, Course, Date, and Attendance Status were read-only; Cancel was available; Delete was unavailable. |

The Attendance restrictions come from the server and form changes documented in Day 14. The presence of a University Teacher security group is distinct from having a Teacher business model or Teacher addon; the missing business module is recorded below.

## Student-role review

After the requested Login User mapping, the user confirmed:

- The review Student, its D15-101 Enrollment, and its Attendance were visible and read-only.
- Student, Enrollment, and Attendance records belonging to other logins or without a Login User remained hidden.
- Create, Delete, and workflow actions were unavailable for those protected records.

An account may have more than one Student record linked to it; own-record access means every matching linked record, rather than an assumed list length of one.

## Configured permissions inspected

Read the saved `security/ir.access.csv` files in Student, Course, Enrollment, and Attendance:

| Model | Administrator | Teacher | Student |
|---|---|---|---|
| Student | Create/read/edit/delete | Create/read/edit | Read own linked records |
| Department | Create/read/edit/delete | Read | Read |
| Course | Create/read/edit/delete | Read | Read |
| Enrollment | Create/read/edit/delete | Create/read/edit | Read own linked records |
| Attendance | Create/read/edit/delete | Create/read/edit, with lifecycle restrictions | Read own linked records |

The Student model domain is `[('user_id', '=', user.id)]`. Enrollment and Attendance use `[('student_id.user_id', '=', user.id)]`. Teachers do not receive delete access to Student, Enrollment, or Attendance through these declarations. Attendance additionally limits Teachers to Draft creation/detail edits and guarded lifecycle actions.

The table describes the configured access declarations. It does not claim that each possible operation was independently attempted during Day 15; the actual manual exercises are listed above.

## Read-only source and database audit

The audit inspected addon directories and model definitions, queried `ir_model` and `ir_module_module`, and checked existing GPA and birth-date data using a read-only database connection.

Registered University models:

```text
university.attendance
university.course
university.department
university.enrollment
university.student
```

Installed University addons:

```text
university_attendance
university_course
university_enrollment
university_student
university_student_custom
```

There were no existing future birth dates at the audit. There was one existing out-of-range GPA record, identified below. These findings were rechecked when preparing this README.

## Open findings

### 1. Missing Week 5 Teacher module

There is no `university_teacher` addon directory and no registered `university.teacher` model in the inspected learning environment. The earlier Teacher-module deliverable therefore cannot be signed off merely because Teacher user permissions work.

**Required follow-up:** Implement and verify the intended Teacher module and its department link, views/menu, and role permissions before confirming that Week 5's module deliverables are complete.

### 2. Older Student record has GPA 5.0

The read-only query found Student record ID 4 with GPA 5.0, outside the allowed 0.0-4.0 range. The new review record's invalid-GPA exercise was rejected correctly, so the older data finding does not establish that current validation is bypassed through the interface.

The correct value for the older record was requested but was not supplied before this documentation request. It was not changed, deleted, or assigned a guessed GPA.

**Required follow-up:** Obtain the correct GPA or explicit instructions for handling that test record, then make and verify the authorized correction.

## Verification boundaries

- Manual results are based on the user's confirmations during the guided exercises. No Day 15 screenshots were supplied, and account identity was not independently established for each operation.
- The source/database audit was read-only and independently verified the installed-model inventory and two findings.
- No new automated Day 15 suite was run. Earlier Day 13 and Day 14 check counts are not Day 15 test results.
- The Student model's own lifecycle buttons were not separately exercised in this review. The explicitly reviewed lifecycle sequences were Enrollment and Attendance confirmation.
- Administrator delete behavior, foreign-key deletion protection, and every multi-role API path were not retested during Day 15.
- Day 14's separate filestore-cleanup issue and unverified manual confirmation-log event were not repaired or newly verified here. Older log entries are not evidence of a fresh Day 15 incident.
- No addon upgrade or server restart was performed as part of this review. Existing review records were not cleaned up.

## Outcome and next work

Documented the user-confirmed validation, relationships, workflows, duplicate protection, summaries, and role checks for the installed University ERP features. Found and preserved two unresolved issues: the absent Teacher module and older invalid GPA data.

Final Week 5-6 sign-off remains pending those findings and any remaining workflow checks. This publication records the review; it does not present unfinished fixes as completed work.

**Activity log:** Reviewed Student validation and age, Department/Student/Course links, Enrollment workflow and uniqueness, Attendance summaries and uniqueness, and Teacher/Student interface restrictions; audited installed models and legacy data; documented the missing Teacher module and unchanged GPA 5.0 record for follow-up.

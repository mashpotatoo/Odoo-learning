# Intensive Day 6 - Month 1 Review

- **Completed:** October 23, 2026
- **Modules reviewed:** `university_student` and `university_student_custom`
- **Environment:** Odoo 20 on Windows
- **Status:** Complete - practical review and concept review

## Overview

Reviewed University Student Management end to end: record creation and persistence, department relationships, workflow buttons, GPA validation, role permissions, guardian fields, and the inherited Status column.

This entry follows the intensive checklist **Month 1 Review (Original Day 28)**. It is separate from the original Month/Week/Day learning hierarchy and focuses on reviewing existing functionality.

## Completed objectives

- [x] Exercise the student app using a dedicated review record.
- [x] Check validation, relationships, workflow, and permissions through separate role accounts.
- [x] Review model inheritance, view inheritance, dependencies, and server-side security.

## Practical review

### 1. Create and reopen a review record

Created a temporary record using the University Administrator account:

| Field | Review value |
|---|---|
| Student Name | Month 1 Review Test |
| Roll Number | REVIEW-001 |
| Department | Computer Science |
| GPA | 3.5 |
| Guardian Name | Test Guardian |
| Guardian Phone | 03000000000 - dummy test value |
| Login User | Empty |

The record appeared in the student list with the expected roll number, department, GPA, and Status column. Reopening the record and retaining the guardian details were user-confirmed.

Login User was left empty so that the review record would not be visible to a Student account under the existing own-record access rule. The record was deleted during the Administrator cleanup check at the end of the practical review.

### 2. Workflow and saved status

Exercised Confirm, Cancel, and Reset to Draft on the review record. The supplied list screenshots showed it in Confirmed and later Draft status, supporting that the status change was saved. The user confirmed the requested Cancel and Reset to Draft steps.

The Teacher account also completed the Confirm → Cancel → Reset to Draft cycle during its permission check.

Existing methods reviewed:

```python
def action_confirm(self):
    self.write({"state": "confirmed"})

def action_cancel(self):
    self.write({"state": "cancelled"})

def action_reset_draft(self):
    self.write({"state": "draft"})
```

These methods use the normal ORM write operation and therefore remain subject to server-side write permissions.

### 3. GPA validation

Tested invalid GPA updates on the review record, then restored a valid value:

| GPA | Expected behavior | Review result |
|---|---|---|
| 4.5 | Reject the save | User-confirmed |
| -1 | Reject the save | User-confirmed |
| 3.5 | Save and remain after reopening | User-confirmed |
| 4.0 | Accept the Administrator update | User-confirmed during the final role check |

Existing constraint reviewed:

```python
@api.constrains("gpa")
def _check_gpa(self):
    for student in self:
        if not 0.0 <= student.gpa <= 4.0:
            raise ValidationError(
                "GPA must be between 0.0 and 4.0."
            )
```

The user also confirmed correcting the older **Teacher Permission Test updated** record, which had displayed GPA 5.00, to a valid test value. Its final value was not captured in a follow-up screenshot or independently queried during this review.

### 4. Student permissions

Using the separate Student account, the user confirmed:

- Only the linked student record was visible.
- Month 1 Review Test was hidden because it had no Login User.
- The student form was read-only.
- Status was visible.
- Confirm, Cancel, and Reset to Draft buttons were absent.

These checks reviewed the interface behavior of the existing access rule and role permissions.

### 5. Teacher permissions

Using the separate Teacher account, the user confirmed:

- Month 1 Review Test was visible.
- Guardian Name could be changed to **Updated Test Guardian**, saved, and retained after reopening.
- The workflow buttons changed the status successfully.
- Delete was absent from the record action menu.

### 6. Administrator permissions and department relationship

Using the University Administrator account, the user confirmed:

1. Month 1 Review Test appeared under **Departments → Computer Science → Students**.
2. Its GPA could be updated to 4.0 and saved.
3. Only the temporary Month 1 Review Test record was deleted for the deletion check.
4. The older out-of-range GPA test value was corrected.

The department check reviewed both sides of the existing relationship:

| Model field | Relationship |
|---|---|
| `university.student.department_id` | Many-to-one: a student points to one department. |
| `university.department.student_ids` | One-to-many: a department lists its linked students. |

## Concept review

### Model definition and model inheritance

`_name` defines a model, while `_inherit` supports model inheritance. This project uses the following extension pattern:

```python
class UniversityStudentExtension(models.Model):
    _inherit = "university.student"

    guardian_name = fields.Char(string="Guardian Name")
    guardian_phone = fields.Char(string="Guardian Phone")
```

With `_inherit` and no new `_name`, these guardian fields extend the existing student model and table.

### Module dependencies and view inheritance

| Concept | Reviewed meaning |
|---|---|
| `depends` in the manifest | Lists prerequisite addons that must be available and loaded first. |
| `inherit_id` in an XML view | References the parent XML view being extended. |
| `_inherit` in Python | Implements model inheritance. |
| XPath with `position="after"` | Inserts content after a targeted element in an inherited view. |

Use `inherit_id` to reference the parent view in an XML view extension, and `_inherit` for model inheritance in Python.

The existing customization addon depends on `university_student` and inserts Status after GPA in the student list. The screenshots supplied during this review showed that column in the expected position.

### Interface controls and server-side security

Hiding a button only removes it from the interface. A caller can still attempt the underlying method through API or RPC requests, so the server must enforce authorization.

The review reinforced that button visibility is an interface aid; access controls must reject unauthorized reads and writes at the server.

## Evidence and verification limits

| Evidence | What it establishes |
|---|---|
| First supplied list screenshot | Review record exists with REVIEW-001, GPA 3.50, Confirmed status, and a visible Status column. |
| Second supplied list screenshot | The review record is displayed as Draft after the reset exercise. |
| User confirmations after each procedure | Guardian persistence, GPA rejection and valid saves, Student and Teacher interface permissions, the department relationship, Administrator editing/deletion, and test-data correction. |
| User answers and feedback | Understanding of model inheritance, dependencies, view inheritance, and server-side security. |

No new automated tests, direct API/RPC permission checks, database queries, module upgrades, or server restarts were performed as part of Day 6. The review results above are based on screenshots and user-confirmed actions.

The [Day 5 README](../Day%205/README.md) records the earlier 20-test regression run and direct server-side permission checks. Those results are prior evidence, not a fresh automated test run for this lesson.

## Outstanding maintenance item

The attachment-cleanup Windows permission issue recorded in the Day 5 README was not investigated or marked resolved during this review.

## Outcome and next step

Completed the practical and conceptual Month 1 review. Continue with **Intensive Day 7 - Improve the Student Module (Original Days 29-30)**; that lesson is not marked complete here.

**Activity log:** Reviewed student record persistence, workflow, GPA validation, role permissions, department relationships, and inheritance concepts, then confirmed Administrator cleanup and the need for server-side authorization.

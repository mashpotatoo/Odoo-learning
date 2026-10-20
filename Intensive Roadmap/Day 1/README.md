# Intensive Day 1 - University User Roles

- **Completed:** October 20, 2026
- **Module:** `university_student`
- **Environment:** Odoo 20 on Windows
- **Status:** Complete - User Roles checklist

## Overview

Implemented Administrator, Teacher, and Student roles in University Student Management, configured their permissions, and created a separate account for each role. Checked student-record access through the Odoo interface using the test accounts.

This entry follows the intensive checklist titled **User Roles (Original Day 20)**. The earlier [Day 20 - Model Methods, Recordsets, and Lead Workflow](../../Month%201/Week%203/Day%206/README.md) documents a separate completed lesson in `ultima_lead`.

## Objectives

- Create Administrator, Teacher, and Student security groups.
- Define access rights for each group.
- Create one test user for each role.
- Check that available student-record operations match each role.

## Completed checklist

- [x] Create Administrator, Teacher, and Student groups.
- [x] Define access rights for each group.
- [x] Create one test user for each role.

## Permission design

| Role | Student records | Department records |
|---|---|---|
| University Administrator | Create, read, update, delete | Create, read, update, delete |
| University Teacher | Create, read, update | Read only |
| University Student | Read only | Read only |

Department permissions were configured in the access file; separate department-operation checks remain for the Security Testing lesson.

## Work completed

### 1. Defined the security groups

Added `security/groups.xml`:

```xml
<odoo>
    <record id="group_university_admin" model="res.groups">
        <field name="name">University Administrator</field>
    </record>

    <record id="group_university_teacher" model="res.groups">
        <field name="name">University Teacher</field>
    </record>

    <record id="group_university_student" model="res.groups">
        <field name="name">University Student</field>
    </record>
</odoo>
```

These custom groups define application permissions. University Administrator is separate from Odoo's general Administrator role.

### 2. Replaced the broad internal-user permissions

The previous access rows granted `crud` to `base.group_user`, giving all internal users full access. Replaced those grants with group-specific rows in `security/ir.access.csv`:

```csv
id,name,model_id,group_id/id,operation,domain
access_university_student,Student Administrator,university.student,university_student.group_university_admin,crud,
access_university_department,Department Administrator,university.department,university_student.group_university_admin,crud,
access_student_teacher,Student Teacher,university.student,university_student.group_university_teacher,cru,
access_department_teacher,Department Teacher,university.department,university_student.group_university_teacher,r,
access_student_reader,Student Reader,university.student,university_student.group_university_student,r,
access_department_reader,Department Reader,university.department,university_student.group_university_student,r,
```

Kept the first two existing record IDs so that upgrading the module updates the original broad grants.

| Operation value | Meaning |
|---|---|
| `crud` | Create, read, update, delete |
| `cru` | Create, read, update |
| `r` | Read only |

The domains are empty: this lesson defines model permissions and does not implement an own-record restriction for students.

### 3. Loaded groups before the access file

Updated the manifest data order:

```python
"data": [
    "security/groups.xml",
    "security/ir.access.csv",
    "views/student_views.xml",
    "views/department_views.xml",
],
```

### 4. Created and assigned test accounts

Created a separate account for each University role. The University Administrator test login is `admin@uni`; Teacher and Student accounts were also created. The setup instructions used the general Odoo role **User** with only the matching University group enabled.

After the access changes, University Management was missing from the main account's app menu. Assigning University Administrator to that account restored the menu, as confirmed in the interface.

## Troubleshooting

### Missing group external IDs during upgrade

The initial upgrade could not resolve the three University group IDs referenced by the CSV. Checked that the XML IDs matched and that the manifest loaded `groups.xml` first. Restarted Odoo to reload the updated manifest; the next upgrade attempt progressed to view validation.

### Invalid student search view

The next upgrade rejected the search view's group declaration:

```xml
<group expand="0" string="Group By">
```

The installed Odoo 20 search-view schema does not accept those attributes. Changed the opening tag to `<group>`, preserving the Department grouping filter:

```xml
<group>
    <filter
        name="group_department"
        string="Department"
        context="{'group_by': 'department_id'}"
    />
</group>
```

The user confirmed the module was working after the correction and upgrade.

## Verification and results

Evidence comes from screenshots and the user's confirmations during the lesson. No automated tests or direct server-call permission checks were run for this day's work.

| Role/check | Result | Evidence |
|---|---|---|
| Student can read student records | Observed | Student list and form screenshots. |
| Student creation control | Hidden | No New button in the Student screenshots. |
| Student form editing | Appeared read-only | Fields displayed as read-only text in the form screenshot. |
| Teacher can read and create a student | Observed | New Teacher Permission Test record appeared in the list. |
| Teacher can update a student | Observed | Saved form showed Teacher Permission Test updated. |
| Teacher Delete action | Hidden | User confirmed there was no Delete option. |
| Administrator can create, update, and delete | User-confirmed | User reported completion of the Admin Permission Test procedure using `admin@uni`. |
| Main account can see University Management | User-confirmed | Menu reappeared after assigning the custom group. |

UI visibility checks do not establish that a direct server request would be denied. Student deletion denial, Teacher deletion denial at the server, department operations, and record-level isolation were not verified in this lesson.

## Next steps

Continue with **Intensive Day 2 - Security Testing**:

- Check department access for all three roles.
- Verify denied operations at the server, including direct access where appropriate.
- Review record visibility and decide whether student access should be limited to the student's own record.
- Document the results without marking untested restrictions as verified.

**Activity log:** Configured University Administrator, Teacher, and Student groups and access rights, created separate test accounts, corrected upgrade issues, and checked student-record permissions through screenshots and user-confirmed actions.

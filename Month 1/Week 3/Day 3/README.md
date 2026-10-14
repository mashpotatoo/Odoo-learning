# Day 17 — Student List View

## Overview

Configured the student list view for quick scanning: it is titled **University Students**, sorts by GPA from highest to lowest, uses a deliberate column order, and lets users hide the phone column. GPA thresholds add success or danger decoration.

## Objectives

- Use Odoo 20's `<list>` view element.
- Set a default order and arrange list columns.
- Mark a field optional and add conditional list decorations.
- Escape comparison operators in XML attribute values.

## Work completed

```xml
<record id="view_university_student_list" model="ir.ui.view">
    <field name="name">university.student.list</field>
    <field name="model">university.student</field>
    <field name="arch" type="xml">
        <list
            string="University Students"
            default_order="gpa desc"
            decoration-success="gpa &gt;= 3.8"
            decoration-danger="gpa &lt; 3.0">
            <field name="name"/>
            <field name="roll_number"/>
            <field name="department_id"/>
            <field name="gpa"/>
            <field name="email"/>
            <field name="phone" optional="hide"/>
        </list>
    </field>
</record>
```

`&gt;=` and `&lt;` are the XML-safe forms of `>=` and `<`. The phone field remains available as an optional column, hidden by default.

## Verification and status

- **Status:** Complete.
- **Tested:** Checked the list with three student records and verified the configured list presentation.
- The threshold rules are documented as configured; no specific color result for each sample record is claimed beyond the recorded test.

## Next steps

Add a search view with name and roll number search fields, GPA filters, and department grouping.

**Activity log:** Renamed and reordered the student list, added GPA sorting and row decorations, and checked it with three student records.

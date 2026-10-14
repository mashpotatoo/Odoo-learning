# Day 16 — Student Form Layout

## Overview

Created a readable student form using Odoo's form, sheet, and nested group elements. Fields were arranged into **Personal Information** and **Academic & Contact** sections.

## Objectives

- Define an `ir.ui.view` record for `university.student`.
- Use `<form>`, `<sheet>`, and nested `<group>` elements to organize fields.
- Escape the ampersand in an XML attribute value as `&amp;`.

## Work completed

```xml
<record id="view_university_student_form" model="ir.ui.view">
    <field name="name">university.student.form</field>
    <field name="model">university.student</field>
    <field name="arch" type="xml">
        <form string="Student Information">
            <sheet>
                <group>
                    <group string="Personal Information">
                        <field name="name"/>
                        <field name="roll_number"/>
                        <field name="date_of_birth"/>
                    </group>
                    <group string="Academic &amp; Contact">
                        <field name="department_id"/>
                        <field name="gpa"/>
                        <field name="email"/>
                        <field name="phone"/>
                    </group>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

In XML, a literal ampersand must be written as `&amp;`. The browser displays it as “Academic & Contact.”

## Verification and status

- **Status:** Complete.
- **Tested:** Inspected a screenshot of the student form and its grouped layout.
- This verifies the visible layout shown in the screenshot; no additional save, validation, or field behavior is claimed here.

## Next steps

Create a list view with a useful column order, GPA sorting, optional phone visibility, and conditional row decorations.

**Activity log:** Organized the student form into personal and academic/contact groups and checked the resulting layout in a screenshot.

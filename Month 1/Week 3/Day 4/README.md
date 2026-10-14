# Day 18 — Student Search and Grouping

## Overview

Added a student search view with name and roll number search fields, **High GPA** and **Low GPA** filters, and a **Group By → Department** option. The window action points to this search view.

## Objectives

- Define an Odoo search view with `<search>` and `<filter>` elements.
- Express GPA conditions as Odoo domains and escape `<` in XML.
- Use a filter context to group by `department_id`.
- Link the search view to the window action with `search_view_id`.

## Work completed

```xml
<record id="view_university_student_search" model="ir.ui.view">
    <field name="name">university.student.search</field>
    <field name="model">university.student</field>
    <field name="arch" type="xml">
        <search string="Search Students">
            <filter
                name="high_gpa"
                string="High GPA"
                domain="[('gpa', '&gt;=', 3.5)]"
            />
            <filter
                name="low_gpa"
                string="Low GPA"
                domain="[('gpa', '&lt;', 3.0)]"
            />
            <separator/>
            <group expand="0" string="Group By">
                <filter
                    name="group_department"
                    string="Department"
                    context="{'group_by': 'department_id'}"
                />
            </group>
            <field name="name"/>
            <field name="roll_number"/>
        </search>
    </field>
</record>

<record id="action_university_student" model="ir.actions.act_window">
    <field name="name">University Students</field>
    <field name="res_model">university.student</field>
    <field name="view_mode">list,form</field>
    <field name="search_view_id" ref="view_university_student_search"/>
</record>
```

The Day 15 action used `form,list` and was tested by opening the form. In the completed Day 18 configuration shown here, the action uses `list,form`, putting the list first while keeping the form available. In XML, `&gt;=` and `&lt;` preserve the intended domain operators.

## Verification and status

- **Status:** Complete.
- **Tested:** Verified the search filters and department grouping in the interface; a screenshot was used for verification.
- The recorded check covers those visible search and grouping controls; no broader access-control or data-permission behavior is claimed.

## Next steps

Begin Day 19: Security and Access Rights. This work is planned for the next learning session and is not yet complete.

**Activity log:** Added GPA search filters, name and roll number search fields, and department grouping, then verified them in a screenshot.

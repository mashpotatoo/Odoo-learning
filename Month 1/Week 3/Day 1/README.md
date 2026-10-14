# Day 15 — XML Basics, Actions, and Menus

## Overview

Introduced the university student interface through Odoo XML records, a window action, and menu items. The action was renamed **University Students** and configured with `form,list` so opening the Students menu started in the form view.

## Objectives

- Recognize the `<odoo>`, `<record>`, and `<field>` structure used in data XML.
- Define a window action for the `university.student` model.
- Connect the action to a parent menu and a Students submenu.

## Work completed

The action record identifies the model, display name, and available view sequence. The menu items expose it in the backend navigation.

```xml
<odoo>
    <record id="action_university_student" model="ir.actions.act_window">
        <field name="name">University Students</field>
        <field name="res_model">university.student</field>
        <field name="view_mode">form,list</field>
    </record>

    <menuitem
        id="menu_university"
        name="University Management"
        sequence="10"
    />

    <menuitem
        id="menu_university_student"
        name="Students"
        parent="menu_university"
        action="action_university_student"
        sequence="20"
    />
</odoo>
```

Each record ID is an external identifier within the module. The child menu's `parent` and `action` values connect navigation to the parent menu and window action.

## Verification and status

- **Status:** Complete.
- **Tested:** Opened the Students menu and confirmed the student form opened.
- The test confirms the form-opening path; it does not claim that every possible view or menu behavior was tested.

## Next steps

Build a structured student form view with a sheet and grouped fields.

**Activity log:** Added the University Students window action and Students menu, then confirmed that the menu opened the form view.

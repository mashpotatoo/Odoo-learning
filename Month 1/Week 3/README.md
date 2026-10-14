# Week 3 — Odoo Views and Navigation

## Overview

Week 3 tracks the learning roadmap for Days 15–21. The completed work so far builds the university student interface from XML navigation and form layout through list presentation, search filters, and department grouping.

**One-word summary:** Views

## Objectives

- Build backend navigation with XML records, window actions, and menu items.
- Arrange student fields in a clear form view.
- Improve list scanning with ordering, optional columns, and GPA decorations.
- Search and group student records with domains and search-view filters.
- Continue with security and access rights, then complete the remaining roadmap days.

## Roadmap and status

| Day | Topic | Status | Notes |
|---|---|---|---|
| 15 | XML basics, records, actions, and menus | Complete | Students menu opened the form view. |
| 16 | Student form view | Complete | Grouped form layout checked in a screenshot. |
| 17 | Student list view | Complete | List configuration checked with three student records. |
| 18 | Search filters and department grouping | Complete | Filters and grouping verified in a screenshot. |
| 19 | Security and Access Rights | Planned | Planned for tomorrow; not yet completed. |
| 20 | Pending roadmap topic | Pending | Topic and work remain to be completed. |
| 21 | Pending roadmap topic | Pending | Topic and work remain to be completed. |

## Completed work

- **Day 15 — XML Basics, Actions, and Menus:** Created the University Students window action and Students menu; confirmed that the menu opened the student form. See [Day 15 README](Day%201/README.md).
- **Day 16 — Student Form Layout:** Organized the student form into Personal Information and Academic & Contact groups; checked the screenshot. See [Day 16 README](Day%202/README.md).
- **Day 17 — Student List View:** Configured GPA-descending order, column order, optional phone visibility, and GPA decorations; checked the list with three student records. See [Day 17 README](Day%203/README.md).
- **Day 18 — Student Search and Grouping:** Added name and roll number search fields, high/low GPA filters, and department grouping; verified the interface using a screenshot. See [Day 18 README](Day%204/README.md).

## Next steps

1. Complete Day 19 by learning and applying security groups and access rights, then record what was actually tested.
2. Confirm or follow the existing roadmap topics for Days 20 and 21; do not mark them complete before doing the work.
3. Update this roadmap as each day is completed.

## Odoo 20 notes

- Odoo 20 list views use `<list>` in view architecture.
- XML attributes must escape comparison characters such as `<` as `&lt;` and `>` as `&gt;`; literal ampersands must be written as `&amp;`.
- The recorded Day 15 action order (`form,list`) and the later Day 18 action order (`list,form`) are documented at their respective points in the learning progression.

For current reference, see the official Odoo 20 documentation for [view records](https://www.odoo.com/documentation/20.0/developer/reference/user_interface/view_records.html).

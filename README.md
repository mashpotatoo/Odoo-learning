# Odoo Software Development Journey

A 3-month hands-on learning journey focused on becoming an Odoo developer through practical projects, business automation, and real-world problem-solving.

## Learning Goals

- Strengthen Python and Object-Oriented Programming skills
- Understand Odoo architecture, ORM, and PostgreSQL
- Develop and customize Odoo modules
- Build business applications and automation workflows
- Learn debugging, testing, Git, and deployment practices

## Progress Tracker

| Month | Progress |
|---|---|
| [Month 1](./Month%201/README.md) - Python Fundamentals & Odoo Development | In progress - Weeks 1-2 completed |
| [Month 2](./Month%202/README.md) | Upcoming |
| [Month 3](./Month%203/README.md) | Upcoming |

## Month 1 - In Progress

Completed the first two weeks of the learning journey, covering Python foundations and Odoo module development. Weeks 3 and 4 are ready for upcoming work.

**Projects:**
- Sales Calculator
- Lead Manager
- OOP Sales Management System
- Ultima Lead Management - Odoo Custom Module
- University Student Management

[View Month 1 Progress](./Month%201/README.md)

## Technology Stack

- Language: Python
- ERP Framework: Odoo 20
- Database: PostgreSQL
- Development Tools: VS Code, PowerShell, Git, GitHub
- Odoo Technologies: ORM, XML Views, Models, Security, Computed Fields

## Learning Approach

Learn -> Build -> Debug -> Test -> Document -> Commit

The focus is on understanding concepts and applying them through working projects rather than only following tutorials.

## Current Status

Month 1 - Weeks 1 and 2 completed; continuing with Week 3.

## Intensive Roadmap

The intensive checklist is tracked separately from the original Month/Week/Day lessons.

| Intensive day | Topic | Status | Completed |
|---|---|---|---|
| [Day 1](./Intensive%20Roadmap/Day%201/README.md) | University User Roles | Complete | October 20, 2026 |
| [Day 5](./Intensive%20Roadmap/Day%205/README.md) | View Inheritance and Module Interaction | Complete | October 22, 2026 |
| [Day 6](./Intensive%20Roadmap/Day%206/README.md) | Month 1 Review | Complete | October 23, 2026 |
| [Day 7](./Intensive%20Roadmap/Day%207/README.md) | Improve the Student Module | Complete | October 24, 2026 |
| [Day 9](./Intensive%20Roadmap/Day%209/README.md) | Department and Course Modules (Original Days 32-33) | Complete | October 30, 2026 |
| [Day 10](./Intensive%20Roadmap/Day%2010/README.md) | Enrollment Module (Original Day 34) | Complete | October 30, 2026 |
| [Day 12](./Intensive%20Roadmap/Day%2012/README.md) | Enrollment Workflow (Original Days 36-37) | Complete | October 31, 2026 |
| [Day 13](./Intensive%20Roadmap/Day%2013/README.md) | Attendance Workflow (Original Days 38-39) | Complete | November 1, 2026 |
| [Day 14](./Intensive%20Roadmap/Day%2014/README.md) | Automation and Security (Original Days 40-41) | Complete - verification limits documented | November 1, 2026 |
| [Day 15](./Intensive%20Roadmap/Day%2015/README.md) | ERP Review (Original Day 42) | Review recorded - 2 open findings | Pending |
| [Day 16](./Intensive%20Roadmap/Day%2016/README.md) | QWeb and Report Actions (Original Days 43-44) | HTML verified; PDF verified in Day 17 follow-up | November 2, 2026 |
| [Day 17](./Intensive%20Roadmap/Day%2017/README.md) | Student Profile Report (Original Day 45) | Complete - HTML, PDF, and enrollments verified | November 2, 2026 |

Day 1 documents Administrator, Teacher, and Student groups in `university_student`, the configured permissions, separate test accounts, and the UI checks completed during the lesson. The Day 1 README also records its verification evidence and the security checks planned at that time.

Day 5 documents a separate customization addon, its dependency on `university_student`, and an inherited list view that adds Status after GPA. It includes the completed tests, deployment checks, and interface verification. Day 6 builds on this work with a Month 1 review.

Day 6 documents the completed practical and concept review, including role permissions, workflow, GPA validation, department relationships, guardian persistence, inheritance, and test-data cleanup. Its results distinguish screenshots and user confirmations from earlier automated tests.

Day 7 documents computed age, future birth-date validation, an inherited Age field, and a timezone cache bug fix. It records 27 passing tests, deployment and live permission checks, user-confirmed interface checks, and remaining maintenance items.

Day 9 documents the new Course addon, its links to the existing Department model, inherited Courses tab, menus, and role permissions. It records file checks, screenshot evidence, and user-confirmed manual role exercises, with the limits of verification stated separately.

Day 10 documents the Enrollment addon, student/course links, enrollment date and status, duplicate protection, and role permissions with own-enrollment visibility for Students. It records file checks, the duplicate-error screenshot, manual role observations, and the limits of verification.

Day 12 documents Enroll, Cancel, and Reset to Draft actions, status-dependent buttons, and a read-only status bar. It records 26 passing workflow checks, the successful live upgrade and server-health verification, user-confirmed Administrator and Teacher exercises, and the limits of action-level transition enforcement.

Day 13 documents the Attendance addon, Record Present/Absent actions, lifecycle workflow, confirmed-record attendance totals and percentage, duplicate protection, role permissions, 93 passing checks, live upgrade evidence, and the recorded manual role confirmations.

Day 14 documents the daily summary job, confirmation automation, hardened Teacher permissions, internal workflow token, matching form restrictions, 64 passing checks, and the live upgrade. It distinguishes the verified scheduled execution from the unverified manual confirmation event, and records the separate filestore cleanup issue and unconfirmed tracker update.

Day 15 records the November 2 ERP review: user-confirmed validation, relationships, Enrollment and Attendance checks, and role restrictions, plus a read-only source/database audit. Final sign-off remains pending the missing Teacher module and an older Student record with an uncorrected GPA of 5.0; no new automated test count is claimed.

Day 16 documents the Student Summary HTML report, QWeb instructions, Print binding, explicit Student read-access check, 27 passing report checks, live installation, and user-confirmed role, missing-roll, and batch exercises. Its PDF setup was completed and verified in the Day 17 follow-up; no tracker update is claimed.

Day 17 documents the Student Profile with personal, academic, contact/guardian, and enrollment sections, inherited access enforcement, missing-value handling, and working Windows PDF output for both student reports. It records 62 final isolated checks, live role-based downloads, visual PDF verification, and the inspected three-item Ultima checklist without claiming an automated tracker status change.

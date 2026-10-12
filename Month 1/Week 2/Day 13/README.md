# Day 13 — Computed Fields, Onchange & Related Fields

**Week:** 2  
**Status:** Completed

## Learning Objectives

- Create computed fields.
- Understand `@api.depends`.
- Use `@api.onchange` for form interactions.
- Create related fields using model relationships.

## 1. Computed Fields

Computed fields automatically calculate values using a Python method.

```python
total_marks = fields.Float(
    string="Total Marks",
    compute="_compute_total_marks",
    store=True
)

@api.depends("python_marks", "database_marks")
def _compute_total_marks(self):
    for student in self:
        student.total_marks = (
            student.python_marks + student.database_marks
        )
```

## 2. Average Marks

```python
average_marks = fields.Float(
    string="Average Marks",
    compute="_compute_average_marks",
    store=True
)

@api.depends("python_marks", "database_marks")
def _compute_average_marks(self):
    for student in self:
        student.average_marks = (
            student.python_marks + student.database_marks
        ) / 2
```

## 3. Percentage Calculation

Assuming the maximum total is 200 marks:

```python
percentage = fields.Float(
    string="Percentage",
    compute="_compute_percentage",
    store=True
)

@api.depends("total_marks")
def _compute_percentage(self):
    for student in self:
        student.percentage = (
            student.total_marks / 200
        ) * 100
```

## 4. Onchange

`@api.onchange` updates values interactively when fields change in an Odoo form.

```python
gpa = fields.Float(string="GPA")
performance = fields.Char(string="Performance")

@api.onchange("gpa")
def _onchange_gpa(self):
    if self.gpa >= 3.00:
        self.performance = "Good"
    else:
        self.performance = "Needs Improvement"
```

Onchange methods should not be the sole enforcement mechanism for business rules because they are not automatically executed by every programmatic create or update.

## 5. Related Fields

Related fields retrieve information through an existing relationship.

Student model:

```python
department_id = fields.Many2one(
    "university.department",
    string="Department"
)

department_code = fields.Char(
    string="Department Code",
    related="department_id.code",
    store=True
)

department_head = fields.Char(
    string="Department Head",
    related="department_id.head_name",
    store=True
)
```

Department model:

```python
class UniversityDepartment(models.Model):
    _name = "university.department"
    _description = "University Department"

    name = fields.Char(string="Department Name")
    code = fields.Char(string="Department Code")
    head_name = fields.Char(string="Department Head")
```

## Key Differences

| Feature | Purpose |
|---|---|
| `compute` | Defines a field's calculation method |
| `@api.depends` | Declares dependencies for recomputation |
| `@api.onchange` | Responds to field changes in a form |
| `related` | Retrieves a field value through a relationship |
| `store=True` | Stores computed or related values in the database |

## Outcome

- Practiced total, average, and percentage calculations.
- Implemented GPA-based form feedback.
- Practiced department-related fields.
- Corrected indentation, syntax, and model placement issues.

**Testing:** Code reviewed as learning exercises. University Student module installation and runtime testing remain pending.

**Next:** Day 14 — University Student Module Integration and Practice.
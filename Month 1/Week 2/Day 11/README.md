# Day 11 — Odoo Recordsets

**Week:** 2  
**Status:** Completed  
**Topic:** Recordsets, Iteration, `mapped()`, `filtered()`, and `sorted()`

## Learning Objectives

- Understand what an Odoo recordset is.
- Iterate through multiple records.
- Extract field values using `mapped()`.
- Filter existing recordsets using `filtered()`.
- Sort records using `sorted()`.
- Combine recordset operations.

## 1. Understanding Recordsets

A recordset is an Odoo collection containing zero, one, or multiple records of the same model.

```python
students = env["university.student"].search([])
```

## 2. Iterating Through Records

```python
for student in students:
    print(student.name, student.gpa)
```

## 3. Using mapped()

Extract specific field values from a recordset.

```python
names = students.mapped("name")
print(names)
```

## 4. Using filtered()

Select records that satisfy a Python condition.

```python
top_students = students.filtered(
    lambda student: student.gpa > 3.50
)
```

## 5. Using sorted()

Sort records by GPA from highest to lowest.

```python
sorted_students = top_students.sorted(
    key=lambda student: student.gpa,
    reverse=True
)
```

Without `reverse=True`, sorting is ascending by default.

## 6. Final Combined Exercise

**Task:** Find all students, filter by GPA, sort descending, and extract names.

```python
students = env["university.student"].search([])

top_students = students.filtered(
    lambda student: student.gpa > 3.50
)

sorted_students = top_students.sorted(
    key=lambda student: student.gpa,
    reverse=True
)

names = sorted_students.mapped("name")

print(names)
```

Expected result with the example dataset:

```text
['Karim', 'Rahim']
```

## Key Differences

| Method | Purpose |
|---|---|
| `search()` | Find records through an ORM database query |
| `for` loop | Process records individually |
| `mapped()` | Extract values from records |
| `filtered()` | Filter an existing recordset |
| `sorted()` | Sort records by a specified key |

## Practice Outcome

- Completed recordset iteration exercises.
- Practiced extracting field values.
- Practiced filtering and sorting.
- Combined four recordset techniques in one exercise.
- Corrected sorting direction and search-domain syntax.

**Testing status:** Code reviewed as learning exercises. The University Student module has not yet been installed or tested in Odoo.

**Next:** Day 12 — Model Relationships (`Many2one`, `One2many`, `Many2many`).
# Day 10 — Odoo ORM Basics

**Week:** 2  
**Status:** Completed

## What I Learned

- Odoo ORM (Object-Relational Mapping)
- Accessing models using `env`
- Creating records with `create()`
- Searching records with `search()`
- Accessing records by ID with `browse()`
- Updating records with `write()`
- Deleting records with `unlink()`

## Practical Exercises

### 1. Create a Student

```python
student = env["university.student"].create({
    "name": "Karim",
    "age": 22,
    "gpa": 3.90,
    "status": "active",
})
```

### 2. Search Students

```python
students = env["university.student"].search([
    ("gpa", ">", 3.60)
])
```

### 3. Browse a Record

```python
student = env["university.student"].browse(5)
```

### 4. Update a Record

```python
student = env["university.student"].browse(5)

student.write({
    "age": 23,
    "gpa": 3.85,
})
```

### 5. Delete a Record

```python
student = env["university.student"].browse(7)
student.unlink()
```

### 6. Search and Update Multiple Records

```python
students = env["university.student"].search([
    ("status", "=", "active")
])

students.write({
    "status": "graduated"
})
```

## Key Learnings

| Method | Purpose |
|---|---|
| `env` | Access Odoo models |
| `create()` | Create records |
| `search()` | Find records |
| `browse()` | Access records by ID |
| `write()` | Update records |
| `unlink()` | Delete records |

## Outcome

Completed ORM syntax exercises and understood basic CRUD operations.

**Testing:** Code practiced and reviewed; actual Odoo database execution is pending.

**Next:** Day 11 — Odoo Recordsets.
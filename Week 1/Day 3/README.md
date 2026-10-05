# Day 3 - OOP Sales Management System

A simple Python sales management program built as part of my Odoo development learning journey.

## What It Does

- Creates and manages product objects
- Creates a specialized Water Purifier class using inheritance
- Stores product name, price, and purifier capacity
- Calculates discounted product prices
- Creates customer lead objects
- Classifies leads based on their budget
- Displays product and lead information

## Concepts Practiced

- Classes and Objects
- Constructors with `__init__()`
- Object Attributes
- `self`
- Methods
- Inheritance
- Method Overriding
- `super()`
- Method Parameters
- `return`
- f-strings

## Class Structure

### Product

Stores:
- Product name
- Product price

Methods:
- `show_info()`

### WaterPurifier

Inherits from `Product`.

Adds:
- Capacity

Methods:
- `show_info()` - extends the parent method using `super()`
- `calculate_discount()` - calculates and returns the final price after discount

### Lead

Stores:
- Customer name
- Budget
- Interested product

Methods:
- `classify()` - classifies the lead based on budget
- `show_info()` - displays lead information and classification

## Lead Classification

- Premium Lead: BDT 40,000+
- Qualified Lead: BDT 25,000 - 39,999
- Low Budget Lead: Below BDT 25,000

## What I Learned

I learned how Object-Oriented Programming can organize related data and behavior using classes and objects.

I also learned how a child class can inherit functionality from a parent class, override existing methods, and reuse parent functionality using `super()`.

Another important lesson was the difference between `print()` and `return`. `print()` displays information, while `return` sends a value back so it can be used elsewhere in the program.

## Run

```bash
python sales_management.py
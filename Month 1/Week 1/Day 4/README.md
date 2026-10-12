# Day 4 - Developer Tools & Debugging

Day 4 of my Odoo development learning journey focused on understanding the developer tools and workflows used for Python and Odoo development.

## What I Practiced

- Git and GitHub workflow
- `git status`
- `git diff`
- Staging files with `git add`
- Creating commits and pushing to GitHub
- Understanding tracked, untracked, modified, and staged files
- Using breakpoints in VS Code
- Step Over with `F10`
- Step Into with `F11`
- Inspecting variables while a program is running
- Reading Python error messages and tracebacks
- Debugging `TypeError`, `NameError`, and `AttributeError`
- Using PowerShell for Python development
- Understanding Python virtual environments (`.venv`)
- Checking which Python interpreter is being used

## Debugging Exercise

Created `debug_practise.py` with an intentional data type error.

The product price was stored as a string:

`"35000"`

instead of an integer:

`35000`

This caused a `TypeError` during the discount calculation.

I used the VS Code debugger to:

1. Set a breakpoint
2. Step into `calculate_discount()`
3. Inspect `self.price` and `discount`
4. Read the Python traceback
5. Identify the incorrect data type
6. Fix the problem
7. Run the program again and verify the result

Final output:

Product: TriShield  
Final Price: BDT 31,500.00

## Odoo Python Environment

I also learned that my local Odoo installation uses its own Python virtual environment:

`.venv`

When the virtual environment is active, Python and installed packages are isolated from the global Windows Python installation.

## What I Learned

I learned that debugging is not about randomly changing code. The correct process is to read the error, locate the failing line, inspect the program state, understand the cause, fix it, and verify the result.

I also learned how Git tracks changes through the working directory, staging area, local repository, and remote GitHub repository.
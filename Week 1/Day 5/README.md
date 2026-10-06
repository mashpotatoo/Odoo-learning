# Day 5 - Odoo Setup & Environment

Day 5 of my Odoo development learning journey focused on understanding how my local Odoo development environment works.

## Environment

- Odoo Version: 20.0
- Operating System: Windows
- Python Environment: `.venv`
- Database: PostgreSQL
- PostgreSQL Host: `localhost`
- PostgreSQL Port: `5432`
- Odoo Web Server: `127.0.0.1:8069`

## Odoo Project Structure

I explored the main directories and files in my Odoo installation.

### `.venv/`

Contains the isolated Python environment used by my Odoo installation.

When `.venv` is active, the `python` command uses the Python interpreter inside this environment instead of the global Windows Python installation.

### `odoo/`

Contains the core Odoo Python framework.

### `addons/`

Contains standard Odoo modules.

### `custom-addons/`

This is where I will create my own custom Odoo modules.

### `odoo-bin`

The command-line entry point used to start and manage the Odoo server.

Example:

```powershell
python odoo-bin -c odoo.conf
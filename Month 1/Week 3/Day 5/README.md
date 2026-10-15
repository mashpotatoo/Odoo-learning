# Day 19 - Security and Access Rights

## Overview

Configured security groups and model access for the Ultima Lead Management module, then added a record filter so regular users can read Premium leads while managers retain access to all leads.

## Objectives

- Create separate User and Manager groups.
- Give Users read-only access and Managers full CRUD access.
- Use an Odoo 20 access domain to limit which records a group can read.
- Verify the permissions with separate Odoo accounts.

## Work completed

The Manager group implies the User group, so a Manager also inherits the baseline User membership.

```xml
<odoo>
    <record id="group_ultima_lead_user" model="res.groups">
        <field name="name">Ultima Lead User</field>
    </record>

    <record id="group_ultima_lead_manager" model="res.groups">
        <field name="name">Ultima Lead Manager</field>
        <field name="implied_ids" eval="[(4, ref('group_ultima_lead_user'))]"/>
    </record>
</odoo>
```

The access file grants Users read access to Premium leads. The Manager row grants create, read, update, and delete access without a record domain.

```csv
id,name,model_id,group_id/id,operation,domain
access_ultima_lead_user,Ultima Lead User,ultima.lead,ultima_lead.group_ultima_lead_user,r,"[('category', '=', 'premium')]"
access_ultima_lead_manager,Ultima Lead Manager,ultima.lead,ultima_lead.group_ultima_lead_manager,crud,
```

The module manifest loads the group definitions and access CSV. After changing the access file, the module was upgraded. Odoo 20 uses the `ir.access` model and the `operation` and `domain` columns in `security/ir.access.csv` for these permissions and record filters.

## Verification and status

- **Status:** Complete.
- **User account (`leaduser@ultima`):** Can read Premium leads; cannot create, edit, duplicate, or delete; cannot see the Low Budget test lead.
- **Manager account (`leadmanager@ultima`):** Can see all leads and can create, edit, duplicate, and delete.
- **Tested:** Checked the access behavior in the Odoo interface using both accounts.

## Key takeaway

Access operations control what a group can do to a model, while a domain narrows the records matched by that access. The Manager permission has no domain, so it continues to cover all lead records.

## Next steps

Continue with the pending Week 3 roadmap topics for Days 20 and 21. Their topics remain unconfirmed.

**Activity log:** Configured Odoo 20 security groups and CRUD permissions for Ultima Lead Management, restricted Users to Premium leads with an access domain, and verified the User and Manager behavior in the interface.

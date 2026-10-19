# Day 20 - Model Methods, Recordsets, and Lead Workflow

**Roadmap:** Month 1 / Week 3 / Day 6 (overall Day 20)

**Status:** Complete

**One-word summary:** Workflow

## Overview

Extended Ultima Lead Management with Draft, Confirmed, Approved, and Rejected states. Added Confirm, Approve, and Reject model methods and connected them to form buttons, with role and current-state checks inside the Python methods.

## Objectives

- Practice model methods, recordsets, and the Odoo environment.
- Implement workflow states and object buttons.
- Restrict actions by role and validate each transition.
- Test successful transitions, denied actions, and recordset behavior.

## Model concepts practiced

| Concept | Use in this lesson |
|---|---|
| Model method | A function inside the UltimaLead class, such as action_confirm(). |
| Recordset (self) | The one or more leads on which the method is called. |
| Iteration | for lead in self checks each selected lead before updating any of them. |
| Environment (self.env) | Provides the current user and access to other models. |
| Current user | self.env.user.has_group(...) checks group membership. |
| Recordset update | self.write({...}) updates the records after validation. |
| Controlled elevation | Confirm uses sudo() only after checking the group, read access, and current states. |

## Workflow and roles

| Current state | Action | Next state | Allowed role |
|---|---|---|---|
| Draft | Confirm | Confirmed | User or Manager |
| Confirmed | Approve | Approved | Manager |
| Confirmed | Reject | Rejected | Manager |

Managers inherit the User group. Approved and Rejected are alternative final outcomes; no reset action was added.

## Work completed

### State field

The stored technical values are lowercase; the labels shown in the interface are capitalized.

```python
state = fields.Selection(
    [
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ],
    string="Status",
    default="draft",
    required=True,
    copy=False,
)
```

### Confirm method

The User role remains read-only under the Day 19 access configuration. Confirm verifies that the caller belongs to the User group and can read every selected lead, then validates all states before elevating the fixed status update.

```python
def action_confirm(self):
    if not self.env.user.has_group(
        "ultima_lead.group_ultima_lead_user"
    ):
        raise AccessError("Only Lead Users can confirm leads.")

    self.check_access("read")

    for lead in self:
        if lead.state != "draft":
            raise UserError("Only Draft leads can be confirmed.")

    self.sudo().write({"state": "confirmed"})
    return True
```

The read check preserves the User permission domain limiting visibility to Premium leads. This action grants no general edit permission.

### Manager methods

Approve and Reject check Manager membership, write access, and the Confirmed source state. Managers already have update permission, so these methods use normal write().

```python
def action_approve(self):
    if not self.env.user.has_group(
        "ultima_lead.group_ultima_lead_manager"
    ):
        raise AccessError("Only Lead Managers can approve leads.")

    self.check_access("write")

    for lead in self:
        if lead.state != "confirmed":
            raise UserError("Only Confirmed leads can be approved.")

    self.write({"state": "approved"})
    return True
```

action_reject() applies the same checks and writes {"state": "rejected"}, with rejection-specific error messages. Both exception classes are imported from odoo.exceptions.

### Form buttons and status bar

Added a header inside the form, before the existing sheet. Each object button names its Python method. Group restrictions and invisible expressions control button visibility; the Python checks enforce authorization and valid states when the action methods are called.

```xml
<header>
    <button name="action_confirm" string="Confirm" type="object"
            class="oe_highlight"
            groups="ultima_lead.group_ultima_lead_user"
            invisible="state != 'draft'"/>
    <button name="action_approve" string="Approve" type="object"
            class="oe_highlight"
            groups="ultima_lead.group_ultima_lead_manager"
            invisible="state != 'confirmed'"/>
    <button name="action_reject" string="Reject" type="object"
            groups="ultima_lead.group_ultima_lead_manager"
            invisible="state != 'confirmed'"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,approved,rejected"
           readonly="1"/>
</header>
```

The status bar displays the current state. Workflow buttons disappear in Approved and Rejected states.

## Verification and results

- **Interface checks:** Observed an Approved lead and a Rejected lead. Confirmed that the User account could confirm a lead and the Manager account could subsequently reject it; approval and rejection controls were hidden from the User.
- **Module upgrade:** Succeeded after restarting the server to load the saved Python methods.
- **Direct method checks:** All 27 checks passed in the local odoo20dev database using temporary leads.

| Check group | Checks | Result |
|---|---:|---|
| Test accounts and role separation | 3 | Passed |
| User and Manager confirmation, including invalid source states | 8 | Passed |
| Manager approval and rejection, including invalid source states | 8 | Passed |
| User approval/rejection denied and state preserved | 4 | Passed |
| Confirmation denied for a lead hidden by the Premium domain | 1 | Passed |
| User still denied general edit access | 1 | Passed |
| Mixed-state recordset denied before any Draft lead changes | 2 | Passed |
| **Total** | **27** | **Passed** |

The verification transaction was rolled back afterward, leaving no temporary test leads. These checks cover the workflow methods and existing role permissions.

## Troubleshooting learned

The first XML upgrade failed with action_confirm is not a valid action on ultima.lead. The method and imports were saved correctly, but the running Odoo process still held the earlier Python code. Restarting Odoo and upgrading the module loaded the methods and view successfully.

After Python changes, restart the server; upgrade the module to apply the XML and schema changes.

## Next steps

Continue with Week 3, Day 21 after confirming its roadmap tasks.

**Activity log:** Implemented lead workflow methods with role and state checks, added action buttons and a status bar, verified the interface behavior, and passed 27 Odoo shell checks with temporary records rolled back afterward.

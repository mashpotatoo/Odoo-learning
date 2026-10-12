from odoo import models, fields

class UltimaLead(models.Model):
    _name = "ultima.lead"
    _description = "Ultima Lead"

    name = fields.Char(string="Customer Name", required= True)
    phone = fields.Char(string="Enter Number", required = True)
    budget = fields.Float(string="Enter budget",required = True)


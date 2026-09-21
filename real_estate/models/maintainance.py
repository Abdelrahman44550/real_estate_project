# from odoo import models, fields, api

# class MaintenanceRequest(models.Model):
#     _name = 'maintenance.request'
#     _description = 'Property Maintenance Request'
  
    
#     name = fields.Char(string="Name" , tracking=True)
#     lease_id = fields.Many2one('real_estate.lease')
#     tenant_id = fields.Many2one(related='lease_id.tenant_id', store=True)
#     property_id = fields.Many2one(related='lease_id.property_id', store=True)
    
#     issue_type = fields.Selection([
#         ('plumbing', 'Plumbing'),
#         ('electrical', 'Electrical'),
#         ('air_condition', 'Air Condition'),
#         ('appliance', 'Appliance'),
#         ('other', 'Other')
#     ], required=True)
#     description = fields.Text(required=True, tracking=True)
#     urgency = fields.Selection([
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#         ('emergency', 'Emergency')
#     ], default='medium', required=True)
#     preferred_date = fields.Date()
#     tenant_phone = fields.Char()
# from odoo import models, fields


from odoo import models, fields


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Property Maintenance Request'

    name = fields.Char(
        string="Name",
       
        # tracking=True
    )

    lease_id = fields.Many2one(
        'real_estate.lease',)

    assigned_to=fields.Many2one('res.users' , string='Assigned To')

    tenant_id = fields.Many2one('real_estate.tenant',
        related='lease_id.tenant_id',
        string='Tenant',
        store=True
    )

    property_id = fields.Many2one(
        'real_estate.property',
        related='lease_id.property_id',
        string='Property',
        store=True
    )

    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ],
        string='Issue Type',

    )

    description = fields.Text(
        string='Description',
        
        tracking=True
    )

    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ],
        string='Urgency',
        default='medium'
    )

    preferred_date = fields.Date(
        string='Preferred Date'
    )

    tenant_phone = fields.Char(
        string='Tenant Phone'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ],
        string='Status',
        default='draft'
    )
    actual_cost = fields.Float(string='Actual Cost')
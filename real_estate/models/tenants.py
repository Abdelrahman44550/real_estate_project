from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    crm_id = fields.Many2one('crm.lead',string='CRM ID')
    age_category = fields.Selection([
        ('A', '0-20'),
        ('B', '20-40'),
        ('C', '40-60'),
        ])
    age = fields.Integer(string='Tenants Age', store=True)
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    property_type = fields.Selection([
    ('apartment', 'Apartment'),
    ('house', 'House'),
    ('villa', 'Villa'),
    ('commercial', 'Commercial')
    ], string='Property Type')
    lead_id = fields.Many2one(
    'crm.lead',
    string='CRM Lead',
    index=True
    )
    
    def update_notes (self):
        """Updating"""
        for record in self:
            record.write({'notes': record.name})  
    def get_lead (self):
        for record in (self):
            if record.crm_id.website:
                record.write({'notes':record.crm_id.website})
            else:
                record.write({'notes':record.crm_id.email_from})       
     

    @api.onchange('date_of_birth')
    def _compute_age(self):

        today = fields.Date.today()

        for record in self:
            if record.date_of_birth:
                record.age = (
                    today.year
                    -record.date_of_birth.year
                    - (
                        (today.month , today.day)
                        < (record.date_of_birth.month, record.date_of_birth.day)
                    )
                )
            else:
                record.age = 0

    @api.constrains('date_of_birth')
    def _check_age(self):
        """Ensure age is envalid"""
        for record in self:
            if record.date_of_birth:
                if record.date_of_birth > fields.Date.today():
                    raise UserError("Age cannot be negative")



    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.'),
    ]

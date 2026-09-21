from odoo import models, fields, api
from odoo.exceptions import UserError

class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    
    name = fields.Char(string='Lease Reference', required=True)
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',  # If property deleted, delete lease too
        index=True
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        
        ondelete='cascade',
        index=True
    )
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    maintainances_ids = fields.One2many('maintenance.request', 'lease_id' , string= "Maintainance Requests")

    def convert_to_active(self):
        if not self.env.user.has_group('real_estate.group_tenant_manager'):
            raise UserError("You Can't Edit This Form")
        for record in self:
            record.write({'state' : 'active'})
    def convert_to_draft(self):
        for record in self:
            record.write({'state' : 'draft'})
    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)
    @api.model
    def copy(self, default=None):
        raise UserError("You Can't Duplicate This Lease")

    def write(self,vals):
        if not self.env.user.has_group('real_estate.group_lease_manager'):
            raise UserError("You Can't Edit This Lease")
        return super(Lease, self).write(vals)
    def unlink(self):
        if not self.env.user.has_group('real_estate.group_lease_manager'):
            raise UserError("You Can't Delete This Lease")
        return super(Lease, self).unlink()
        

              
        
        
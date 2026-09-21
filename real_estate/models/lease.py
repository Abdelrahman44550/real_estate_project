from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import timedelta

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
    duration_months = fields.Integer(string='Duration (Months)', compute='_compute_duration', store=True)
    is_active = fields.Boolean(string='Currently Active', compute='_compute_is_active')
    electricity_recharge = fields.Date(string='Recharge Electric Date')
    total_cost = fields.Float(compute='_compute_total_cost', string='Total Cost')
                                    

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
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate lease duration in months"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_months = int(delta.days / 30)
            else:
                record.duration_months = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Set default price when property is selected and validate availability"""
        if self.property_id and not self.property_id.available:
            raise ValidationError("The selected property is not available.")
        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price

    @api.onchange('property_id')
    def _onchange_deposit_paid(self):
        if self.property_id and self.property_id.price:
            self.deposit_paid = self.property_id.price *0.1

    @api.onchange('start_date')
    def _onchange_electricity_recharge(self):
        if self.start_date:
            self.electricity_recharge = self.start_date + timedelta(days=30)
        else:
            self.electricity_recharge = False    

    def make_maintainance_request(self):
        """make maintenance request""" 
            
        self.ensure_one()
        lease_id = self.env['maintenance.request'].sudo().create({
            'lease_id': self.id,
            'issue_type': 'electrical',
            'description': 'hghjjh',
            'urgency': 'medium',
            'preferred_date': self.electricity_recharge,
            'tenant_phone': self.tenant_id.phone ,
            'state': 'submitted',

            
        })
        return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'Maintenance request created successfully!',
            'type': 'success',
            'sticky': False,
        },
    }
    @api.depends('maintainances_ids.actual_cost')
    def _compute_total_cost(self):
        for lease in self:
            # 1
            lease.total_cost = sum(maintenance.actual_cost for maintenance in lease.maintainances_ids)

            # 2
            # lease.total_cost = 0
            # total_cost = 0
            # for maintenance in lease.maintenance_ids:
            #     if maintenance.actual_cost:
            #         total_cost += maintenance.actual_cost
            # lease.total_cost = total_cost   

            # 3
            # maintainances_ids = self.env['maintenance.request'].search([('lease_id', '=', lease.id)])
            # lease.total_cost = 0  
            # for maintenance in maintainances_ids:
            #     if maintenance.actual_cost:
            #         lease.total_cost += maintenance.actual_cost

              
        
        
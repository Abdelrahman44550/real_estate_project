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
    plumbing_cost = fields.Float(
    string='Plumbing Cost',
    compute='_compute_plumbing_cost',
    store=True
    )

    electrical_cost = fields.Float(
    string='Electrical Cost',
    compute='_compute_electrical_cost',
    store=True
    )

    air_condition_cost = fields.Float(
    string='Air Condition Cost',
    compute='_compute_air_condition_cost',
    store=True
    )

    appliance_cost = fields.Float(
    string='Appliance Cost',
    compute='_compute_appliance_cost',
    store=True
    )

    other_cost = fields.Float(
    string='Other Cost',
    compute='_compute_other_cost',
    store=True
    )
    total_cash_amount = fields.Float(
    string='Total Cash Amount',
    compute='_compute_payments_methods',
    store=True
    )
    total_check_amount = fields.Float(
    string='Total Check Amount',
    compute='_compute_payments_methods',
    store=True
    )
    total_bank_transfer_amount = fields.Float(
    string='Total Bank Transfer Amount',
    compute='_compute_payments_methods',
    store=True
    )
    total_credit_card_amount = fields.Float(
    string='Total Credit Card Amount',
    compute='_compute_payments_methods',
    store=True
    )
    total_other_amount = fields.Float(
    string='Total other Amount',
    compute='_compute_payments_methods',
    store=True
    )
    total_amount = fields.Float(
    string='Total  Amount',
    compute='_compute_payments_methods',
    store=True
    )
    payment_ids = fields.One2many(
        'lease.payment',
        'lease_id',
        string='Payments'
    )

                                    

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

    # def write(self,vals):
    #     if not self.env.user.has_group('real_estate.group_lease_manager'):
    #         raise UserError("You Can't Edit This Lease")
    #     return super(Lease, self).write(vals)
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
    
    @api.depends('maintainances_ids.actual_cost', 'maintainances_ids.issue_type')
    def _compute_plumbing_cost(self):
        for lease in self:
            lease.plumbing_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintainances_ids
                if maintenance.issue_type == 'plumbing'
            )


    @api.depends('maintainances_ids.actual_cost', 'maintainances_ids.issue_type')
    def _compute_electrical_cost(self):
        for lease in self:
            lease.electrical_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintainances_ids
                if maintenance.issue_type == 'electrical'
            )


    @api.depends('maintainances_ids.actual_cost', 'maintainances_ids.issue_type')
    def _compute_air_condition_cost(self):
        for lease in self:
            lease.air_condition_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintainances_ids
                if maintenance.issue_type == 'air_condition'
            )


    @api.depends('maintainances_ids.actual_cost', 'maintainances_ids.issue_type')
    def _compute_appliance_cost(self):
        for lease in self:
            lease.appliance_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintainances_ids
                if maintenance.issue_type == 'appliance'
            )


    @api.depends('maintainances_ids.actual_cost', 'maintainances_ids.issue_type')
    def _compute_other_cost(self):
        for lease in self:
            lease.other_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintainances_ids
                if maintenance.issue_type == 'other'
        )

    @api.depends('payment_ids.amount', 'payment_ids.payment_method')         
    def _compute_payments_methods(self):

        for record in self:

            costs = {
                type_name: sum(
                    record.payment_ids.filtered(
                        lambda payment: payment.payment_method == type_name
                    ).mapped('amount')
                )
                for type_name in [
                    'cash',
                    'credit_card',
                    'bank_transfer',
                    'check',
                    'other'
                ]
            }

            record.total_cash_amount = costs['cash']
            record.total_credit_card_amount = costs['credit_card']
            record.total_bank_transfer_amount = costs['bank_transfer']
            record.total_check_amount = costs['check']
            record.total_other_amount = costs['other']
            record.total_amount = sum(
                record.payment_ids.mapped('amount')
        )
    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})
                # === VALIDATION ===
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be after start date")


    @api.constrains('deposit_paid', 'monthly_rent')
    def _check_deposit_paid(self):
        """Ensure deposit paid does not exceed monthly rent"""
        for record in self:
            if record.deposit_paid > record.monthly_rent:
                raise ValidationError(
                    "Deposit Paid cannot be greater than Monthly Rent."
                )
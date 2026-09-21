from odoo import models, fields, api

class LeaseWizard(models.TransientModel):
    _name = 'lease.wizard'
    _description = 'Lease Wizard'
    
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
    monthly_rent = fields.Float(string='Monthly Rent')
    deposit_paid = fields.Float(string='Deposit Paid')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    
    def action_submit_request(self):
        """Create maintenance request and notify manager"""
        self.ensure_one()
        
        # 1. Create maintenance.request record
        maintenance_request = self.env['real_estate.lease'].create({
            'property_id': self.property_id.id,
            # 'tenant_id': self.tenant_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'deposit_paid': self.deposit_paid,
            'state': self.state,
            'monthly_rent' : self.monthly_rent

        })
        
        # 2. Send notification to property manager (Agent)
        # if self.property_id.agent_id:
        #     maintenance_request.activity_schedule(
        #         'mail.mail_activity_data_todo',
        #         user_id=self.property_id.agent_id.id,
        #         summary=f"New {self.issue_type.capitalize()} Maintenance Request",
        #         note=f"Urgency: {self.urgency}\nDescription: {self.description}"
        #     )
        
        # 3. Return action to close wizard and show confirmation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your Lease has been Created successfully and the manager has been notified.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

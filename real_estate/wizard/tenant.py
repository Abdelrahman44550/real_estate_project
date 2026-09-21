from odoo import models, fields, api

class TenantWizard(models.TransientModel):
    _name = 'tenant.wizard'
    _description = 'Tenant Wizard'

    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    city = fields.Char(string='City')

    def action_create_tanent(self):
        """Create maintenance request and notify manager"""
        self.ensure_one()
        tenant_id = self.env['real_estate.tenant'].sudo().create({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your Tenant has been Created successfully and the manager has been notified.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True) 
    
    def get_lead_name (self):
        for record in self:
            record.write({'description': record.name})
    def _cron_create_tenant (self):
        """Creating New Tenant"""
        leads = self.search([
            ('property_type', '!=', False)
        ])
        for lead in leads:
            self.env['real_estate.tenant'].create({
                'name': lead.name,
                'email': lead.email_from,
                'property_type': lead.property_type,
                'phone': lead.phone,
                'lead_id': lead.id,
            })
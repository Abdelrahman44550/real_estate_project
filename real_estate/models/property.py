from odoo import models, fields, api

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)   
    agent_id = fields.Many2one('res.users', string='Sales Person')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)
    deposit = fields.Float(string='Deposit', required=True)
    lease_ids = fields.One2many('real_estate.lease', 'property_id', string='Leases')

    # Smart Button Count
    lease_count = fields.Integer(
        string='Lease Count',
        compute='_compute_lease_count'
    )

    def _compute_lease_count(self):
            for record in self:
                record.lease_count = len(record.lease_ids)

    def action_view_leases(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'real_estate.lease',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {
                'default_property_id': self.id
            },
        }
    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})
    
    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})
    def describtion (self):
        """Descripe"""
        for record in self:
            record.write({'description': record.description+'description'})
    def increase_deposit(self):
        """Increasing Deposit"""
        for record in self:
            record.write({'deposit': record.deposit + 1000})
    def add_bedroom(self):
        """Increasing Deposit"""
        for record in self:
            record.write({'bedrooms': record.bedrooms + 1})
    def update_to_villa (self):
        """Updating_to_villa"""
        for record in (self):
            if record.available:
                record.write({'property_type': "villa"})
    def add_agent (self):
        for record in (self):
            record.write({'description': record.agent_id.login})



    # def write(self, vals):        
    #     if vals.get('available')==False:
    #         if 'bedroom' in vals:
    #             #raise UserError("cannot change bedrroms it's rented")
    #             return super(property, self).write(vals)    



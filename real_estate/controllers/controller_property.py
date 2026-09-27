from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class RealEstatePropertyPortal(CustomerPortal):

    # =========================================
    # Portal Home Counter
    # =========================================

    def _prepare_home_portal_values(self, counters):

        values = super()._prepare_home_portal_values(counters)

        if "property_count" in counters:

            property_count = request.env[
                'real_estate.property'
            ].sudo().search_count([
                ('agent_id', '=', request.env.user.id)
            ])

            values['property_count'] = property_count

        return values


    # =========================================
    # Portal Layout Values
    # =========================================

    def _prepare_portal_layout_values(self):

        values = super()._prepare_portal_layout_values()

        property_count = request.env[
            'real_estate.property'
        ].sudo().search_count([
            ('agent_id', '=', request.env.user.id)
        ])

        values.update({
            'property_count': property_count,
        })

        return values


    # =========================================
    # My Properties
    # =========================================

    @http.route(
        ['/my/properties', '/my/properties/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_my_properties(self, page=1, **kw):

        values = self._prepare_portal_layout_values()

        properties = request.env[
            'real_estate.property'
        ].sudo().search([
            ('agent_id', '=', request.env.user.id)
        ], order='create_date desc')

        values.update({
            'properties': properties,
        })

        return request.render(
            'real_estate.portal_my_properties',
            values
        )


    # =========================================
    # Available Properties
    # =========================================

    @http.route(
        ['/my/available-properties'],
        type='http',
        auth='user',
        website=True
    )
    def portal_available_properties(
        self,
        property_type=None,
        min_price=None,
        max_price=None,
        min_bedrooms=None,
        **kw
    ):

        values = self._prepare_portal_layout_values()

        # Start with available properties only
        domain = [
            ('available', '=', True)
        ]

        # Property Type
        if property_type:
            domain.append(
                ('property_type', '=', property_type)
            )

        # Minimum Price
        if min_price:
            domain.append(
                ('price', '>=', float(min_price))
            )

        # Maximum Price
        if max_price:
            domain.append(
                ('price', '<=', float(max_price))
            )

        # Minimum Bedrooms
        if min_bedrooms:
            domain.append(
                ('bedrooms', '>=', int(min_bedrooms))
            )

        # Search properties
        properties = request.env[
            'real_estate.property'
        ].sudo().search(
            domain,
            order='create_date desc'
        )

        values.update({
            'available_properties': properties,

            # Keep filter values in the form
            'property_type': property_type,
            'min_price': min_price,
            'max_price': max_price,
            'min_bedrooms': min_bedrooms,
        })

        return request.render(
            'real_estate.portal_available_properties',
            values
        )
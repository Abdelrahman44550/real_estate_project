# -*- coding: utf-8 -*-
# from odoo import http


# class RealEstateProject(http.Controller):
#     @http.route('/real_estate_project/real_estate_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_estate_project/real_estate_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_estate_project.listing', {
#             'root': '/real_estate_project/real_estate_project',
#             'objects': http.request.env['real_estate_project.real_estate_project'].search([]),
#         })

#     @http.route('/real_estate_project/real_estate_project/objects/<model("real_estate_project.real_estate_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_estate_project.object', {
#             'object': obj
#         })


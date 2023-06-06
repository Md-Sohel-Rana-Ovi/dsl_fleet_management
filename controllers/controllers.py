# -*- coding: utf-8 -*-
# from odoo import http


# class DslFleetManagement(http.Controller):
#     @http.route('/dsl_fleet_management/dsl_fleet_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dsl_fleet_management/dsl_fleet_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dsl_fleet_management.listing', {
#             'root': '/dsl_fleet_management/dsl_fleet_management',
#             'objects': http.request.env['dsl_fleet_management.dsl_fleet_management'].search([]),
#         })

#     @http.route('/dsl_fleet_management/dsl_fleet_management/objects/<model("dsl_fleet_management.dsl_fleet_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dsl_fleet_management.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class PosQtyUpdation(http.Controller):
#     @http.route('/pos_qty_updation/pos_qty_updation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_qty_updation/pos_qty_updation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_qty_updation.listing', {
#             'root': '/pos_qty_updation/pos_qty_updation',
#             'objects': http.request.env['pos_qty_updation.pos_qty_updation'].search([]),
#         })

#     @http.route('/pos_qty_updation/pos_qty_updation/objects/<model("pos_qty_updation.pos_qty_updation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_qty_updation.object', {
#             'object': obj
#         })

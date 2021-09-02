# -*- coding: utf-8 -*-

from odoo import models, fields, api


class YeloOrders(models.Model):
    _name = 'yelo.orders'
    _rec_name = 'yelo_order_id'
    _description = 'Yelo Orders'

    yelo_customer_id = fields.Integer(string='Customer ID', required=True)
    yelo_restaurant_id = fields.Integer(string='Restaurant ID', required=True)
    yelo_order_id = fields.Integer(string="Order ID", required=True)
    yelo_order_type = fields.Selection([
            ('pickup', 'Pickup'),
            ('delivery', 'Delivery'),
        ], string="Order Type")
    sync_status = fields.Boolean(string='Sync status', default=False)
    function_1_status = fields.Boolean(string='F1 status', default=False)
    function_2_status = fields.Boolean(string='F2 status', default=False)
    function_3_status = fields.Boolean(string='F3 status', default=False)
    function_4_status = fields.Boolean(string='F4 status', default=False)

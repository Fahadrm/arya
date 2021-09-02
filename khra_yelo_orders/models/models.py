# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


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

    @api.model
    def _yelo_order_sync(self):
        records = self.search([
            ('sync_status', '=', False)
        ])
        for record in records:
            webhook = self.env["configure.webhook"].search([], limit=1)
            url = webhook.request_url
            api_key = webhook.api_key
            payload = "{\r\n    \"api_key\"   : {} ,\r\n    \"job_id\"    : {}\r\n}".format(api_key, record.yelo_order_id)
            headers = {}

            response = requests.request("POST", url, headers=headers, data=payload)
            _logger.info('RESPONSE RECEIVED FROM YELO when an order placed %r', response.text)


# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):
    @http.route('/webhook/products/<string:auth_token>', type='json', auth='public', methods=['POST'])
    def webhook(self, auth_token, **post):
        _logger.info('RESPONSE RECEIVED FROM YELO IS %r', auth_token)
        # print('post_data', post)
        # yelo_product = request.env["yelo.products"].sudo().search(
        #     [('yelo_order_id', '=', post['order_id'])])
        # if not yelo_product:
        #     request.env["yelo.products"].create({
        #         'yelo_order_id': post['order_id']
        #     })
        yelo_product = request.env["yelo.products"].sudo().search(
            [('yelo_order_id', '=', request.jsonrequest['order_id'])])
        if not yelo_product:
            request.env["yelo.products"].sudo().create({
                'yelo_order_id': request.jsonrequest['order_id']
            })
        return {}


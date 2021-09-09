# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging
import json
import datetime

_logger = logging.getLogger(__name__)


class YeloOrders(models.Model):
    _name = 'yelo.orders'
    _rec_name = 'yelo_order_id'
    _description = 'Yelo Orders'

    yelo_customer_id = fields.Integer(string='Customer ID', required=True)
    yelo_restaurant_id = fields.Integer(string='Restaurant ID', required=True)
    yelo_order_id = fields.Integer(string="Order ID", required=True)
    yelo_order_status = fields.Integer(string="Order Status")
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
        pass
        # records = self.search([
        #     ('sync_status', '=', False)
        # ])
        # for record in records:
        #     webhook = self.env["configure.webhook"].search([], limit=1)
        #     url = webhook.request_url
        #     api_key = webhook.api_key
        #     # payload = "{\r\n    \"api_key\"   :\" %s\" ,\r\n    \"job_id\"    : %d \r\n}" % (api_key, record.yelo_order_id)
        #     # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        #     todo = {"api_key": api_key, "job_id": record.yelo_order_id}
        #
        #     # response = requests.request("POST", url, headers=headers, data=payload)
        #     # _logger.info('RESPONSE RECEIVED FROM YELO when an order placed %r', response.text)
        #
        #     headers = {"Content-Type": "application/json"}
        #     response = requests.post(url, data=json.dumps(todo), headers=headers)
        #     data_received = response.json()
        #     for data in data_received['data']:
        #         if data['job_status'] == 13:
        #             restaurant = self.env['res.partner'].search([('yelo_restaurant_id', '=', data['merchant_id'])])
        #             customer = self.env['res.partner'].search([('yelo_customer_id', '=', data['customer_id'])])
        #             if not restaurant:
        #                 restaurant = self.env['res.partner'].create({
        #                     'name': data['merchant_name'],
        #                     'partner_type': 'restaurant',
        #                     'yelo_restaurant_id': data['merchant_id'],
        #                     'phone': data['merchant_phone_number'],
        #                     'email': data['merchant_email'],
        #                     'property_account_receivable_id': self.env.company.restaurant_receivable_account_id.id,
        #                     'property_account_payable_id': self.env.company.restaurant_payable_account_id.id,
        #                 })
        #             if not customer:
        #                 customer = self.env['res.partner'].create({
        #                     'name': data['customer_username'],
        #                     'partner_type': 'customer',
        #                     'yelo_customer_id': data['customer_id'],
        #                     'phone': data['customer_phone'],
        #                     'email': data['customer_email'],
        #                     'property_account_receivable_id': self.env.company.customer_receivable_account_id.id,
        #                     'property_account_payable_id': self.env.company.customer_payable_account_id.id,
        #                 })
        #             new_date = datetime.datetime.strptime(data['job_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        #             move_date = new_date.date()
        #             first_entry_move = self.env['account.move'].create({
        #                 'date': move_date,
        #                 'journal_id': self.env.company.yelo_first_entry_journal_id.id,
        #                 'company_id': self.env.company.id,
        #                 'user_id': self.env.user.id,
        #                 'yelo_order_id': record.yelo_order_id,
        #                 'line_ids': [
        #                     (0, 0,
        #                         {
        #                             'account_id': customer.property_account_receivable_id.id,
        #                             'name': "Customer Control A/c",
        #                             'debit': data['total_amount'],
        #                             'credit': 0,
        #                             'currency_id': self.env.company.currency_id.id,
        #                             'partner_id': customer.id,
        #                         }),
        #                     (0, 0,
        #                         {
        #                             'account_id': self.env.company.order_processed_account_id.id,
        #                             'name': "Order Processed",
        #                             'debit': 0,
        #                             'credit': data['total_amount'],
        #                             'currency_id': self.env.company.currency_id.id
        #                         })
        #                 ]
        #             })
        #             # first_entry_move.post()
        #             # if first_entry_move.post():
        #             #     if data['is_cash_on_delivery']:
        #             #         second_entry_move = self.env['account.move'].create({
        #             #             'date': move_date,
        #             #             'journal_id': self.env.company.yelo_second_entry_journal_id.id,
        #             #             'company_id': self.env.company.id,
        #             #             'user_id': self.env.user.id,
        #             #             'yelo_order_id': record.yelo_order_id,
        #             #             'line_ids': [
        #             #                 (0, 0,
        #             #                  {
        #             #                      'account_id': self.env.company.delivery_boy_receivable_account_id.id,
        #             #                      'name': "Rider Control A/c",
        #             #                      'debit': data['total_amount'],
        #             #                      'credit': 0,
        #             #                      'currency_id': self.env.company.currency_id.id
        #             #                  }),
        #             #                 (0, 0,
        #             #                  {
        #             #                      'account_id': customer.property_account_receivable_id.id,
        #             #                      'name': "Customer Control A/c",
        #             #                      'debit': 0,
        #             #                      'credit': data['total_amount'],
        #             #                      'currency_id': self.env.company.currency_id.id,
        #             #                      'partner_id': customer.id,
        #             #                  })
        #             #             ]
        #             #         })
        #             #         second_entry_move.post()
        #             #     else:
        #             #         if data['payment_method'] == 8:
        #             #             second_entry_move = self.env['account.move'].create({
        #             #                 'date': move_date,
        #             #                 'journal_id': self.env.company.yelo_second_entry_journal_id.id,
        #             #                 'company_id': self.env.company.id,
        #             #                 'user_id': self.env.user.id,
        #             #                 'yelo_order_id': record.yelo_order_id,
        #             #                 'line_ids': [
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': self.env.company.razor_pay_payment_gateway_account_id.id,
        #             #                          'name': "Razor pay Payment Gateway A/c",
        #             #                          'debit': data['total_amount'],
        #             #                          'credit': 0,
        #             #                          'currency_id': self.env.company.currency_id.id
        #             #                      }),
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': customer.property_account_receivable_id.id,
        #             #                          'name': "Customer Control A/c",
        #             #                          'debit': 0,
        #             #                          'credit': data['total_amount'],
        #             #                          'currency_id': self.env.company.currency_id.id,
        #             #                          'partner_id': customer.id,
        #             #                      })
        #             #                 ]
        #             #             })
        #             #             second_entry_move.post()
        #             #         if data['payment_method'] == 8:
        #             #             second_entry_move1 = self.env['account.move'].create({
        #             #                 'date': move_date,
        #             #                 'journal_id': self.env.company.yelo_second_entry_journal_id.id,
        #             #                 'company_id': self.env.company.id,
        #             #                 'user_id': self.env.user.id,
        #             #                 'yelo_order_id': record.yelo_order_id,
        #             #                 'line_ids': [
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': self.env.company.razor_pay_payment_gateway_account_id.id,
        #             #                          'name': "Razor pay Payment Gateway A/c",
        #             #                          'debit': data['total_amount'],
        #             #                          'credit': 0,
        #             #                          'currency_id': self.env.company.currency_id.id
        #             #                      }),
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': self.env.company.customer_wallet_account_id.id,
        #             #                          'name': "Customer Wallet A/c",
        #             #                          'debit': 0,
        #             #                          'credit': data['total_amount'],
        #             #                          'currency_id': self.env.company.currency_id.id,
        #             #                          'partner_id': customer.id,
        #             #                      })
        #             #                 ]
        #             #             })
        #             #             second_entry_move1.post()
        #             #             second_entry_move2 = self.env['account.move'].create({
        #             #                 'date': move_date,
        #             #                 'journal_id': self.env.company.yelo_second_entry_journal_id.id,
        #             #                 'company_id': self.env.company.id,
        #             #                 'user_id': self.env.user.id,
        #             #                 'yelo_order_id': record.yelo_order_id,
        #             #                 'line_ids': [
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': self.env.company.customer_wallet_account_id.id,
        #             #                          'name': "Customer Wallet A/c",
        #             #                          'debit': data['total_amount'],
        #             #                          'credit': 0,
        #             #                          'currency_id': self.env.company.currency_id.id,
        #             #                          'partner_id': customer.id,
        #             #                      }),
        #             #                     (0, 0,
        #             #                      {
        #             #                          'account_id': customer.property_account_receivable_id.id,
        #             #                          'name': "Customer Control A/c",
        #             #                          'debit': 0,
        #             #                          'credit': data['total_amount'],
        #             #                          'currency_id': self.env.company.currency_id.id,
        #             #                          'partner_id': customer.id,
        #             #                      })
        #             #                 ]
        #             #             })
        #             #             second_entry_move2.post()
        #
        #     _logger.info('RESPONSE RECEIVED FROM YELO when an order placed %r', data_received['data'])



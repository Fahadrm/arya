# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class RestaurantPaymentBatch(models.Model):
    _name = 'restaurant.payment.batch'
    _description = 'Restaurant payment batch'
    _order = 'id desc'

    name = fields.Char('Batch Reference', required=True, index=True, copy=False, default='New')
    date = fields.Datetime('Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    payment_processing_date = fields.Date(string='Payment Processing Date', readonly=True, copy=False)
    user_id = fields.Many2one('res.users', string='User', index=True,
                              default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
            vals['name'] = self.env['ir.sequence'].next_by_code('restaurant.payment.batch', sequence_date=seq_date) or '/'
        return super(RestaurantPaymentBatch, self).create(vals)

    @api.model
    def _sync_restaurant_payments(self):
        date = datetime.datetime.today().date() 
#         - datetime.timedelta(days=1)
        move_line_ids = self.env['account.move.line'].search([('partner_id', '!=', False),
            ('move_id.journal_id', '=', self.env.company.yelo_third_entry_journal_id.id),
            ('date', '<=', date), ('account_id', '=', self.env.company.restaurant_receivable_account_id.id),
            ('restaurant_cost_type', '!=', False), ('move_id.reversed_entry_id', '=', False)])
        if move_line_ids:
            batch_id = self.create({
                'payment_processing_date': date,
            })
        restaurant_data = {}
        for line in move_line_ids:
            if line.partner_id.id not in restaurant_data:
                restaurant_data[line.partner_id.id] = {
                    'gst': line.credit if line.restaurant_cost_type == 'gst' else 0,
                    'food_cost': line.credit if line.restaurant_cost_type == 'food_cost' else 0,
                    'name': line.partner_id.name,
                    'orders': [line.move_id.yelo_order_id]
                }
            else:
                restaurant_data[line.partner_id.id]['gst'] += line.credit if line.restaurant_cost_type == 'gst' else 0
                restaurant_data[line.partner_id.id]['food_cost'] += line.credit if line.restaurant_cost_type == 'food_cost' else 0
                if line.move_id.yelo_order_id not in restaurant_data[line.partner_id.id]['orders']:
                    restaurant_data[line.partner_id.id]['orders'].append(line.move_id.yelo_order_id)
        for key in restaurant_data:
            adjust_amt = 0
            adjust_food_gst = 0
            move_line_ids = self.env['account.move.line'].search([('partner_id', '=', key),
                                                                  ('move_id.reversed_entry_id.journal_id', '=',
                                                                   self.env.company.yelo_third_entry_journal_id.id),
                                                                  ('date', '<=', date), ('account_id', '=',
                                                                                        self.env.company.restaurant_receivable_account_id.id),
                                                                  ('restaurant_cost_type', '!=', False)])
            for line in move_line_ids:
                adjust_amt += line.dedit if line.restaurant_cost_type == 'food_cost' else 0,
                adjust_food_gst += line.debit if line.restaurant_cost_type == 'gst' else 0,
            self.env['restaurant.payments'].create({
                'name': batch_id.name + " " + restaurant_data[key]['name'],
                'batch_id': batch_id.id,
                'partner_id': key,
                'food_cost': restaurant_data[key]['food_cost'],
                'adjust_amt': adjust_amt,
                'food_gst': restaurant_data[key]['gst'],
                'adjust_food_gst': adjust_food_gst,
                'total_orders': len(restaurant_data[line.partner_id.id]['orders'])
            })


class RestaurantPayments(models.Model):
    _name = 'restaurant.payments'
    _description = 'Restaurant payments'
    _order = 'batch_id, id'

    name = fields.Text(string='Description', required=True)
    batch_id = fields.Many2one('restaurant.payment.batch', string='Batch Reference', index=True, required=True,
                               ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Restaurant/Partner',
                                 domain="[('partner_type', '=', 'restaurant'),('yelo_restaurant_id','!=',False)]")
    yelo_restaurant_id = fields.Integer(string='Yelo Restaurant ID', related='partner_id.yelo_restaurant_id',
                                        readonly=True, store=True)
    food_cost = fields.Float(string='Food Cost', digits='Product Price')
    adjust_amt = fields.Float(string='Adjustments', digits='Product Price')
    revised_order_amount = fields.Float(string='Revised Order Amount', digits='Product Price', compute="_compute_revised_order_amt")
    food_gst = fields.Float(string='Food GST', digits='Product Price')
    adjust_food_gst = fields.Float(string='Adjust Food GST', digits='Product Price')
    gst = fields.Float(string='GST', digits='Product Price', compute="_compute_revised_food_gst")
    commission_rate = fields.Float(string='Commission Rate', digits='Product Price', related='partner_id.restaurant_commission')
    commission_amt = fields.Float(string='Commission Amount', digits='Product Price', compute="_compute_amount")
    commission_gst = fields.Float(string="Commission GST", digits='Product Price', compute="_compute_amount")
    commission_tcs = fields.Float(string="Commission TCS", digits='Product Price', compute="_compute_amount")
    commission_tds = fields.Float(string="Commission TDS", digits='Product Price', compute="_compute_amount")
    final_payment = fields.Float(string='Final Payment', required=True, digits='Product Price', compute="_compute_amount")
    total_orders = fields.Float(string='Total Orders', digits='Product Unit of Measure')
    company_id = fields.Many2one('res.company', related='batch_id.company_id', string='Company', store=True,
                                 readonly=True)
    user_id = fields.Many2one('res.users', related='batch_id.user_id', string='User', store=True, readonly=True)
    payout_email = fields.Boolean(string='Payout Email', default=False)

    @api.depends('food_cost', 'adjust_amt', 'gst', 'commission_rate')
    def _compute_amount(self):
        for record in self:
            commission = ((record.food_cost - record.adjust_amt) * record.commission_rate)/100
            commission_tax_details = self.env.company.account_commission_tax_id.compute_all(
                commission, quantity=1)
            commission_amt = commission_tax_details['total_excluded']
            commission_gst = commission_tax_details['total_included'] - commission_tax_details['total_excluded']
            commission_tcs_details = self.env.company.account_commission_tcs_tax_id.compute_all(
                commission_amt + commission_gst, quantity=1)
            commission_tds_details = self.env.company.account_commission_tds_tax_id.compute_all(
                commission_amt + commission_gst, quantity=1)
            commission_tcs = commission_tcs_details['total_included'] - commission_tcs_details['total_excluded']
            commission_tds = commission_tds_details['total_included'] - commission_tds_details['total_excluded']
            final_payment = record.food_cost - record.adjust_amt + record.gst - commission_amt - commission_gst \
                            - commission_tcs - commission_tds
            record.update({
                'commission_amt': commission_amt,
                'commission_gst': commission_gst,
                'commission_tcs': commission_tcs,
                'commission_tds': commission_tds,
                'final_payment': final_payment
            })

    @api.depends('food_cost', 'adjust_amt')
    def _compute_revised_order_amt(self):
        for record in self:
            revised_order_amount = record.food_cost - record.adjust_amt
            record.update({
                'revised_order_amount': revised_order_amount
            })

    @api.depends('food_gst', 'adjust_food_gst')
    def _compute_revised_food_gst(self):
        for record in self:
            gst = record.food_gst - record.adjust_food_gst
            record.update({
                'gst': gst
            })



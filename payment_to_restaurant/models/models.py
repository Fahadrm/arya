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
    user_id = fields.Many2one('res.users', string='User', index=True, tracking=True,
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
        date = datetime.datetime.today().date() - datetime.timedelta(days=1)
        move_line_ids = self.env['account.move.line'].search([('partner_id', '!=', False),
            ('move_id.journal_id', '=', self.env.company.yelo_third_entry_journal_id.id),
            ('date', '=', date), ('account_id', '=', self.env.company.restaurant_receivable_account_id.id),
            ('restaurant_cost_type', '!=', False)])
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
                }
            else:
                restaurant_data[line.partner_id.id]['gst'] += line.credit if line.restaurant_cost_type == 'gst' else 0
                restaurant_data[line.partner_id.id]['food_cost'] += line.credit if line.restaurant_cost_type == 'food_cost' else 0
        for key in restaurant_data:
            self.env['restaurant.payments'].create({
                'name': batch_id.name + " " + restaurant_data[key]['name'],
                'batch_id': batch_id.id,
                'partner_id': key,
                'food_cost': restaurant_data[key]['food_cost'],
                'gst': restaurant_data[key]['gst'],
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
    gst = fields.Float(string='GST', digits='Product Price')
    commission_rate = fields.Float(string='Commission Rate', digits='Product Price', related='partner_id.restaurant_commission')
    commission_amt = fields.Float(string='Commission Amount', digits='Product Price', compute="_compute_amount")
    final_payment = fields.Float(string='Final Payment', required=True, digits='Product Price', compute="_compute_amount")

    company_id = fields.Many2one('res.company', related='batch_id.company_id', string='Company', store=True,
                                 readonly=True)
    user_id = fields.Many2one('res.users', related='batch_id.user_id', string='User', store=True, readonly=True)

    @api.depends('food_cost', 'gst', 'commission_rate')
    def _compute_amount(self):
        for record in self:
            commission_amt = (record.food_cost * record.commission_rate)/100
            final_payment = record.food_cost - commission_amt + record.gst
            record.update({
                'commission_amt': commission_amt,
                'final_payment': final_payment
            })



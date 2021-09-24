# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import base64


class RestaurantMailing(models.Model):
    _name = 'restaurant.mailing'
    _description = 'Mail to Restaurants'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _order = 'sent_date DESC'
    _rec_name = "subject"

    active = fields.Boolean(default=True, tracking=True)
    subject = fields.Char('Subject', help='Subject of your Mailing', required=True, translate=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    email_from = fields.Char(string='Send From', required=True,
                             default=lambda self: self.env.user.email_formatted)
    email_to = fields.Text('To', help='Message recipients (emails)')
    email_cc = fields.Char('Cc', help='Carbon copy message recipients')
    recipient_ids = fields.Many2many('res.partner', string='To (Partners)',
                                     context={'active_test': False})
    sent_date = fields.Datetime(string='Sent Date', copy=False)
    schedule_date = fields.Datetime(string='Scheduled for', tracking=True)
    body_html = fields.Text('Rich-text Contents', help="Rich-text/HTML message")
    attachment_ids = fields.Many2many('ir.attachment', 'restaurant_mailing_ir_attachments_rel',
                                      'restaurant_mailing_id', 'attachment_id', string='Attachments')
    state = fields.Selection([('draft', 'Draft'), ('in_queue', 'In Queue'), ('sending', 'Sending'), ('done', 'Sent')],
                             string='Status', required=True, tracking=True, copy=False, default='draft')
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True,  default=lambda self: self.env.user)
    # Restaurant Payment Details
    partner_id = fields.Many2one('res.partner', string='Restaurant/Partner',
                                 domain="[('partner_type', '=', 'restaurant'),('yelo_restaurant_id','!=',False)]")
    yelo_restaurant_id = fields.Integer(string='Yelo Restaurant ID', related='partner_id.yelo_restaurant_id',
                                        readonly=True, store=True)
    food_cost = fields.Float(string='Food Cost', digits='Product Price')
    gst = fields.Float(string='GST', digits='Product Price')
    commission_rate = fields.Float(string='Commission Rate', digits='Product Price',
                                   related='partner_id.restaurant_commission')
    commission_amt = fields.Float(string='Commission Amount', digits='Product Price')
    final_payment = fields.Float(string='Final Payment', digits='Product Price')
    payout_start_date = fields.Date(string='Start Date', readonly=True, copy=False, store=True)
    payout_end_date = fields.Date(string='End Date', readonly=True, copy=False, store=True)
    total_orders = fields.Float(string='Total Orders', digits='Product Unit of Measure')

    def _update_payment_details(self):
        date1 = datetime.datetime.today().date() - datetime.timedelta(days=9)
        date2 = datetime.datetime.today().date() - datetime.timedelta(days=1)
        restaurant_payments = self.env['restaurant.payments'].search([
            ('batch_id.payment_processing_date', '>=', date1),
            ('batch_id.payment_processing_date', '<=', date2),
            ('payout_email', '=', False)])
        restaurant_details = {}
        restaurant_ids = []
        restaurant_data = {}
        for payments in restaurant_payments:
            if payments.partner_id.id not in restaurant_details:
                restaurant_details[payments.partner_id.id] = [{
                    'gst': payments.gst,
                    'food_cost': payments.food_cost,
                    'commission_amt': payments.commission_amt,
                    'final_payment': payments.final_payment,
                    'batch_id': payments.batch_id,
                    'payment_processing_date': payments.batch_id.payment_processing_date,
                }]
                restaurant_ids.append(payments.partner_id.id)
            else:
                restaurant_details[payments.partner_id.id].append(
                    {
                        'gst': payments.gst,
                        'food_cost': payments.food_cost,
                        'commission_amt': payments.commission_amt,
                        'final_payment': payments.final_payment,
                        'batch_id': payments.batch_id,
                        'payment_processing_date': payments.batch_id.payment_processing_date,
                    }
                )
            if payments.partner_id.id not in restaurant_data:
                restaurant_data[payments.partner_id.id] = {
                    'gst': payments.gst,
                    'food_cost': payments.food_cost,
                    'commission_amt': payments.commission_amt,
                    'final_payment': payments.final_payment,
                    'partner_id': payments.partner_id,
                    'total_orders': payments.total_orders,
                }
            else:
                restaurant_data[payments.partner_id.id]['gst'] += payments.gst
                restaurant_data[payments.partner_id.id]['food_cost'] += payments.food_cost
                restaurant_data[payments.partner_id.id]['commission_amt'] += payments.commission_amt
                restaurant_data[payments.partner_id.id]['final_payment'] += payments.final_payment
                restaurant_data[payments.partner_id.id]['total_orders'] += payments.total_orders
            payments.payout_email = True
        for key in restaurant_data:
            email_date = self.create({
                'subject': restaurant_data[key]['partner_id'].name + " Payout",
                'email_to': restaurant_data[key]['partner_id'].email,
                'partner_id': key,
                'food_cost': restaurant_data[key]['food_cost'],
                'gst': restaurant_data[key]['gst'],
                'commission_rate': restaurant_data[key]['partner_id'].restaurant_commission,
                'commission_amt': restaurant_data[key]['commission_amt'],
                'final_payment': restaurant_data[key]['final_payment'],
                'payout_start_date': date1,
                'payout_end_date': date2,
                'total_orders': restaurant_data[key]['total_orders'],
            })

    def action_put_in_queue(self):
        self.write({'state': 'in_queue'})

    @api.constrains('schedule_date')
    def _check_schedule_date(self):
        for record in self:
            if record.schedule_date < fields.Datetime.now():
                raise ValidationError(_('Please select a date equal/or greater than the current date.'))

    def _send_payment_details(self):
        pass
        mass_mailings = self.search([('state', '=', 'in_queue'), '|', ('schedule_date', '<', fields.Datetime.now()), ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            # pdf_attachment = mass_mailing.action_get_attachment(res, company)

            # return self.env.ref('reorder_email_notification.reorder_email_notification_action_xlsx').report_action([],data=data)

            mail_to = []
            orders = []
            for recipient in mass_mailing.recipient_ids:
                mail_to.append(recipient.email)
            mail_to.append(mass_mailing.email_to)
            mass_mailing_mail_to = ",".join(mail_to)
            payments = self.env['restaurant.payments'].search([
                ('batch_id.payment_processing_date', '>=', mass_mailing.payout_start_date),
                ('batch_id.payment_processing_date', '<=', mass_mailing.payout_end_date),
                ('partner_id', '=', mass_mailing.partner_id.id)])
            for payment in payments:
                orders.append(
                    {
                        'payout_on': payment.batch_id.payment_processing_date,
                        'order_amount': payment.revised_order_amount,
                        'payout_amount': payment.final_payment,
                        'total_orders': payment.total_orders,
                    }
                )
            template_id = self.env.ref('mail_to_restaurant.restaurant_weekly_payment_mail_template')
            if template_id and mass_mailing_mail_to:
                # template_id.send_mail(self.id, force_send=True)
                template_id.with_context({'email_to': mass_mailing_mail_to, 'email_cc': mass_mailing.email_cc,
                                          'orders': orders, }).\
                    send_mail(mass_mailing.id, force_send=True, raise_exception=False, email_values=None, notif_layout=False)

    # def action_get_attachment(self, res, company):
    #     pdf = self.env.ref('reorder_email_notification.action_reorder_email_notification_pdf')\
    #         .render_qweb_pdf(self.ids, data={'data': res, 'company': company})
    #     b64_pdf = base64.b64encode(pdf[0])
    #     # save pdf as attachment
    #     name = "reorder_qty_notification"
    #     return self.env['ir.attachment'].create({
    #         'name': name,
    #         'type': 'binary',
    #         'datas': b64_pdf,
    #         # 'company_id': company.id,
    #         # 'datas_fname': name + '.pdf',
    #         # 'store_fname': name,
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/x-pdf'
    #     })



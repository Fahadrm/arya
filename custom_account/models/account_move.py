from odoo import api, models, fields


class AccountMoveInherit(models.Model):

    _inherit = 'account.move'

    def button_cancel(self):
        res = super(AccountMoveInherit, self).button_cancel()
        self.ensure_one()
        template = self.env.ref('custom_account.cancel_invoice_email_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': ('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        self.write({'auto_post': False, 'state': 'cancel'})
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConfigureWebhook(models.Model):
    _name = 'configure.webhook'
    _description = 'Webhook Configuration'

    name = fields.Char(required=True, string='Name')
    webhook_auth_key = fields.Char(string="Auth Key")
    request_url = fields.Char(string="URL", required=True)
    api_key = fields.Char(string="Api Key", required=True)

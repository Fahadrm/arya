# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging
import json
import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    yelo_order_id = fields.Integer(string="Yelo Order Ref")

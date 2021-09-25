# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import os
import urllib.request
import json
# open a connection to a URL using urllib
from odoo.exceptions import AccessDenied, UserError
from odoo.addons import decimal_precision as dp



class ProductQtyUpdation(models.Model):
    _name = "product.qty.updation"

    name = fields.Char(string="Name",default="Qty")
    pos_qty = fields.Float(string="Qty",digits=dp.get_precision('Weignscale Qty'))


    def read_file_button(self):
        s=[]
        if self.env['product.qty.updation'].search([]):
            updation = self.env['product.qty.updation'].search([],order="id desc",limit=1)
            for i in updation:
                if i.pos_qty:
                    field = i.pos_qty
                    field = str(i.pos_qty).strip().split()
                    s = field
                    i.unlink()
            self.env['product.qty.updation'].search([]).unlink()
        else:
            return "QTY"

        if s!=[]:
            return s[0]
        else:
            return "QTY"




# class PosOrder(models.Model):
#     _inherit = 'pos.order'
#
    # def read_file_button(self):
    #     webUrl = urllib.request.urlopen('http://127.0.0.1/sample.json')
    #
    #     # get the result code and print it
    #     print("result code: " + str(webUrl.getcode()))
    #
    #     myfile = json.loads(webUrl.read())
    #
    #     # read the data from the URL and print it
    #     # myfile = webUrl.read()
    #     print(myfile)
    #     # file = os.path.abspath("//http://127.0.0.1/sample.json")
    #     # myfile = open(file, "r+").readlines()
    #     # myfile = open(r"http://127.0.0.1/index.html", "r+").readlines()
    #     # myfile = open("//home/loyal/Desktop/title.txt", "r")  # returns file handle
    #     # myfile.read()  # reading from the file
    #     # myfile.close()  # closing the file handle, to release the resources.
    #     s=[]
    #     # for line in myfile:
    #     fields = myfile['salary']
    #     fields = str(myfile['salary']).strip().split()
    #     s=fields
    #         # print(fields[0], fields[1], fields[2], fields[3])
    #     if s!=[]:
    #         return s[0]
    #     else:
    #         return



# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Product(models.Model):
    _inherit= 'product.product'
    
    addon_product = fields.Boolean(string='Is an add-on Product ?')



# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:



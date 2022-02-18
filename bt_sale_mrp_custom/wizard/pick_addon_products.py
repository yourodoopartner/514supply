# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PickAddonProductsWizard(models.TransientModel):
    _name= 'pick.addon.product.wizard'
    _description = 'Pick Add-on Product Wizard'
    
    @api.model
    def default_get(self, fields):
        result = super(PickAddonProductsWizard, self).default_get(fields)
        ctx = dict(self.env.context) or {}
        print (">>>>>>>>>>",ctx)
        if ctx.get('active_id', False):
            oder_line = self.env['sale.order.line'].browse(ctx.get('active_id', False))
            result['order_line_id'] = oder_line.id
            result['main_product_id'] = oder_line.product_id and oder_line.product_id.id or False
            result['name'] = oder_line.bom_ref
            prod_list = []
            for product_line in oder_line.addon_product_ids:
                prod_list.append((0,0, {'product_id': product_line.product_id.id, 
                                        'product_qty': product_line.product_qty}))
            result['addon_product_ids'] = prod_list
        return result
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line')
    main_product_id = fields.Many2one('product.product', string='Product')
    addon_product_ids = fields.One2many('pick.addon.product.wizard.line', 'addon_wizard_id', string='Add-on Products')
    name = fields.Char(string="Bom Reference")
    
    def action_pick_addon_products(self):
        for wizard in self:
            print (">>>>>>>>", wizard.addon_product_ids)
            addons_prod_list = []
            products = []
            addon_pool = self.env['sale.addon.product']
            for line in wizard.addon_product_ids:
                products.append(line.product_id.id)
                addon_line = addon_pool.search([('order_line_id','=',wizard.order_line_id.id),
                                                ('product_id','=',line.product_id.id)], limit=1)
                if addon_line: 
                    addon_line.product_qty = line.product_qty
                else:
                    addons_prod_list.append((0,0,{'product_id': line.product_id.id, 'product_qty': line.product_qty}))

            mission_addons = addon_pool.search([('order_line_id','=',wizard.order_line_id.id),('product_id','not in',products)])
            print (">>>>>addons_prod_list......",addons_prod_list, "mission_addons'''''''",mission_addons)
            mission_addons.unlink()
            wizard.order_line_id.bom_ref = wizard.name
#             wizard.order_line_id.addon_product_ids []
            wizard.order_line_id.addon_product_ids = addons_prod_list
            

class PickAddonProductsWizardLine(models.TransientModel):
    _name= 'pick.addon.product.wizard.line'
    _description = 'Pick Add-on Product Wizard Line'

    addon_wizard_id = fields.Many2one('pick.addon.product.wizard', string="Pick Add-on")
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string="Quantity per Unit", default=1)

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:






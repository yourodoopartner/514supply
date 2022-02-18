# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import ValidationError

class SaleAddonProducts(models.Model):
    _name= 'sale.addon.product'
    _description = 'Sale Add-on Products'
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line' , copy=False)
    product_id = fields.Many2one('product.product', string='Product', copy=False)
    product_qty = fields.Float(string="Quantity", default=1, copy=False)


class SaleOrderLine(models.Model):
    _inherit= 'sale.order.line'
    
    addon_product_ids = fields.One2many('sale.addon.product', 'order_line_id', string='Sale Add-on Products', copy=False)
    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials' , copy=False)
    mrp_id = fields.Many2one('mrp.production', string='MRP Production' , copy=False)
    bom_ref = fields.Char(string="Bom Reference", copy=False)
    
    def _get_addon_bom(self,):
        bom_pool = self.env['mrp.bom']
        bom_line_pool = self.env['mrp.bom.line']
        line_bom = False
        self.ensure_one()
        product_bom_objs = bom_pool.search(['|',('product_id','=',self.product_id.id),
                                                ('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
#             for addon_product in self.addon_product_ids:
        for bom in product_bom_objs:
            product_not_found = False
            for addon_product in self.addon_product_ids:
                lines = bom_line_pool.search([('bom_id', '=', bom.id),
                                              ('product_qty','=',addon_product.product_qty),
                                              ('product_id','=',addon_product.product_id.id)])
                if not lines:
                    product_not_found = True
                    continue
            if product_not_found:
                continue
            else:
                line_bom = bom
                break
        return line_bom
        
    def _prepare_bom_vals(self, product_bom):
        bom_pool = self.env['mrp.bom']
        bom_line_pool = self.env['mrp.bom.line']
        self.ensure_one()
        bom_lines = []
        for bom_line in product_bom.bom_line_ids:
            bom_lines.append((0,0, {
                'product_id': bom_line.product_id.id,
                'product_qty': bom_line.product_qty,
                }))
        for addon_product in self.addon_product_ids:
            bom_lines.append((0,0, {
                'product_id': addon_product.product_id.id,
                'product_qty': addon_product.product_qty,
                }))
        bom_vals = {
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'product_id': self.product_id.id,
            'product_qty': product_bom.product_qty,
            'code': product_bom.code,
            'type': 'normal',
            'bom_line_ids': bom_lines,
            'code': self.bom_ref,
            }
        return bom_vals
    
    def _create_mrp(self, bom):
        mrp_pool = self.env['mrp.production']
        mrp_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.product_uom_qty,
            'bom_id': bom.id,
            'product_uom_id': bom.product_uom_id and bom.product_uom_id.id,
            'date_planned_start': datetime.now(),
            
            }
        mrp = mrp_pool.create(mrp_vals)
        mrp._onchange_bom_id()
        mrp._onchange_date_planned_start()
        mrp._onchange_move_raw()
        mrp._onchange_move_finished_product()
        mrp._onchange_move_finished()
        mrp._onchange_move_finished()
        return mrp
        
                
class SaleOrder(models.Model):
    _inherit= 'sale.order'
    
    mrp_created = fields.Boolean(string="MRP Created", copy=False)
    
    def action_create_mrp(self):
        bom_pool = self.env['mrp.bom']
        for order in self:
            for line in order.order_line:
                if line.product_id:
                    product_bom = bom_pool.search(['|',('product_id','=',line.product_id.id),
                                                       ('product_tmpl_id','=',line.product_id.product_tmpl_id.id)], limit=1)
                    if not product_bom:
                        raise ValidationError(_('Configure Bill of materials for product %s', line.product_id.name))
                    if not line.addon_product_ids:
                        line_bom = product_bom
                    else:
                        line_bom = line._get_addon_bom()
                        if not line_bom:
                            bom_vals = line._prepare_bom_vals(product_bom)
                            line_bom = bom_pool.create(bom_vals)
                    line.bom_id = line_bom.id
                    mrp = line._create_mrp(line.bom_id)
                    line.mrp_id = mrp.id
            order.mrp_created = True
            
    def action_view_addons_mrp(self):
        mrp_ids = []
        for line in self.order_line:
            if line.mrp_id:
                mrp_ids.append(line.mrp_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        if len(mrp_ids) > 1:
            action['domain'] = [('id', 'in', mrp_ids)]
        elif len(mrp_ids) == 1:
            form_view = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = mrp_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
                

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

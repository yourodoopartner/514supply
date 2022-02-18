# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': '514 Sales MRP Customizations',
    'version': '0.01',
    'category': 'Sales',
    'summary': """514 Sales MRP Customizations""",
    'license':'LGPL-3',
    'description': """
     BoM Variants and the custom manufacturing process
""",
    'author' : 'Your odoo partner',
    'website' : 'http://yourodoopartner.com/',
    'depends': ['sale_mrp'],
    'images': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pick_addon_products_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml'
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True
}



# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

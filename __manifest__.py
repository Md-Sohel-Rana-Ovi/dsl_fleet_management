# -*- coding: utf-8 -*-
{
    'name': "dsl_fleet_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'fleet',
        'stock',
        'website',
        'sale_management',
        'multi_level_approval',
        'dsl_multi_level_approval_extension',
        'stock',
        'mail',
       
    ],

    # always loaded
    'data': [  
        ## Data
        'data/ir_sequence.xml',
        'data/approval_sequence.xml',

        ##views
        'security/ir.model.access.csv', 
        'views/dsl_maintenance_type.xml',  
        'views/dsl_maintenance_request_views.xml',
        'views/multi_approval_type_inherit_views.xml',
        'views/menu.xml',
        
        ##wizards  
        'wizards/dsl_maintenance_payment_wizards.xml',   
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

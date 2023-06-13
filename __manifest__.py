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
        'mail',

    ],

    # always loaded
    'data': [
        # Data
        'data/ir_sequence.xml',
        'data/approval_sequence.xml',

        # views
        'security/ir.model.access.csv',
        'views/dsl_maintenance_type.xml',
        'views/multi_approval_type_inherit_views.xml',
        'views/fleet_vehicle_views_extension.xml',
        'views/dsl_vehicle_purchase_views.xml',
        'views/dsl_fueling_request_views.xml',
        'views/dsl_accidental_case_views.xml',
        'views/menu.xml',

        # wizards
        'wizards/dsl_vehicle_payment_wizards.xml',
        # reports
        'reports/dsl_refueling_appeoval_report.xml',
        'reports/dsl_services_approval_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dsl_fleet_management/static/src/js/dashboard.js',
            'dsl_fleet_management/static/src/xml/dashboard.xml',
            'dsl_fleet_management/static/src/js/libs/Chart.bundle.js',
        ],
    
        'web.assets_frontend': [
          
        ],
        'web.assets_common': [

        ],  
    },
}

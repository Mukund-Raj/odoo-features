# -*- coding: utf-8 -*-
{
    'name': "Extra Control Panel Buttons",
    'summary': """Extra Control Panel Buttons""",
    'description': """
        Extra Control Panel Buttons like buttons just more than Edit/import
        """,

    'author': "Mukund Raj",
    'email': 'mukundraj.mr@gmail.com',
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical',
    'version': '13.1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml'
    ],
    'application': False,
    'installable': True
}

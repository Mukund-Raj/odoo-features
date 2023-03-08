{
    'name': "Odoo create button",
    'summary': """Odoo create button modification""",
    'description': """
        odoo create button modification
        """,

    'author': "Mukund Raj",
    'email': 'mukundraj.mr@gmail.com',
    'website': "",

    'category': 'Technical',
    'version': '13.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml'
    ],
    'application': False,
    'installable': True
}

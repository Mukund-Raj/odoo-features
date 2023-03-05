{
    'name': "Many2many field",
    'summary': """Many2many fields custom options""",
    'description': """
        1. Many2many add a line opens Form instead of search view
        """,

    'author': "Mukund Raj",
    'email': 'mukundraj.mr@gmail.com',
    'website': "",

    'category': 'Technical',
    'version': '13.1.0.0',

    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml'
    ],
    'application': False,
    'installable': True
}

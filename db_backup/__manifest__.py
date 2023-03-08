# -*- coding: utf-8 -*-
{
    'name': "DB Backup",
    'summary': """It will ensure daily backups for databases""",
    'description': """
        daily backups for database
        """,

    'author': "Mukund Raj",
    'email': 'mukundraj.mr@gmail.com',
    'website': "",

    'category': 'Backups',
    'version': '13.2.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/backup_cron.xml',
        'views/all_db_backups.xml',
        'views/backup_dbs.xml',
        'views/actions.xml',
        'views/menus.xml'
    ],
    'application': True,
    'installable': True
}

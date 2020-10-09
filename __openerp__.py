{
    'name': "Претензионно-исковая деятельность",

    'summary': """В соответствии с ...""",
    'author': "АО ВНИИЖТ",
    'website': "",
    'category': '',
    'version': '0.1',
    'depends': ['eco'],
    'data': [
        'assets.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/sud.xml',
        'views/menu.xml',
        'data/eco_pret_isk_problems_view_content.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
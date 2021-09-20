{
    'name' : 'Custom Account',
    'version' : '1.1',
    'summary': 'Account & Invoice',
    'sequence': 1,
    'description': "This Is A Account System Software",
    'category': 'payroll',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['sale', 'account', 'sale_stock', 'stock','base', 'mail'],
    'data': [
        'data/mail_template_view.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
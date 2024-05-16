# -*- coding: utf-8 -*-
{
    'name': 'HubSpot Integration',
    'version': '1.0',
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    'category': 'Extra Tools',
    'summary': "Synchronize data between Hubspot and Odoo",
    'description': "A product of Bac Ha Software allows to Synchronized data between Hubspot and Odoo, provides comprehensive solutions to email marketing and related problems.",
    'depends': ['base_setup', 'mail', 'mass_mailing', 'bhs_mass_mailing'],
    'module_type': 'official',
    'data': [
        'security/ir.model.access.csv',
        'data/cron_companies_data.xml',
        'data/cron_contact_data.xml',
        'data/cron_list_contact_hubspot_data.xml',
        'views/hubspot_companies_views.xml',
        'views/mailing_views.xml',
        'views/hubspot_syn_menu.xml',
        'views/res_config_settings_views.xml'
    ],
    'external_dependencies': {
        'python': ['simplejson', 'hubspot', 'hubspot-api-client']
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
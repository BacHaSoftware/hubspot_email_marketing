# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    hubspot_api_key = fields.Char(string="HubSpot API Key")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        hubspot_api_key = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key') or False

        res.update({
            'hubspot_api_key': hubspot_api_key
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("hubspot_api_key", self.hubspot_api_key)

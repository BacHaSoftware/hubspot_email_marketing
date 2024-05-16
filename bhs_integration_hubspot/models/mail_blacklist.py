# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import hubspot
from datetime import timedelta
import requests
import json

from datetime import datetime
from pprint import pprint
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException


class MailBlacklist(models.Model):

    _inherit = 'mail.blacklist'

    def unlink(self):
        res = super(MailBlacklist, self).unlink()
        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return res
        contact_url = "https://api.hubapi.com/contacts/v1/contact/email"
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }
        for line in self:
            try:
                res_hubspot_contact = requests.request("GET",
                                                       contact_url + "/" + str(line.email) + '/profile',
                                                       headers=headers)
                hubspot_contact = res_hubspot_contact.json()
                requests.request("DELETE", 'https://api.hubapi.com/contacts/v1/contact/vid/' + str(hubspot_contact.get('vid')),
                                                       headers=headers)
            except Exception as e:
                print("Exception when calling update contact: %s\n" % e)

        return res

    def write(self, vals):
        res = super(MailBlacklist, self).write(vals)
        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return res
        contact_url = "https://api.hubapi.com/contacts/v1/contact/email"
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }

        for blacklist in self:
            # add blacklist
            print(str(blacklist.active))
            if blacklist.active:
                # update contact Lead status là unqualified
                params = {
                    "properties": [{"property": "hs_lead_status", "value": "UNQUALIFIED"}]
                }

                # list_unqualified_contacts.append(blacklist.email)
            #remove blacklist
            else:
                # update contact Lead status là new
                params = {
                    "properties": [{"property": "hs_lead_status", "value": "NEW"}]
                }
                # list_new_contacts.append(blacklist.email)

            try:
                res_hubspot_contact = requests.request("POST",
                                                       contact_url + "/" + str(blacklist.email) + '/profile',
                                                       headers=headers, data=json.dumps(params))
                print('***Update email %s: %d' % (str(blacklist.email),res_hubspot_contact.status_code))
            except Exception as e:
                print("Exception when calling update contact: %s\n" % e)
        return res

    def add_unqualified_contacts_to_hubspot(self, days=0):
        migration_start = datetime.now()
        print(f'Start add_unqualified_contacts_to_hubspot at {migration_start}')

        domain_odoo_blacklist = []
        if days > 0:
            end_date = fields.Datetime.now()
            start_date = end_date - timedelta(days=days)
            domain_odoo_blacklist = [('create_date', '>=', start_date), ('create_date', '<=', end_date)]

        odoo_blacklist = self.env['mail.blacklist'].sudo().search(domain_odoo_blacklist)
        list_odoo_blacklist = odoo_blacklist.mapped('email')
        list_hubspot_blacklist = []
        print('*** list_odoo_blacklist')
        print(len(list_odoo_blacklist))

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if not HUBSPOT_ACCESS_TOKEN or HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return
        hubspot_api = hubspot.Client.create(access_token=HUBSPOT_ACCESS_TOKEN)

        if len(list_odoo_blacklist) > 0:
            start_index = 0
            while start_index < len(list_odoo_blacklist):
                batch = list_odoo_blacklist[start_index:start_index + 100]
                # print(batch)
                filter_groups = [
                    {
                        "filters": [
                            {
                                "values": batch,
                                "propertyName": "email",
                                "operator": "IN"
                            },
                            {
                                "value": "UNQUALIFIED",
                                "propertyName": "hs_lead_status",
                                "operator": "EQ"
                            }
                        ]
                    }
                ]

                public_object_search_request = PublicObjectSearchRequest(
                    filter_groups=filter_groups, limit=100
                )

                try:
                    api_response = hubspot_api.crm.contacts.search_api.do_search(
                        public_object_search_request=public_object_search_request)
                    # print(api_response)
                    for res in api_response.results:
                        list_hubspot_blacklist.append(res.properties.get("email"))
                    start_index += 100
                except ApiException as e:
                    print("Exception when calling search_api->do_search: %s\n" % e)

        # lọc các contact chưa có
        # add_unqualified_contacts = [x for x in list_odoo_blacklist if x not in set(list_hubspot_blacklist)]
        add_unqualified_contacts = []
        for element in list_odoo_blacklist:
            if element not in list_hubspot_blacklist:
                add_unqualified_contacts.append(element)

        print('*** list_hubspot_blacklist')
        print(len(list_hubspot_blacklist))

        print('*** add_unqualified_contacts')
        print(add_unqualified_contacts)

        if len(add_unqualified_contacts) > 0:
            start_index_add = 0
            while start_index_add < len(add_unqualified_contacts):
                batch_add = add_unqualified_contacts[start_index_add:start_index_add + 100]
                # tạo mới contact hubspot
                arr_add_unqualified = []
                for email_unqualified in batch_add:
                    arr_add_unqualified.append(
                        {"properties": {"hs_lead_status": "UNQUALIFIED", "email": email_unqualified}})

                try:
                    # thêm contact ở hubspot
                    if arr_add_unqualified:
                        batch_input_simple_public_object_input_for_create = {"inputs": arr_add_unqualified}
                        hubspot_api.crm.contacts.batch_api.create(
                            batch_input_simple_public_object_input_for_create=batch_input_simple_public_object_input_for_create
                        )
                except ApiException as e:
                    print("Exception when calling batch_api --> create: %s\n" % e)

                start_index_add += 100
                print(f'***Add contacts: Start index: {start_index_add}')

        print(f'***Total contacts add migration: {len(add_unqualified_contacts)}')
        print(f'End add_unqualified_contacts_to_hubspot, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    def unqualified_contact_in_hubspot(self, days=0):
        migration_start = datetime.now()
        print(f'Start migrating blacklist contact from Odoo to Hubspot at {migration_start}')

        domain_odoo_blacklist = []
        if days > 0:
            end_date = fields.Datetime.now()
            start_date = end_date - timedelta(days=days)
            domain_odoo_blacklist = [('create_date', '>=', start_date), ('create_date', '<=', end_date)]

        odoo_blacklist = self.env['mail.blacklist'].sudo().search(domain_odoo_blacklist)
        # print(odoo_blacklist)
        list_odoo_blacklist = odoo_blacklist.mapped('email')
        list_hubspot_blacklist = []

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if not HUBSPOT_ACCESS_TOKEN or HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return
        hubspot_api = hubspot.Client.create(access_token=HUBSPOT_ACCESS_TOKEN)

        # print(len(list_odoo_blacklist))
        if len(list_odoo_blacklist) > 0:
            # *** CẬP NHẬT NHỮNG CONTACT ĐÃ CÓ
            start_index = 0
            while start_index < len(list_odoo_blacklist):
                batch = list_odoo_blacklist[start_index:start_index + 100]

                filter_groups = [
                    {
                        "filters": [
                            {
                                "values": batch,
                                "propertyName": "email",
                                "operator": "IN"
                            },
                            {
                                "value": "UNQUALIFIED",
                                "propertyName": "hs_lead_status",
                                "operator": "NEQ"
                            }
                        ]
                    }
                ]

                public_object_search_request = PublicObjectSearchRequest(
                    filter_groups=filter_groups, limit=100
                )
                try:
                    api_response = hubspot_api.crm.contacts.search_api.do_search(
                        public_object_search_request=public_object_search_request)
                    arr_update = []
                    for res in api_response.results:
                        arr_update.append({"id": res.id, "properties": {"hs_lead_status": "UNQUALIFIED"}})
                        list_hubspot_blacklist.append(res.properties.get("email"))

                    # CẬP NHẬT CONTACTS HUBSPOT
                    if arr_update:
                        batch_input_simple_public_object_batch_input = {"inputs": arr_update}
                        hubspot_api.crm.contacts.batch_api.update(
                            batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input
                        )
                    # #tạo mới contact hubspot
                    # add_unqualified_contacts = [x for x in list_odoo_blacklist if x not in set(list_hubspot_blacklist)]
                except ApiException as e:
                    print("Exception when calling search_api->do_search: %s\n" % e)

                start_index += 100
                print(f'***Update contacts: Start index: {start_index}')

        # THÊM CONTACT UNQUALIFIED VÀO HUBSPOT
        self.add_unqualified_contacts_to_hubspot(days)
        print(f'End migrating blacklist contact from Odoo to Hubspot, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")


# class MailingList(models.Model):
#     _inherit = 'mailing.list'
#
#     id_list_hubspot = fields.Char(string="ID List Hubspot")
#     def sync_list_contact_hubspot_odoo(self):
#         ir_config = self.env['ir.config_parameter'].sudo()
#         param_list = "?count=100&offset=0"
#         # list_url = "https://api.hubapi.com/contacts/v1/lists"
#         list_url = ir_config.get_param('hubspot_api') + ir_config.get_param('hubspot_api_get_list')
#         YOUR_ACCESS_TOKEN = ir_config.get_param('hubspot_api_key')
#         headers = {
#             'content-type': 'application/json',
#             'authorization': 'Bearer %s' % YOUR_ACCESS_TOKEN
#         }
#         res_list = requests.request("GET", list_url + param_list, headers=headers)
#         lists = res_list.json().get('lists')
#         mailing_lists = self.env['mailing.list'].sudo().search([])
#         name_mailing_list = [ml.name for ml in mailing_lists]
#         hubspot_lists_name = [l for l in lists if l.get('name') not in name_mailing_list]
#         list_vals = []
#         for hub in hubspot_lists_name:
#             vals = {
#                 'name': hub.get('name'),
#                 'id_list_hubspot': hub.get('listId'),
#             }
#             list_vals.append(vals)
#         self.env['mailing.list'].sudo().create(list_vals)
#         #Contacts in list hubspot
#         hubspot_lists_name_lastest = [l for l in lists if datetime.fromtimestamp(l.get('updatedAt')/1000) >= datetime.now()-timedelta(days=3)]
#         param_contact = "?count=1000"
#         if hubspot_lists_name_lastest:
#             for hub_lastest in hubspot_lists_name_lastest:
#                 contact_url = "https://api.hubapi.com/contacts/v1/lists/%s/contacts/all" %hub_lastest.get('listId')
#                 contact_url = ir_config.get_param('hubspot_api') + ir_config.get_param('hubspot_api_get_contact') %hub_lastest.get('listId')
#                 res_contact = requests.request("GET", contact_url+param_contact, headers=headers)
#                 contacts = res_contact.json().get('contacts')
#                 contact_vals = []
#                 for contact in contacts:
#                     if datetime.fromtimestamp(contact.get('addedAt')/1000) >= datetime.now()-timedelta(days=2):
#                         list_contact = self.env['mailing.list'].sudo().search([('id_list_hubspot', '=', hub_lastest.get('listId'))])
#                         vals = {
#                             'name': contact.get('properties').get('firstname').get('value'),
#                             'email': contact.get('identity-profiles')[0]['identities'][0]['value'],
#                             'list_ids': [(4, list_contact.id)]
#                             }
#                         if contact.get('properties').get('company'):
#                             vals['company_name'] = contact.get('properties').get('company').get('value')
#                         # self.env['mailing.contact'].sudo().create(vals)
#                         contact_vals.append(vals)
#                 print(contact_vals)
#                 self.env['mailing.contact'].sudo().create(contact_vals)


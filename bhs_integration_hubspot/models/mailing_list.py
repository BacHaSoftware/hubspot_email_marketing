# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import hubspot
import requests

from datetime import datetime, timedelta
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException

from pprint import pprint


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    state_name = fields.Char('State')
    industry_name = fields.Char('Industry', compute='_compute_industry_name', store=True)
    hubspot_companyID = fields.Char('Hubspot CompanyID')
    hubspot_company_related = fields.Many2one('hubspot.companies', 'Hubspot company related')
    linkedIn_URL = fields.Char('LinkedIn URL')

    @api.depends('hubspot_companyID', 'company_name', 'hubspot_company_related.industry_name')
    def _compute_industry_name(self):
        for contact in self:
            contact.hubspot_company_related = False
            contact.industry_name = ''
            if contact.hubspot_companyID != '':
                hubspot_company = self.env['hubspot.companies'].sudo().search(
                    [('id_companies_hubspot', '=', contact.hubspot_companyID)])
                if hubspot_company:
                    contact.hubspot_company_related = hubspot_company.id

                if hubspot_company and hubspot_company.industry_name:
                    contact.industry_name = hubspot_company.industry_name


class MailingList(models.Model):
    _inherit = 'mailing.list'

    id_list_hubspot = fields.Char(string="ID List Hubspot")

    # def sync_list_contact_hubspot_odoo(self, days=0):
    #     if days >= 0:
    #         end_date = fields.Datetime.now()
    #         start_date = end_date - timedelta(days=days)
    #         sdate = str(int(round(start_date.timestamp() * 1000)))
    #
    #         HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
    #         hubspot_api = hubspot.Client.create(access_token=HUBSPOT_ACCESS_TOKEN)
    #
    #         after = 0
    #         flag = True
    #         while(flag):
    #             public_object_search_request = PublicObjectSearchRequest(
    #                 filter_groups=[
    #                     {
    #                         "filters": [
    #                             {
    #                                 "value": 1373001,
    #                                 "propertyName": "list_id",
    #                                 "operator": "EQ"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 properties=["hs_lead_status","firstname","lastname","company","email","object_lists"],
    #                 limit=100, after=after
    #             )
    #
    #             try:
    #                 # print('---START API HUBSPOT')
    #                 api_response = hubspot_api.crm.contacts.search_api.do_search(
    #                     public_object_search_request=public_object_search_request)
    #                 print(api_response)
    #                 pprint(api_response)
    #                 break
    #
    #                 after += 100
    #                 arr_update = []
    #                 for res in api_response.results:
    #                     arr_update.append({"email": res.properties['email']})
    #
    #                 print(arr_update)
    #                 print(len(arr_update))
    #
    #                 if len(arr_update) <= 100:
    #                     flag = False
    #                     break
    #
    #                 # if arr_update:
    #                 #     batch_input_simple_public_object_batch_input = {"inputs": arr_update}
    #                 #     hubspot_api.crm.contacts.batch_api.update(
    #                 #         batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input
    #                 #     )
    #                 #     print('---DONE UPDATE HUBSPOT')
    #                 # print('--DONE API HUBSPOT')
    #             except ApiException as e:
    #                 flag = False
    #                 print("Exception when calling search_api->do_search: %s\n" % e)

    # ĐỒNG BỘ DANH SÁCH LIST
    def sync_list_hubspot_odoo(self, offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot list at {migration_start}')

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return

        list_url = "https://api.hubapi.com/contacts/v1/lists"
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }

        offset = offset
        total_list = 0
        flag = True

        while flag:
            params = {
                "count": 100,
                "offset": offset
            }

            res_hubspot_list = requests.request("GET", list_url, headers=headers, params=params)
            hubspot_lists = res_hubspot_list.json()

            for l in hubspot_lists.get('lists'):
                if l.get('listType') == 'STATIC' or l.get('name') == 'Blacklist':
                    # ĐỒNG BỘ DATA LISTS
                    odoo_mailing_lists_update = self.env['mailing.list'].sudo().search(
                        ['|', ('id_list_hubspot', '=', l.get('listId')), ('name', '=', l.get('name'))])
                    if odoo_mailing_lists_update:
                        odoo_mailing_lists_update.write(
                            {'name': l.get('name'), 'id_list_hubspot': l.get('listId')})
                    else:
                        vals = {
                            'name': l.get('name'),
                            'id_list_hubspot': l.get('listId'),
                        }
                        self.env['mailing.list'].sudo().create(vals)

                    total_list += 1

            offset = hubspot_lists.get('offset')
            if not hubspot_lists.get('has-more'):
                flag = False
                break

        print(f'***Total lists migration: {total_list}')
        print(f'End migrating hubspot list, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    def sync_list_remove_hubspot_odoo(self, offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot list at {migration_start}')

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return

        list_url = "https://api.hubapi.com/contacts/v1/lists"
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }

        offset = offset
        total_list = 0
        flag = True
        list_hubspot_ids = []

        while flag:
            params = {
                "count": 100,
                "offset": offset
            }

            res_hubspot_list = requests.request("GET", list_url, headers=headers, params=params)
            hubspot_lists = res_hubspot_list.json()

            for l in hubspot_lists.get('lists'):
                if l.get('listType') == 'STATIC' or l.get('name') == 'Blacklist':
                    list_hubspot_ids.append(l.get('listId'))

            offset = hubspot_lists.get('offset')
            if not hubspot_lists.get('has-more'):
                flag = False
                break

        if len(list_hubspot_ids) > 0:
            list_id_in_odoo = self.env['mailing.list'].sudo().search([('id_list_hubspot', '>', 0)])
            vals_list_remove = [vals.id for vals in list_id_in_odoo if int(vals.id_list_hubspot) not in list_hubspot_ids]

            if vals_list_remove:
                self.env['mailing.list'].sudo().browse(vals_list_remove).unlink()

        print(f'***Total lists hubspot remove in odoo: {total_list}')
        print(f'End migrating hubspot list removed, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    # ĐỒNG BỘ DANH SÁCH contacts by list_id
    def sync_contacts_by_list_hubspot_odoo(self, list_id=0, vid_offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot contact by list_id at {migration_start}')

        if int(list_id) > 0:
            HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
            if HUBSPOT_ACCESS_TOKEN == '':
                print('Not found HUBSPOT_ACCESS_TOKEN config')
                return

            list_url = "https://api.hubapi.com/contacts/v1/lists"
            headers = {
                'content-type': 'application/json',
                'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
            }

            odoo_mailing_lists_update = self.env['mailing.list'].sudo().search(
                [('id_list_hubspot', '=', list_id)])

            total_contact = 0
            vid_offset = vid_offset
            flag_contact = True

            while flag_contact:
                params = {
                    "count": 100,
                    "vidOffset": vid_offset,
                    "property": ['hs_lead_status', 'email', 'company', 'firstname', 'lastname', 'jobtitle', 'country', 'state', 'industry', 'associatedcompanyid', 'linkedin_url'],
                }

                res_hubspot_contact = requests.request("GET",
                                                       list_url + "/" + str(list_id) + '/contacts/all',
                                                       headers=headers, params=params)
                hubspot_list_contacts = res_hubspot_contact.json()
                # print(len(hubspot_list_contacts.get('contacts')))
                print('vidOffset: %d' % vid_offset)

                for c in hubspot_list_contacts.get('contacts'):
                    firstname = c.get('properties').get('firstname').get('value') if c.get('properties').get(
                        'firstname') else ''
                    lastname = c.get('properties').get('lastname').get('value') if c.get('properties').get(
                        'lastname') else ''
                    email = c.get('properties').get('email').get('value') if c.get('properties').get('email') else ''
                    company_name = c.get('properties').get('company').get('value') if c.get('properties').get(
                        'company') else ''
                    industry_name = c.get('properties').get('industry').get('value') if c.get('properties').get(
                        'industry') else ''
                    state_name = c.get('properties').get('state').get('value') if c.get('properties').get(
                        'state') else ''
                    hubspot_companyID = c.get('properties').get('associatedcompanyid').get('value') if c.get('properties').get(
                        'associatedcompanyid') else ''
                    linkedin_url = c.get('properties').get('linkedin_url').get('value') if c.get('properties').get(
                        'linkedin_url') else ''

                    chk_contact = self.env['mailing.contact'].sudo().search(
                        [('email', '=', email)], limit=1)

                    # nếu status ko là UNQUALIFIED thì cập nhật contact data
                    if c.get('properties').get('hs_lead_status') and c.get('properties').get('hs_lead_status').get(
                            'value') == 'UNQUALIFIED':
                        if not chk_contact.email:
                            self.env['mail.blacklist'].sudo()._add(email)
                        else:
                            chk_contact.add_to_blacklist()
                            chk_contact.remove_blacklist_contacts([email])
                    # UNQUALIFIED THÌ CẬP NHẬT BLACKLIST VÀ XÓA CONTACT KHỎI LIST
                    else:
                        vals = {
                            'name': '%s %s' % (firstname, lastname),
                            'email': email,
                            'company_name': company_name,
                            'industry_name': industry_name,
                            'state_name': state_name,
                            'hubspot_companyID': hubspot_companyID,
                            'linkedIn_URL': linkedin_url,
                            'list_ids': [(6, 0, [odoo_mailing_lists_update.id])]
                        }

                        # Nếu trong danh sách đã kết nối thì không cập nhật list_ids
                        contacted_contacts = self.env['mailing.contact.contacted'].sudo().search([('email', '=', email)])
                        if contacted_contacts:
                            vals.pop('list_ids')

                        if c.get('properties').get('jobtitle'):
                            job_title = self.env['res.partner.title'].sudo().search(
                                [('name', '=', c.get('properties').get('jobtitle').get('value'))], limit=1)
                            if job_title:
                                title_id = job_title.id
                            else:
                                title_id = self.env['res.partner.title'].sudo().create(
                                    {'name': c.get('properties').get('jobtitle').get('value')}).id

                            vals['title_id'] = title_id

                        if c.get('properties').get('country'):
                            country_name = self.env['res.country'].sudo().search(
                                [('name', '=', c.get('properties').get('country').get('value'))], limit=1)
                            if country_name:
                                country_id = country_name.id
                                vals['country_id'] = country_id
                            else:
                                print('*** No country name: %s' % c.get('properties').get('country').get('value'))
                                # break

                        if chk_contact:
                            chk_contact.write(vals)
                        else:
                            self.env['mailing.contact'].sudo().create(vals)

                print("Hubspot List ID: %d" % list_id)

                total_contact += len(hubspot_list_contacts.get('contacts'))
                print("*** Migrated: %d records" % total_contact)
                print("--------------------------------------------------")

                vid_offset = hubspot_list_contacts.get('vid-offset')
                # print(vid_offset)

                if not hubspot_list_contacts.get('has-more'):
                    flag_contact = False
                    break

        print(f'End migrating hubspot contacts by list_id, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    #syn contact daily
    def sync_list_contact_hubspot_odoo_daily(self, days=1, vid_offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot lists and contacts at {migration_start}')

        if days > 0:
            end_date = fields.Datetime.now()
            start_date = (end_date - timedelta(days=days))
            sdate = int(round(start_date.timestamp() * 1000))
            print(f'Migrating from {start_date}')
            print(f'{sdate}')

            HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
            if HUBSPOT_ACCESS_TOKEN == '':
                print('Not found HUBSPOT_ACCESS_TOKEN config')
                return

            list_url = "https://api.hubapi.com/contacts/v1/lists"
            headers = {
                'content-type': 'application/json',
                'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
            }

            # ĐỒNG BỘ DANH SÁCH LIST
            self.sync_list_hubspot_odoo()

            list_mapping = self.env['mailing.list'].sudo().search([('id_list_hubspot', '!=', False)])
            id_list_mapping = dict(zip(list_mapping.mapped('id_list_hubspot'), list_mapping.mapped('id')))
            # print(id_list_mapping)

            # ĐỒNG BỘ DATA CONTACTS
            total_contact = 0
            vid_offset = vid_offset
            flag_contact = True
            time_offset = sdate

            while flag_contact:
                params = {
                    "count": 100,
                    "vidOffset": vid_offset,
                    # "timeOffset": time_offset,
                    "showListMemberships": 'true',
                    "property": ['hs_lead_status', 'email', 'company', 'firstname', 'lastname', 'jobtitle', 'country', 'state', 'industry', 'associatedcompanyid', 'linkedin_url'],
                }

                res_hubspot_contact = requests.request("GET", list_url + '/recently_updated/contacts/recent', headers=headers, params=params)
                hubspot_list_contacts = res_hubspot_contact.json()
                # print(hubspot_list_contacts)
                # print(len(hubspot_list_contacts.get('contacts')))
                # break
                # print('vidOffset: %d' % vid_offset)
                print('timeOffset: %d' % time_offset)

                for c in hubspot_list_contacts.get('contacts'):
                    # contact đã có list membership
                    if c.get('list-memberships') and len(c.get('list-memberships')) > 0:
                        hp_list_id = c.get('list-memberships')[0].get('static-list-id')

                        firstname = c.get('properties').get('firstname').get('value') if c.get('properties').get(
                            'firstname') else ''
                        lastname = c.get('properties').get('lastname').get('value') if c.get('properties').get(
                            'lastname') else ''
                        email = c.get('properties').get('email').get('value') if c.get('properties').get('email') else ''
                        company_name = c.get('properties').get('company').get('value') if c.get('properties').get(
                            'company') else ''
                        industry_name = c.get('properties').get('industry').get('value') if c.get('properties').get(
                            'industry') else ''
                        state_name = c.get('properties').get('state').get('value') if c.get('properties').get(
                            'state') else ''
                        hubspot_companyID = c.get('properties').get('associatedcompanyid').get('value') if c.get(
                            'properties').get(
                            'associatedcompanyid') else ''
                        linkedin_url = c.get('properties').get('linkedin_url').get('value') if c.get('properties').get(
                            'linkedin_url') else ''

                        chk_contact = self.env['mailing.contact'].sudo().search(
                            [('email', '=', email)], limit=1)

                        # nếu status là UNQUALIFIED: CẬP NHẬT BLACKLIST VÀ XÓA CONTACT KHỎI LIST
                        if c.get('properties').get('hs_lead_status') and c.get('properties').get('hs_lead_status').get(
                                'value') == 'UNQUALIFIED':
                            if not chk_contact.email:
                                self.env['mail.blacklist'].sudo()._add(email)
                            else:
                                chk_contact.add_to_blacklist()
                                chk_contact.remove_blacklist_contacts([email])
                        # status khác UNQUALIFIED THÌ TẠO MỚI HOẶC CẬP NHẬT CONTACTS
                        else:
                            # if datetime.fromtimestamp(
                            #         int(c.get('properties').get('lastmodifieddate').get('value')) / 1000) >= start_date:
                            list_ids = [id_list_mapping[str(hp_list_id)]] if str(hp_list_id) in id_list_mapping else []

                            vals = {
                                'name': '%s %s' % (firstname, lastname),
                                'email': email,
                                'company_name': company_name,
                                'industry_name': industry_name,
                                'state_name': state_name,
                                'hubspot_companyID': hubspot_companyID,
                                'linkedIn_URL': linkedin_url,
                                # 'list_ids': [(6, 0, list_ids)]
                            }

                            # Nếu có data list_ids thì mới cập nhật list:
                            if len(list_ids) > 0:
                                vals['list_ids'] = [(6, 0, list_ids)]

                            # Nếu trong danh sách đã kết nối thì không cập nhật list_ids
                            contacted_contacts = self.env['mailing.contact.contacted'].sudo().search(
                                [('email', '=', email)])
                            if contacted_contacts:
                                vals.pop('list_ids')

                            if c.get('properties').get('jobtitle'):
                                job_title = self.env['res.partner.title'].sudo().search(
                                    [('name', '=', c.get('properties').get('jobtitle').get('value'))], limit=1)
                                if job_title:
                                    title_id = job_title.id
                                else:
                                    title_id = self.env['res.partner.title'].sudo().create(
                                        {'name': c.get('properties').get('jobtitle').get('value')}).id

                                vals['title_id'] = title_id

                            if c.get('properties').get('country'):
                                country_name = self.env['res.country'].sudo().search(
                                    [('name', '=', c.get('properties').get('country').get('value'))], limit=1)
                                if country_name:
                                    country_id = country_name.id
                                    vals['country_id'] = country_id
                                else:
                                    print('*** No country name: %s' % c.get('properties').get('country').get('value'))

                            if chk_contact:
                                chk_contact.write(vals)
                            else:
                                self.env['mailing.contact'].sudo().create(vals)

                        total_contact += 1


                vid_offset = hubspot_list_contacts.get('vid-offset')
                time_offset = hubspot_list_contacts.get('time-offset')
                print("* time-offset: %s" % str(time_offset))
                print("* vid-offset: %s" % str(vid_offset))
                print("* has-more: %s" % str(hubspot_list_contacts.get('has-more')))

                print("*** Migrated contacts: %d records" % total_contact)
                print("--------------------------------------------------")

                if not hubspot_list_contacts.get('has-more'):
                    flag_contact = False
                    print("*** BREAK Migrated contacts --")
                    break
                else:
                    if time_offset > 0 and time_offset < sdate:
                        flag_contact = False
                        print("*** BREAK Migrated contacts --")
                        break

        print(f'End migrating hubspot lists and contacts, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    # syn deleted contact from hubspot to odoo
    def sync_deleted_contact_hubspot_odoo(self, after=''):
        migration_start = datetime.now()
        print(f'Start migrating deleted contact from hubspot to odoo at {migration_start}')
        print(f'Migrating from {fields.Datetime.now()}')

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return

        hubspot_url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }

        # ĐỒNG BỘ DATA ARCHIVED CONTACTS
        total_contact = 0
        total_update_contact = 0
        flag_contact = True

        while flag_contact:
            params = {
                "limit": 100,
                "archived": 'true',
                "property": ['email', 'hs_lastmodifieddate', 'archivedAt'],
            }

            if after != '':
                params['after'] = after

            res_hubspot_deleted_contact = requests.request("GET", hubspot_url,
                                                   headers=headers, params=params)
            hubspot_list_contacts = res_hubspot_deleted_contact.json()
            contacted_contact = self.env['mailing.contact.contacted'].search([])

            after = str(hubspot_list_contacts.get('paging').get('next').get('after')) if hubspot_list_contacts.get('paging') else ''
            email_archived = [c.get('properties').get('email') for c in hubspot_list_contacts.get('results') if (c.get('properties').get('email') and c.get('properties').get('email') not in contacted_contact.mapped('email'))]

            # search contact by email_archived in odoo
            if len(email_archived) > 0:
                archived_contacts = self.env['mailing.contact'].sudo().search(
                    [('email', 'in', email_archived)])
                # xóa contact trên odoo
                if archived_contacts:
                    archived_contacts.unlink()
                    total_update_contact += len(email_archived)

                total_contact += len(email_archived)

            print("*** Total archived contacts: %d records" % total_contact)
            print("*** Migrated archived contacts: %d records" % total_update_contact)
            print("--------------------------------------------------")

            print("* after: %s" % after)
            if after == '':
                flag_contact = False
                print("*** BREAK Migrate archived contacts --")
                break
            print("--------------------------------------------------")


        print(f'End migrating hubspot archived contacts, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

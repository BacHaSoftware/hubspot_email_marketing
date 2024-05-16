# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import hubspot
import requests

from datetime import datetime, timedelta
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from time import sleep


class HubspotCompanies(models.Model):
    _name = 'hubspot.companies'
    _description = "Hubspot companies"

    name = fields.Char('Name')
    domain = fields.Char('Domain')
    country = fields.Char('Country')
    state = fields.Char('State')
    city = fields.Char('City')
    website = fields.Char('Website')
    description = fields.Char('Description')
    phone = fields.Char('Phone')
    industry_name = fields.Char('Industry')
    numberofemployees = fields.Integer('Number of employees')
    id_companies_hubspot = fields.Char('Hubspot CompanyID')
    linkedin_company_page = fields.Char('LinkedIn Company page')
    contacts_related = fields.One2many(
        "mailing.contact", "hubspot_company_related", "Mailing Contacts Related", help="Mailing Contacts Related"
    )

    # ĐỒNG BỘ DANH SÁCH COMPANY TỪ HUBSPOT
    def sync_companies_hubspot_odoo(self, offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot list at {migration_start}')

        HUBSPOT_ACCESS_TOKEN = self.env['ir.config_parameter'].sudo().get_param('hubspot_api_key')
        if HUBSPOT_ACCESS_TOKEN == '':
            print('Not found HUBSPOT_ACCESS_TOKEN config')
            return

        list_url = "https://api.hubapi.com/companies/v2/companies/paged"
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
        }

        offset = offset
        total_companies = 0
        flag = True

        while flag:
            sleep(2)
            params = {
                "limit": 100,
                "offset": offset,
                "properties": ['name', 'industry','hs_lastmodifieddate', 'domain', 'country', 'city', 'description', 'numberofemployees','phone','state','hs_object_id','website', 'linkedin_company_page'],
            }

            res_hubspot_companies = requests.request("GET", list_url, headers=headers, params=params)
            hubspot_companies = res_hubspot_companies.json()

            for c in hubspot_companies.get('companies'):
                # ĐỒNG BỘ DATA COMPANIES
                h_companyID = c.get('companyId')
                h_companyName = c.get('properties').get('name').get('value') if c.get('properties').get('name') else ''
                h_companyIndustry = c.get('properties').get('industry').get('value') if c.get('properties').get('industry') else ''
                hs_lastmodifieddate = c.get('properties').get('hs_lastmodifieddate').get('value') if c.get('properties').get('hs_lastmodifieddate') else 0
                domain = c.get('properties').get('domain').get('value') if c.get('properties').get('domain') else ''
                country = c.get('properties').get('country').get('value') if c.get('properties').get('country') else ''
                state = c.get('properties').get('state').get('value') if c.get('properties').get('state') else ''
                city = c.get('properties').get('city').get('value') if c.get('properties').get('city') else ''
                website = c.get('properties').get('website').get('value') if c.get('properties').get('website') else ''
                description = c.get('properties').get('description').get('value') if c.get('properties').get('description') else ''
                phone = c.get('properties').get('phone').get('value') if c.get('properties').get('phone') else ''
                numberofemployees = c.get('properties').get('numberofemployees').get('value') if c.get('properties').get('numberofemployees') else 0
                linkedin_company_page = c.get('properties').get('linkedin_company_page').get('value') if c.get('properties').get('linkedin_company_page') else ''

                if h_companyIndustry != '':
                    h_companyIndustry = h_companyIndustry.replace("_", " ")

                odoo_companies_update = self.env['hubspot.companies'].sudo().search(
                    [('id_companies_hubspot', '=', h_companyID)])

                vals = {
                    'name': h_companyName,
                    'domain': domain,
                    'country': country,
                    'state': state,
                    'city': city,
                    'website': website,
                    'description': description,
                    'phone': phone,
                    'linkedin_company_page': linkedin_company_page,
                    'numberofemployees': numberofemployees,
                    'industry_name': h_companyIndustry
                }

                if odoo_companies_update:
                    odoo_companies_update.write(vals)
                else:
                    vals["id_companies_hubspot"] = h_companyID
                    self.env['hubspot.companies'].sudo().create(vals)

                total_companies += 1

            offset = hubspot_companies.get('offset')
            print(offset)
            print(f'***Migrated: {total_companies}')
            # if total_companies > 31700:
            #     break
            if not hubspot_companies.get('has-more'):
                flag = False
                break

        print(f'***Total companies migration: {total_companies}')
        print(f'End migrating hubspot companies, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")

    # syn companies daily
    def sync_companies_hubspot_odoo_daily(self, days=1, vid_offset=0):
        migration_start = datetime.now()
        print(f'Start migrating hubspot companies at {migration_start}')

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

            companies_url = "https://api.hubapi.com/companies/v2/companies/recent/modified"
            headers = {
                'content-type': 'application/json',
                'authorization': 'Bearer %s' % HUBSPOT_ACCESS_TOKEN
            }

            # ĐỒNG BỘ DATA CONTACTS
            total_contact = 0
            vid_offset = vid_offset
            flag_contact = True
            time_offset = sdate

            while flag_contact:
                params = {
                    "count": 100,
                    "offset": vid_offset,
                    "since": time_offset,
                    "property": ['hs_lead_status', 'email', 'company', 'firstname', 'lastname', 'jobtitle',
                                 'country', 'state', 'industry','linkedin_company_page'],
                }

                res_hubspot_companies = requests.request("GET", companies_url,
                                                       headers=headers, params=params)
                hubspot_companies = res_hubspot_companies.json()
                # print(hubspot_companies)
                # print(len(hubspot_list_contacts.get('contacts')))
                # break
                print('vidOffset: %d' % vid_offset)
                print('timeOffset: %d' % time_offset)

                for c in hubspot_companies.get('results'):
                    # ĐỒNG BỘ DATA COMPANIES
                    h_companyID = c.get('companyId')
                    h_companyName = c.get('properties').get('name').get('value') if c.get('properties').get(
                        'name') else ''
                    h_companyIndustry = c.get('properties').get('industry').get('value') if c.get('properties').get(
                        'industry') else ''
                    hs_lastmodifieddate = c.get('properties').get('hs_lastmodifieddate').get('value') if c.get(
                        'properties').get('hs_lastmodifieddate') else 0
                    domain = c.get('properties').get('domain').get('value') if c.get('properties').get('domain') else ''
                    country = c.get('properties').get('country').get('value') if c.get('properties').get(
                        'country') else ''
                    state = c.get('properties').get('state').get('value') if c.get('properties').get('state') else ''
                    city = c.get('properties').get('city').get('value') if c.get('properties').get('city') else ''
                    website = c.get('properties').get('website').get('value') if c.get('properties').get(
                        'website') else ''
                    description = c.get('properties').get('description').get('value') if c.get('properties').get(
                        'description') else ''
                    phone = c.get('properties').get('phone').get('value') if c.get('properties').get('phone') else ''
                    numberofemployees = c.get('properties').get('numberofemployees').get('value') if c.get(
                        'properties').get('numberofemployees') else 0
                    linkedin_company_page = c.get('properties').get('linkedin_company_page').get('value') if c.get(
                        'properties').get('linkedin_company_page') else ''

                    chk_companies = self.env['hubspot.companies'].sudo().search(
                        [('id_companies_hubspot', '=', h_companyID)], limit=1)

                    vals = {
                        'name': h_companyName,
                        'domain': domain,
                        'country': country,
                        'state': state,
                        'city': city,
                        'website': website,
                        'description': description,
                        'phone': phone,
                        'linkedin_company_page': linkedin_company_page,
                        'numberofemployees': numberofemployees,
                        'industry_name': h_companyIndustry
                    }

                    if chk_companies:
                        chk_companies.write(vals)
                    else:
                        vals["id_companies_hubspot"] = h_companyID
                        self.env['hubspot.companies'].sudo().create(vals)

                    total_contact += 1

                vid_offset = hubspot_companies.get('offset')

                print("*** Migrated companies: %d records" % total_contact)
                print("--------------------------------------------------")

                if not hubspot_companies.get('hasMore'):
                    flag_contact = False
                    print("*** BREAK Migrated companies --")
                    break

        print(f'End migrating hubspot companies daily, total time: {datetime.now() - migration_start}')
        print("--------------------------------------------------")


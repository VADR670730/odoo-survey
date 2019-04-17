# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse='lead_id')

class crm_phonecall(models.Model):
    _inherit = 'crm.phonecall'

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse='phonecall_id')

    @api.multi
    def action_make_survey(self):
        """
        Open survey on current
        phonecall.
        
        If there is one survey with model == crm.lead (if we come from lead) open
        this else list surveys. (res.partner if we come from res.partner)
        
        """
        partner_ids = [
            self.env['res.users'].browse(self.env.uid).partner_id.id]
        res = {}
        for phonecall in self:
            if phonecall.partner_id and phonecall.partner_id.email:
                partner_ids.append(phonecall.partner_id.id)
            res = self.env['ir.actions.act_window'].for_xml_id(
                'calendar', 'action_calendar_event')
            res['context'] = {
                'default_phonecall_id': phonecall.id,
                'default_partner_ids': partner_ids,
                'default_user_id': self.env.uid,
                'default_email_from': phonecall.email_from,
                'default_name': phonecall.name,
            }
            """
                default_lead_id, default_phonecall_id, default_partner_id
            
            """
            
        return res


class res_partner(models.Model):
    _inherit = 'res.partner'

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse='partner_id')


class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    lead_id = fields.Many2one(comodel_name='crm.lead')
    phonecall_id = fields.Many2one(comodel_name='crm.phonecall')
    
# ~ class survey_survey(models.Model):
    # ~ _inherit = 'survey.survey'

    # ~ fields_name = fields.Char(string='Fields Name', help='The fields will be used to save survey question.')
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

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse_name='lead_id')
    @api.one
    def _compute_survey_count(self):
        self.survey_count = self.env['survey.user_input'].search_count([('lead_id', '=', self.id)])
    survey_count = fields.Integer(compute='_compute_survey_count',string="Surveys",)

    @api.multi
    def action_make_survey(self):
        """
        Open survey on current
        phonecall.
        
        If there is one survey with model == crm.lead (if we come from lead) open
        this else list surveys. (res.partner if we come from res.partner)
        
        """
        _logger.warn('self crm.lead %s' % self)        
        _logger.warn('context %s' % self._context)        
        return {
                'type': 'ir.actions.act_window',
                'name':  'Open Survey',
                'key2': 'client_action_multi',
                'res_model': 'crm.phonecall.survey.wizard',
                # ~ 'res_id': ,
                'view_type': 'form',
                'view_mode': 'form',
                # ~ 'view_id': self.onboard_stage_id.view_id.id,
                'target': 'new',
                'context': self._context,
            }



class crm_phonecall(models.Model):
    _inherit = 'crm.phonecall'

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse_name='phonecall_id')
    @api.one
    def _compute_survey_count(self):
        self.survey_count = self.env['survey.user_input'].search_count([('phonecall_id', '=', self.id)])
    survey_count = fields.Integer(compute='_compute_survey_count',string="Surveys",)


    @api.multi
    def action_make_survey(self):
        """
        Open survey on current
        phonecall.
        
        If there is one survey with model == crm.lead (if we come from lead) open
        this else list surveys. (res.partner if we come from res.partner)
        
        """
        self.ensure_one()
        _logger.warn('phonecall_id %s' % self.id)        
        _logger.warn('phonecall_id context %s' % self.with_context(phonecall_id=self.id)._context)        
        return {
                'type': 'ir.actions.act_window',
                'name':  'Open Survey',
                'key2': 'client_action_multi',
                'res_model': 'crm.phonecall.survey.wizard',
                # ~ 'res_id': ,
                'view_type': 'form',
                'view_mode': 'form',
                # ~ 'view_id': self.onboard_stage_id.view_id.id,
                'target': 'new',
                'context': self.with_context(phonecall_id=self.id)._context,
            }
            
            
            
        
class crm_phonecall_survey_wizard(models.TransientModel):
    _name = 'crm.phonecall.survey.wizard'

    # ~ survey_id = fields.Many2one(comodel_name='survey.survey',domain=([('stage_id.closed','=',False)]))
    def _default_survey(self):
        return {'survey_id': self.env['survey.survey'].search([('model_id.model','=','crm.phonecall'),('stage_id.closed','=',False),('stage_id.name','!=','draft')])[0].id}
    survey_id = fields.Many2one(comodel_name='survey.survey',domain=([('model_id.model','=','crm.phonecall'),('stage_id.closed','=',False),('stage_id.name','!=','draft')]),required=True,
                          default='_default_survey')
    # ~ survey_id = fields.Many2one(comodel_name='survey.survey',domain=([('model_id.name','=','crm.phonecall'),]))
    
    
    @api.multi
    def confirm(self):
        self.ensure_one()
        _logger.warn('survey context %s' % self._context)
        record = {'survey_id': self.survey_id.id,'state': 'new'}
        if self._context.get('default_opportunity_id'):
            record['lead_id'] = self._context.get('default_opportunity_id')
        elif self._context.get('default_lead_id'):
            record['lead_id'] = self._context.get('default_lead_id')
        if self._context.get('default_partner_id'):
            record['partner_id'] = self._context.get('default_partner_id')
        if self._context.get('phonecall_id'):
            record['phonecall_id'] = self._context.get('phonecall_id')
        response = self.env['survey.user_input'].create(record)
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()


class res_partner(models.Model):
    _inherit = 'res.partner'

    survey_ids = fields.One2many(comodel_name='survey.user_input',inverse_name='partner_id')
    @api.one
    def _compute_survey_count(self):
        self.survey_count = self.env['survey.user_input'].search_count([('partner_id', '=', self.id)])
    survey_count = fields.Integer(compute='_compute_survey_count',string="Surveys",)

class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    lead_id = fields.Many2one(comodel_name='crm.lead')
    phonecall_id = fields.Many2one(comodel_name='crm.phonecall')
    
# ~ class survey_survey(models.Model):
    # ~ _inherit = 'survey.survey'

    # ~ fields_name = fields.Char(string='Fields Name', help='The fields will be used to save survey question.')


class survey_survey(models.Model):
    _inherit = 'survey.survey'

    model_id = fields.Many2one(comodel_name='ir.model')

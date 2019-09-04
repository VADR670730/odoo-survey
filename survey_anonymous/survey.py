# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution,  third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation,  either version 3 of the
#    License,  or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not,  see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class Survey(models.Model):
    _inherit = 'survey.survey'
    
    anonymous = fields.Boolean('Anonymous Answers')
    
    @api.multi
    def write(self, values):
        if not values.get('anonymous', True):
            for survey in self:
                if survey.anonymous and self.env['survey.user_input'].search_count([('survey_id', '=', survey.id), '|', ('partner_id', '!=', False), ('email', '!=', False)]):
                    raise Warning("You can't change a survey from anonymous while it has non-anonymous answers!")
        res = super(Survey, self).write(values)
        if values.get('stage_id') == self.env.ref('survey.stage_closed').id:
            anonymous = self.filtered('anonymous')
            if anonymous:
                anonymous.anonymize_answers()
        return res
    
    @api.multi
    def anonymize_answers(self):
        answers = self.env['survey.user_input'].search([('survey_id', 'in', self._ids)])
        if answers:
            answers.write({'partner_id': False, 'email': False})

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'
    
    anonymous = fields.Boolean(related='survey_id.anonymous', readonly=True)

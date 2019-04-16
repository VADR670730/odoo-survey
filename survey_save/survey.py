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
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.survey.controllers.main import WebsiteSurvey
import logging
_logger = logging.getLogger(__name__)


class survey_question(models.Model):
    _inherit = 'survey.question'

    fields_name = fields.Char(string='Fields Name', help='The fields will be used to save survey question.')

class survey_label(models.Model):
    _inherit = 'survey.label'

    tecnical_value = fields.Char(string='Tecnical Value', help='Use this answer only when survey question will be saved on a record.')

class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    @api.multi
    def get_values(self):
        values = {}
        for line in self.user_input_line_ids.filtered(lambda l: not l.skipped):
            _logger.warn('--------------> Answer Type %s %s' % (line.question_id.display_name,line.answer_type))
            if line.answer_type == 'text':
                if not values.get(line.question_id.fields_name or line.question_id.display_name,False):
                    values[line.question_id.fields_name or line.question_id.display_name]={'value': line.value_text if not line.skipped else None,'type': line.answer_type, 'question_id': line.question_id}
                else:  # Concatenate strings when same name appears several times
                    values[line.question_id.fields_name or line.question_id.display_name]['value'] += ' ' + line.value_text
            elif line.answer_type == 'free_text':
                values[line.question_id.fields_name or line.question_id.display_name]={'value': line.value_free_text if not line.skipped else None,'type': line.answer_type, 'question_id': line.question_id }
            elif line.answer_type == 'number':
                values[line.question_id.fields_name or line.question_id.display_name]={'value': line.value_number if not line.skipped else None,'type': line.answer_type, 'question_id': line.question_id }
            elif line.answer_type == 'date':
                values[line.question_id.fields_name or line.question_id.display_name]={'value': line.value_date if not line.skipped else None,'type': line.answer_type, 'question_id': line.question_id }
            elif line.answer_type == 'suggestion':  # self.question_id.type ->  simple_choice, multiple_choice, matrix
                if line.question_id.type == 'simple_choice':
                    values[line.question_id.fields_name or line.question_id.display_name]={'value': line.value_suggested.tecnical_value,'type': line.question_id.type, 'question_id': line.question_id }
                if line.question_id.type == 'multiple_choice':
                    if values.get(line.question_id.fields_name or line.question_id.display_name,False):
                        values[line.question_id.fields_name or line.question_id.display_name]['value'].append(line.value_suggested.tecnical_value)
                    else:
                        values[line.question_id.fields_name or line.question_id.display_name]={'value': [line.value_suggested.tecnical_value],'type': line.question_id.type, 'question_id': line.question_id }
                if line.question_id.type == 'matrix':
                    if values.get(line.question_id.fields_name or line.question_id.display_name,False):
                        values[line.question_id.fields_name or line.question_id.display_name]['value'][line.value_suggested.tecnical_value] = line.value_suggested_row.value
                    else:
                        values[line.question_id.fields_name or line.question_id.display_name]={'value': {},'type': line.question_id.type, 'question_id': line.question_id }
                        values[line.question_id.fields_name or line.question_id.display_name]['value'][line.value_suggested.tecnical_value] = line.value_suggested_row.value
            else:
                raise Warning('Unknown answer type %s' % line.answer_type)
        return values
    
    @api.one
    def save_values(self,save_record): 
        records = {}
        for key,value in self.get_values().items():
            if not '.' in key:
                records['main'] = {}
            else:
                records[key.split('.')[0]] = {}
        for key,value in self.get_values().items():
            if not '.' in key:
                if value['type'] in ['text','number','date','free_text','simple_choice']:
                    records['main'][key] = value['value']
                elif value['type'] == 'multiple_choice':
                    # Check related table, translate values to ids
                    raise Warning('Multiple_choice not implemented yet')
                    # ~ getattr(user_input.employee_id, key) = (6,0,value['value'])
                elif value['type'] == 'matrix':
                    raise Warning('Matrix not implemented yet')
            else: # Implements only one level down address.street -> records['address']['street'] = value TODO recusive function
                records[key.split('.')[0]][key.split('.')[1]] = value['value']
        for key in records:
            if key == 'main':
                getattr(self,save_record).write(records[key])
                _logger.warn('Main write %s' % records[key])
            else:
                if hasattr(getattr(self,save_record),key):
                    
                    if not 'name' in records[key]: # if name is missing, use name from employee_id.name
                        # ~ _logger.warn('name is missing in record %s:%s adds %s' %(key,records[key],user_input.employee_id.name))
                        records[key]['name'] = getattr(self,save_record).name
                    if not getattr(getattr(self,save_record),key): # Attribute is None, create a record
                        # ~ _logger.warn('Attribute is none %s:%s (create related record)' % (key,getattr(user_input.employee_id,key)))
                        getattr(self,save_record).write({key: getattr(getattr(self,save_record),key).create(records[key]).id})
                    else:
                        # ~ _logger.warn('Write record to attribute %s:%s' % (key,records[key]))
                        getattr(getattr(self,save_record),key).write(records[key])
                else:
                    _logger.error('Attribute is missing  %s:%s ' %(key,records[key]))
     

class survey_user_input_line(models.Model):
    _inherit = 'survey.user_input_line'

    @api.model
    def save_lines(self, user_input_id, question, post, answer_tag):
        # TODO: catch question datas
        return super(survey_user_input_line, self).save_lines(user_input_id, question, post, answer_tag)



# ~ class WebsiteSurvey(WebsiteSurvey):
    
    # ~ @http.route(['/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    # ~ def submit(self, survey, **post):
        # ~ res = super(WebsiteSurvey, self).submit(survey, **post)
        # ~ user_input = request.env['survey.user_input'].search([('token', '=', post['token'])])
        # ~ if user_input.employee_id:
            # ~ user_input.save_values('employee_id')
        # ~ return res

    # ~ @http.route(['/survey/check/<string:token>'], type='http', methods=['GET'], auth='public', website=True)
    # ~ def check(self, token, **post):
        # ~ user_input = request.env['survey.user_input'].search([('token', '=', token)])
        # ~ if user_input.employee_id:
            # ~ user_input.save_values('employee_id')
        # ~ return 'Hello World'
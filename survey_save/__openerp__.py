# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Survey Save',
    'version': '1.1',
    'category': 'Survey',
    'licence': 'AGPL-3',
    'description': """
Save Answers from a Survey on a record
======================================

Adds meta-data to make it possible to save
forms to records.

Question is expanded with fields_name, the attribute name that stores the
answer. Questions with identical fields_name of text-type will be concatenated.
For example Fist_name (name), Last_name (name) will save a string
"First Last" in the attribute name. Fields_names with punctuation writes
data in related records. For example partner_id.street is a valid statement.

Questions using suggestions have a tecnical_value for translation
of the label to the data to be written to the record.

The answer have two new methods for analysing and saving data. The method
get_values() returns a record with a dict of dicts for each record-type. Data
that will be written to the main record is tied to "main". If there is
an attribute partner_id, a record for partner_id has the attribute for key.

The method save_values(save_record) saves the record from get_values(). The
save_record parameter is a string that names the attribute on answer-record.
The idea is that the answer is related to the replicant using an attribute
on the answer (survey.user_input).

class WebsiteSurvey(WebsiteSurvey):

    @http.route(['/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        res = super(WebsiteSurvey, self).submit(survey, **post)
        user_input = request.env['survey.user_input'].search([('token', '=', post['token'])])
        if user_input.employee_id:
            user_input.save_values('employee_id')
        return res


    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['survey',],
    'data': [
        'survey_view.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

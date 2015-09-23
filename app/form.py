"""Search form."""

from flask_wtf import Form
from wtforms import SubmitField, StringField, SelectField, RadioField, \
    BooleanField
from wtforms.validators import DataRequired


class SearchForm(Form):
    submit_button = SubmitField("Search")
    partner_name = StringField("Partner name:",
                               validators=[DataRequired()])
    partner_industry = SelectField("Partner industry:",
                                   choices=[('any', 'Any')])
    partnership_level = SelectField("Partnership level:",
                                    choices=[('any', 'Any')])
    partner_type = RadioField("Partner Type:",
                              choices=[('yes', 'YES'),
                                       ('no', 'NO')])
    business_unit = SelectField("Business Unit:",
                                choices=[('any', 'Any')])
    region = SelectField("Region:",
                         choices=[('any', 'Any')])
    country = SelectField("Country:",
                          choices=[('any', 'Any')])
    competitor = BooleanField("Competitor:")

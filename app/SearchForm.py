# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 13:56:20 2015

@author: rbajaj
"""

from flask.ext.wtf import Form    
from wtforms import SubmitField, StringField, SelectField, RadioField,  BooleanField


class SearchForm(Form):
    submit_button = SubmitField("Search")
    
    partner_industry = SelectField("Partner industry:",
                                   choices=[('any', 'Any')])
    partnership_level = SelectField("Partnership level:",
                                    choices=[('any', 'Any')])
    RH_Partner_req = RadioField("RHPartner",
                              choices=[('1', 'Yes'),
                                       ('0', 'No'),
                                       ('2', 'May Be') ],default='2')


    prod_req = SelectField('product',choices=[('Any','Any'),('CRM','CRM')
    ,('Analytics','Analytics'),('Cloud','Cloud'),('DataManagement','Data Management')
    ,('IoT','IoT'),('Mobility','Mobility'),('Middleware','Middleware'),('Platforms','Platforms')
    ,('Virtualization','Virtualization'),('Security','Security'),('Storage','Storage')], default='Any')
    
    
    ind_req = SelectField('industry' ,choices=[('Any','Any'),('Aerospace&Defense','Aerospace & Defense')  ,('Automotive','Automotive'),('Banking','Banking'),('Computer_Services','Computer Services')  ,('Chemicals&Petroleum','Chemicals & Petroleum'),('EngineeringandConstruction','Engineering & Construction'),  ('Education','Education'),('Electronics','Electronics')  ,('Energy&Utilities','Energy & Utilities'),  ('FinancialMarkets','Financial Markets'),('Healthcare','Healthcare'),  ('IndustrialProducts','Industrial Products'),('Insurance','Insurance'),  ('LifeSciences','Life Sciences'),('Media&Entertainment','Media & Entertainment'),  ('Public_Sector','Public Sector'),  ('ProfessionalServices','Professional Services'),('Retail','Retail'),  ('Telecommunications','Telecommunications'),('Travel&Transportation','Travel & Transportation'),('WholesaleDistribution&Services','WholesaleDistribution & Services')], default='Any')

    region_req = SelectField('region',choices=[('Any','Any'),('APAC','APAC')  ,('EMEA','EMEA'),('LATAM','LATAM'),('NA','NA')], default='Any')

    #,('"C™te d"'"Ivoire"','"C™te d"'"Ivoire') , ,,, ,('Curaao','Curaao')
    ctry_choices=[('Any','Worldwide'),('Afghanistan','Afghanistan') ,('Albania','Albania'),('Algeria','Algeria'),('Andorra','Andorra'),('Angola','Angola'),('Antartica','Antartica'),('Amenia','Amenia'),('Aruba','Aruba'),('Australia','Australia'),('Austria','Austria'),('Azerbaijan','Azerbaijan'),('Bahamas','Bahamas'),('Baharain','Baharain'),('Bangladesh','Bangladesh'),('Barabados','Barabados'),('Belarus','Belarus'),('Belgium','Belgium'),('Belize','Belize'),('Benin','Benin'),('Bhutan','Bhutan'),('Bolivia','Bolivia'),('Bosnania and Herzegovina','Bosnania and Herzegovina'),('Botswana','Botswana'),('Brazil','Brazil'),('British Indian Ocean Territory','British Indian Ocean Territory'),('Brunei Darussalam','Brunei Darussalam'),('Bulgaria','Bulgaria'),('Burkina Fas','Burkina Fas'),('Burundi','Burundi'),('Cambodia','Cambodia'),('Cameroon','Cameroon'),('Canada','Canada'),('Cape Verde','Cape Verde'),('Cayman Islands','Cayman Islands'),('Central African Republic','Central African Republic'),('Chad','Chad'),('Chile','Chile'),('China','China'),('Christmas Island','Christmas Island'),('Colombia','Colombia'),('Comoros','Comoros'),('Congo (Kinshasa)','Congo (Kinshasa)'),('Congo (Brazzaville)','Congo (Brazzaville)'),('Cook Islands','Cook Islands'),('Costa Rica','Costa Rica'),('Croatia','Croatia'),('Cuba','Cuba'),('Cyprus','Cyprus'),('Czech Republic','Czech Republic'),('Denmark','Denmark'),('Djibouti','Djibouti'),('Dominica','Dominica'),('Dominican','Dominican'),('Ecuador','Ecuador'),('Egypt','Egypt'),('El Salvador','El Salvador'),('Equatorial Guinea','Equatorial Guinea'),('EritreaEstonia','EritreaEstonia'),('Estonia','Estonia'),('Ethiopia','Ethiopia'),('Falkland Islands','Falkland Islands'),('Faroe Islands','Faroe Islands'),('Fiji','Fiji'),('Finland','Finland'),('France','France'),('French Guiana','French Guiana'),('French Polynesia','French Polynesia'),('French Southern Territorie','French Southern Territorie'),('Gabon','Gabon'),('Gambia','Gambia'),('Gambia','Gambia'),('Germany','Germany'),('Ghana','Ghana'),('Gibraltar','Gibraltar'),('Greece','Greece'),('Greenland','Greenland'),('Grenada','Grenada'),('Guadeloupe','Guadeloupe'),('Guam','Guam'),('Guatemala','Guatemala'),('Guernsey','Guernsey'),('Guinea','Guinea'),('Guinea-Bissau','Guinea-Bissau'),('Guyana','Guyana'),('Haiti','Haiti'),('Heard and McDonald Islands','Heard and McDonald Islands'),('Honduras','Honduras'),('Hong Kong','Hong Kong'),('Hungary','Hungary'),('Iceland','Iceland'),('India','India'),('Indonesia','Indonesia'),('Iran','Iran'),('Iraq','Iraq'),('Ireland','Ireland'),('Isle of Man','Isle of Man'),('Israel','Israel'),('Italy','Italy'),('Jamaica','Jamaica'),('Japan','Japan'),('Jersey','Jersey'),('Kazakhstan','Kazakhstan'),('Kenya','Kenya'),('Kiribati','Kiribati'),('North Korea','North Korea'),('South Korea','South Korea'),('Kuwait','Kuwait'),('Kyrgyzstan','Kyrgyzstan'),('Laos','Laos'),('Latvia','Latvia'),('Lebanon','Lebanon'),('Lesotho','Lesotho'),('Liberia','Liberia'),('Libya','Libya'),('Liechtenstein','Liechtenstein'),('Lithuania','Lithuania'),('Luxembourg','Luxembourg'),('Macau','Macau'),('Macedonia','Macedonia'),('Madagascar','Madagascar'),('Malawi','Malawi'),('Malaysia','Malaysia'),('Maldives','Maldives'),('Mali','Mali'),('Malta','Malta'),('Marshall Islands','Marshall Islands'),('Martinique','Martinique'),('Mauritania','Mauritania'),('Mauritius','Mauritius'),('Mayotte','Mayotte'),('Mexico','Mexico'),('Micronesia','Micronesia'),('Moldova','Moldova'),('Monaco','Monaco'),('Mongolia','Mongolia'),('Montenegro','Montenegro'),('Montserrat','Montserrat'),('Morocco','Morocco'),('Mozambique','Mozambique'),('Myanmar','Myanmar'),('Namibia','Namibia'),('Nauru','Nauru'),('Nepal','Nepal'),('Netherlands','Netherlands'),('New Caledonia','New Caledonia'),('New Zealand','New Zealand'),('Nicaragua','Nicaragua'),('Niger','Niger'),('Nigeria','Nigeria'),('Niue','Niue'),('Norfolk Island','Norfolk Island'),('Northern Mariana Islands','Northern Mariana Islands'),('Norway','Norway'),('Oman','Oman'),('Pakistan','Pakistan'),('Palau','Palau'),('Palestine','Palestine'),('Panama','Panama'),('Papua New Guinea','Papua New Guinea'),('Paraguay','Paraguay'),('Peru','Peru'),('Philippines','Philippines'),('Pitcairn','Pitcairn'),('Poland','Poland'),('Portugal','Portugal'),('Puerto Rico','Puerto Rico'),('Qatar','Qatar'),('Reunion','Reunion'),('Romania','Romania'),('Russian Federation','Russian Federation'),('Rwanda','Rwanda'),('Saint BarthZlemy','Saint BarthZlemy'),('Saint Helena','Saint Helena'),('Saint Kitts and Nevis','Saint Kitts and Nevis'),('Saint Lucia','Saint Lucia'),('Saint Martin','Saint Martin'),('Saint Pierre and Miquelon','Saint Pierre and Miquelon'),('Saint Vincent and the Grenadines','Saint Vincent and the Grenadines'),('Samoa','Samoa'),('San Marino','San Marino'),('Sao Tome and Principe','Sao Tome and Principe'),('Saudi Arabia','Saudi Arabia'),('Senegal','Senegal'),('Serbia','Serbia'),('Seychelles','Seychelles'),('Sierra Leone','Sierra Leone'),('Singapore','Singapore'),('Sint Maarten','Sint Maarten'),('Slovakia','Slovakia'),('Slovenia','Slovenia'),('Solomon Islands','Solomon Islands'),('Somalia','Somalia'),('Somalia','Somalia'),('South Africa','South Africa'),('South Georgia and South Sandwich Islands','South Georgia and South Sandwich Islands'),('South Sudan','South Sudan'),('Spain','Spain'),('Sri Lanka','Sri Lanka'),('Sudan','Sudan'),('Suriname','Suriname'),('Svalbard and Jan Mayen Islands','Svalbard and Jan Mayen Islands'),('Swaziland','Swaziland'),('Sweden','Sweden'),('Switzerland','Switzerland'),('Syria','Syria'),('Taiwan','Taiwan'),('Tajikistan','Tajikistan'),('Tanzania','Tanzania'),('Thailand','Thailand'),('Timor-Leste','Timor-Leste'),('Togo','Togo'),('Tokelau','Tokelau'),('Tonga','Tonga'),('Trinidad and Tobago','Trinidad and Tobago'),('Tunisia','Tunisia'),('Turkey','Turkey'),('Turkmenistan','Turkmenistan'),('Turks and Caicos Islands','Turks and Caicos Islands'),('Tuvalu','Tuvalu'),('Uganda','Uganda'),('Ukraine','Ukraine'),('United Arab Emirates','United Arab Emirates'),('United Kingdom','United Kingdom'),('United States Minor Outlying Islands','United States Minor Outlying Islands'),('United States','United States'),('Uruguay','Uruguay'),('Uzbekistan','Uzbekistan'),('Vanuatu','Vanuatu'),('Vatican City','Vatican City'),('Venezuela','Venezuela'),('Vietnam','Vietnam'),('Virgin Islands, British','Virgin Islands, British'),('Virgin Islands, U.S.','Virgin Islands, U.S.'),('Western Sahara','Western Sahara'),('Yemen','Yemen'),('Zambia','Zambia'),('Zimbabwe','Zimbabwe')]
   
    country_req = SelectField('country',choices = ctry_choices, default='Any')

           
    
    name_req = StringField('pname', default='')
    
    
    
    role_req = SelectField('role',choices=[('Any','Any'),('Distributor','Distributor')
    ,('ISV','ISV'),('OEM','OEM'),('Reseller','Reseller')
    ,('SystemIntegrator','System Integrator')], default='Any')


    level_req = SelectField('partnership_level',choices=[('Any','Any'),('Diamond','Diamond')
    ,('Gold','Gold'),('Silver','Silver'),('Bronze','Bronze')
    ,('Valued','Valued')], default='Any')
    
    
    Global_Partner_req = BooleanField('Global_Partner_req')

#    CISCO_Partner_req = BooleanField('CISCOPartner')   
#    CITRIX_Partner_req = BooleanField('CITRIXPartner')
#    MS_Partner_req = BooleanField('MSPartner')
#    Dell_Partner_req = BooleanField('DellPartner')
#    IBM_Partner_req = BooleanField('IBMPartner')
#    Oracle_Partner_req = BooleanField('OraclePartner')
#    VM_Partner_req = BooleanField('VMPartner')
#    
#    SAP_Partner_req = BooleanField('SAPPartner')
    
#    NonRH_Partner_req = BooleanField('NonRHPartner')
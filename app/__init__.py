# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 16:34:28 2015

@author: rbajaj
"""

from flask import Flask
#from flask.ext.sqlalchemy import SQLAlchemy
#from flaskext.mysql import MySQL


app = Flask(__name__)
#app.config.from_object('config')
#db = SQLAlchemy(app)

#
#mysql = MySQL()
#app.config['MYSQL_DATABASE_USER'] = 'rbajaj'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'nxzd8978'
#app.config['MYSQL_DATABASE_DB'] = 'rhpartners'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)

from app import views
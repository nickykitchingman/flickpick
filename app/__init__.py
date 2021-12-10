#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:05:22 2021

@author: sc20nk
"""

# Setup app & admin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True)
adminView = Admin(app, template_mode="bootstrap3")

# Logging
import logging
import logging.config
import logging.handlers

logging.config.fileConfig('log/logging.conf')
logging._srcfile = False
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False

traceLogger = logging.getLogger('trace')
accessLogger = logging.getLogger('access')
errorLogger = logging.getLogger('warning')
criticalLogger = logging.getLogger('critical')

# Models & views (including auth, admin views)
from app import views, models, auth, admin

app.register_blueprint(auth.bp)
app.register_blueprint(views.bp)
app.add_url_rule('/', endpoint='index')
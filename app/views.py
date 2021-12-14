#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:07:20 2021

@author: sc20nk
"""

from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session, jsonify
from app import app, db, models, admin, errorLogger, traceLogger, criticalLogger
from .forms import RegisterForm
from .models import User, Movie, Group, friend_request, MovieChoice
from sqlalchemy import desc
from sqlalchemy.orm import aliased
import json

from werkzeug.exceptions import abort
from app.auth import login_required

bp = Blueprint('app', __name__)


@bp.route('/')
def index():
    # Customise index if signed in
    signed_in = g.user is not None
    return render_template("index.html",
                           title="Home",
                           user=g.user)

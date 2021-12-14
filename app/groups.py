#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 22:50:10 2021

@author: sc20nk
"""

from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session, jsonify
from app import app, db, models, admin, errorLogger, traceLogger, criticalLogger
from .forms import RegisterForm
from .models import User, Movie, StreamSite, Group, friend_request, MovieChoice
from sqlalchemy import desc
from sqlalchemy.orm import aliased
import json

from werkzeug.exceptions import abort
from app.auth import login_required

bp = Blueprint('groups', __name__)


@bp.route('/groups')
@login_required
def groups():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to load movies - not logged in')
        abort(401)

    return render_template("main/groups.html",
                           title="Groups",
                           user=g.user,
                           group_list=g.user.groups)


@bp.route('/create_group', methods=['POST'])
@login_required
def create_group():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised create_group - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    group_name = data.get('name')
    traceLogger.debug(
        f'User ({g.user.userId}) requested to find create_group %{group_name}%')

    # Check doesn't already exist
    if g.user.in_group(group_name):
        return jsonify({'error': 'Group already exists'})

    # Create group and add user to it
    new_group = Group(name=group_name)
    g.user.groups.append(new_group)
    db.session.commit()

    return json.dumps({'status': 'OK'})

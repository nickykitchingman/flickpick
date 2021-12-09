#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:07:20 2021

@author: sc20nk
"""

from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session, jsonify
from app import app, db, models, admin, errorLogger, traceLogger
from .forms import RegisterForm
from .models import User, Movie, StreamSite, Group
from flask_admin.contrib.sqla import ModelView 
import json

from werkzeug.exceptions import abort
from app.auth import login_required

bp = Blueprint('app', __name__)

# Admin front end
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(StreamSite, db.session))
admin.add_view(ModelView(Group, db.session))

@bp.route('/')
def index():
        signed_in = session.get('user_id') is not None

        return render_template("index.html", 
                title="Home",
                user_level=1 if signed_in else 0)

@bp.route('/friends')
@login_required
def friends():
        #friends = [{"forename":"Nicky", "surname":"Kitchingman"}, {"forename":"Tony", "surname":"Stark"}]
        #matches = [{"name":"Iron Man"}, {"name":"Cars 3"}]
        # Get current user
        user_id = session.get('user_id')

        # Not logged in
        if user_id == None:
                errorLogger.error('Failed to load movies - no user_id in session')
                abort(401)
        user = User.query.filter_by(userId=user_id).first()
        if user is None:
                errorLogger.error(f'Failed to load movies - user ({user_id}) not in database')
                abort(401)

        return render_template("main/friends.html", 
                title="Friends",
                user_level=1,
                friend_list=user.friends)
                #matches=matches)

@bp.route('/users_like', methods=['POST'])
@login_required
def users_like():
        user_id = session.get('user_id')
        # Not logged in
        if user_id == None:
                errorLogger.error('Unauthorised user_like - not logged in')
                abort(403)

        # Load JSON data
        data = json.loads(request.data)
        username = data.get('username')
        traceLogger.debug(f'User ({user_id}) requested to find users_like %{username}%')

        # Get users with similar username
        users = User.query.filter(User.username.like(f'%{username}%'), User.userId!=user_id).limit(5).all()
        user_dicts = [user.as_dict() for user in users]

        return jsonify(user_dicts)

@bp.route('/groups')
@login_required
def groups():
        #groups = [{"name":"Fam"}, {"name":"The Boys"}, {"name":"CompSci"}]
        #matches = [{"name":"Jumanji"}, {"name":"Spectre"}]
        # Get current user
        user_id = session.get('user_id')

        # Not logged in
        if user_id == None:
                errorLogger.error('Failed to load movies - no user_id in session')
                abort(401)
        user = User.query.filter_by(userId=user_id).first()
        if user is None:
                errorLogger.error(f'Failed to load movies - user ({user_id}) not in database')
                abort(401)

        return render_template("main/groups.html", 
                title="Groups",
                user_level=1,
                group_list=user.groups)
                #matches=matches)

@bp.route('/matcher')
@login_required
def matcher():
        movie =  {"name":"Spectre"}

        return render_template("main/movie_match.html", 
                title="Movie Matcher",
                user_level=1,
                movie=movie)

@bp.route('/movies')
@login_required
def movies():
        #movie =  {"name":"Spectre"}
        # Get current user
        user_id = session.get('user_id')

        # Not logged in
        if user_id == None:
                errorLogger.error('Failed to load movies - no user_id in session')
                abort(401)
        user = User.query.filter_by(userId=user_id).first()
        if user is None:
                errorLogger.error(f'Failed to load movies - user ({user_id}) not in database')
                abort(401)

        return render_template("main/movies.html", 
                title="Your Movies",
                user_level=1,
                movie_list=user.movies)
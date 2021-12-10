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

@bp.route('/friends')
@login_required
def friends():
        # Not logged in
        if g.user == None:
                errorLogger.error('Failed to load movies - no user_id in session')
                abort(401)

        return render_template("main/friends.html", 
                title="Friends",
                user=g.user,
                friend_list=g.user.friends)

@bp.route('/users_like', methods=['POST'])
@login_required
def users_like():
        # Not logged in
        if g.user == None:
                errorLogger.error('Unauthorised user_like - not logged in')
                abort(403)

        # Load JSON data
        data = json.loads(request.data)
        username = data.get('username')
        traceLogger.debug(f'User ({g.user.userId}) requested to find users_like %{username}%')

        # Get users with similar username
        users = User.query.filter(User.username.like(f'%{username}%'),
                User.userId!=g.user.userId,
                User.roles.any(name='user')).limit(5).all()
        user_dicts = [user.as_dict() for user in users]

        return jsonify(user_dicts)

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

@bp.route('/matcher')
@login_required
def matcher():
        # Not logged in
        if g.user == None:
                errorLogger.error('Failed to load matcher - not logged in')
                abort(401)

        movie =  {"name":"Spectre"}

        return render_template("main/movie_match.html", 
                title="Movie Matcher",
                user=g.user,
                movie=movie)

@bp.route('/movies')
@login_required
def movies():
        # Not logged in
        if g.user == None:
                errorLogger.error('Failed to load movies - not logged in')
                abort(401)

        return render_template("main/movies.html", 
                title="Your Movies",
                user=g.user,
                movie_list=g.user.movies)
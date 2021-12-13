#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:07:20 2021

@author: sc20nk
"""

from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session, jsonify
from app import app, db, models, admin, errorLogger, traceLogger
from .forms import RegisterForm
from .models import User, Movie, StreamSite, Group, friend_request
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
        errorLogger.error('Failed to load friends - no user_id in session')
        abort(401)

    # Get friend requests
    requests = db.session.query(friend_request.c.friendId, friend_request.c.date).filter(
        friend_request.c.userId == g.user.userId).all()
    requests_list = [{'friend': User.query.get(
        req.friendId), 'data': req.date} for req in requests]

    return render_template("main/friends.html",
                           title="Friends",
                           user=g.user,
                           friend_list=g.user.friends,
                           requests=requests_list)


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
    traceLogger.debug(
        f'User ({g.user.userId}) requested to find users_like %{username}%')

    # Get users with similar username
    users = User.query.filter(User.username.like(f'%{username}%'),
                              User.userId != g.user.userId,
                              User.roles.any(name='user'),
                              ~User.requests.any(userId=g.user.userId,
                                                 )).limit(5).all()
    user_dicts = [user.as_dict() for user in users]

    return jsonify(user_dicts)

@bp.route('/friend_request', methods=['POST'])
@login_required
def send_friend_request():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised friend_request - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    user_id = data.get('userId')

    # Check user exists
    friend = User.query.get(user_id)
    if friend is None:
        errorLogger.error('friend_request failed - could not find user')
        abort(404)

    # Send friend request
    traceLogger.debug(
        f'User ({g.user.userId}) sending request to {friend.username}')
    friend.requests.append(g.user)
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/request_accept', methods=['POST'])
@login_required
def request_accept():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised request_accept - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    user_id = data.get('userId')

    # Check user exists
    friend = User.query.get(user_id)
    if friend is None:
        errorLogger.error('request_accept failed - could not find user')
        abort(404)

    # Accept friend request
    traceLogger.debug(
        f'User ({g.user.userId}) accepting request from ({friend.userId})')
    if friend not in g.user.friends:
        g.user.friends.append(friend)
    if g.user not in friend.friends:
        friend.friends.append(g.user)
    if friend in g.user.requests:
        g.user.requests.remove(friend)
    db.session.commit()

    return json.dumps({'status': 'OK'})

@bp.route('/request_decline', methods=['POST'])
@login_required
def request_decline():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised request_decline - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    user_id = data.get('userId')

    # Check user exists
    friend = User.query.get(user_id)
    if friend is None:
        errorLogger.error('request_decline failed - could not find user')
        abort(404)

    # Decline friend request
    traceLogger.debug(
        f'User ({g.user.userId}) declining request from ({friend.userId})')
    if friend in g.user.requests:
        g.user.requests.remove(friend)
    db.session.commit()

    return json.dumps({'status': 'OK'})

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

    movie = {"name": "Spectre"}

    return render_template("main/movie_match.html",
                           title="Movie Matcher",
                           user=g.user,
                           movie=movie)

@bp.route('/clear_movies')
@login_required
def clear_movies():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to clear_movies - not logged in')
        abort(401)

    g.user.movies.empty()
    db.session.commit()

    return json.dumps({'status': 'OK'})

@bp.route('/next_movie')
@login_required
def next_movie():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to get next_movie - not logged in')
        abort(401)

    num_movies = Movie.query.count()

    return json.dumps({'status': 'OK'})

@bp.route('/clear_movies')
@login_required
def matcher():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to clear_movies - not logged in')
        abort(401)

    g.user.movies.empty()
    db.session.commit()


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
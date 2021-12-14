#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 22:48:35 2021

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

bp = Blueprint('friends', __name__)


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
        req.friendId), 'date': req.date} for req in requests]

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


def matchToDict(match):
    match_dict = match.Movie.as_dict()
    match_dict['strength'] = match[1] + match[2]
    return match_dict


@bp.route('/match_friend', methods=['POST'])
@login_required
def match_friend():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to match friend - not logged in')
        abort(401)

    # Load JSON data
    data = json.loads(request.data)
    friend_id = data.get('friendId')
    friend = User.query.get(friend_id)
    traceLogger.debug(
        f"User ({g.user.userId}) matched with {friend_id}")

    # Invalid movie
    if friend is None:
        errorLogger.error(
            f'Failed to match friend - friend id not valid {friend_id}')
        abort(403)

    # Movie match by summing strengths
    # try:
    FriendMovieChoice = aliased(MovieChoice)
    matches = db.session.query(Movie, MovieChoice.strength, FriendMovieChoice.strength)\
        .join(MovieChoice, Movie.movieId == MovieChoice.movieId)\
        .join(FriendMovieChoice, Movie.movieId == FriendMovieChoice.movieId)\
        .filter(MovieChoice.userId == g.user.userId,
                FriendMovieChoice.userId == friend.userId,
                MovieChoice.strength + FriendMovieChoice.strength > 0)\
        .order_by(desc(MovieChoice.strength + FriendMovieChoice.strength)).all()
    # Critical db error
    # except SQLAlchemyError as e:
    #     error = str(e.__dict__['orig'])
    #     criticalLogger.critical(error)
    #     abort(500)

    max_strength = 4

    return jsonify({'matches': [matchToDict(match) for match in matches],
                    'maxStrength': max_strength})

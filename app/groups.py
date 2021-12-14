#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 22:50:10 2021

@author: sc20nk
"""

from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session, jsonify
from app import app, db, models, admin, errorLogger, traceLogger, criticalLogger
from .forms import RegisterForm
from .models import User, Movie, Group, in_group, MovieChoice
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
    group_name = data.get('input')
    traceLogger.debug(
        f'User ({g.user.userId}) requested to find create_group {group_name}')

    # Check doesn't already exist
    if g.user.in_group(group_name):
        return jsonify({'error': 'Group already exists'})

    # Create group and add user to it
    new_group = Group(name=group_name)
    g.user.groups.append(new_group)
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/add_to_group', methods=['POST'])
@login_required
def add_to_group():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised add to group - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    friend_name = data.get('input')
    group_id = data.get('groupId')
    friend = User.query.filter_by(username=friend_name).first()
    group = Group.query.get(group_id)

    # Check user exists
    if friend is None:
        return jsonify({'error': 'User does not exist'})
    # Check is friend
    if not g.user.has_friend(friend_name):
        return jsonify({'error': 'Must be friends!'})
    # Check not already in group
    if friend.in_group_id(group_id):
        return jsonify({'error': 'User already in group'})
    # Check group exists
    if group is None:
        errorLogger.error(f"Cannot add to group {group_id} - does not exist")
        abort(403)

    traceLogger.debug(
        f'User ({g.user.userId}) added {friend.userId} to group {group_id}')

    # Add friend to group
    group.members.append(friend)
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/edit_group', methods=['POST'])
@login_required
def edit_group():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised edit group - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    group_name = data.get('input')
    group_id = data.get('groupId')
    group = Group.query.get(group_id)

    # Check group exists
    if group is None:
        errorLogger.error(f"Cannot edit group {group_id} - does not exist")
        abort(403)

    traceLogger.debug(
        f'User ({g.user.userId}) changed {group.groupId} name to {group_name}')

    # Add friend to group
    group.name = group_name
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/leave_group', methods=['POST'])
@login_required
def leave_group():
    # Not logged in
    if g.user == None:
        errorLogger.error('Unauthorised leave_group - not logged in')
        abort(403)

    # Load JSON data
    data = json.loads(request.data)
    group_id = data.get('groupId')
    group = Group.query.get(group_id)
    traceLogger.debug(
        f'User ({g.user.userId}) requested to find leave_group {group_id}')

    # Check user in group
    if not g.user.in_group_id(group_id):
        errorLogger.error(
            f'User {g.user.userId} cannot leave_group - not in it')
        abort(403)

    # Check group exists
    if group is None:
        errorLogger.error(
            f'User {g.user.userId} cannot leave_group - does not exist')
        abort(403)

    # Leave group
    num_members = len(group.members)
    g.user.groups.remove(group)
    if (num_members <= 1):
        db.session.delete(group)
    db.session.commit()

    return json.dumps({'status': 'OK'})


# Convert match to dictionary form for json
def matchToDict(match):
    match_dict = match.Movie.as_dict()
    strength = match[1]
    if len(match) > 2:
        strength += match[2]
    match_dict['strength'] = strength
    return match_dict


@bp.route('/match_group', methods=['POST'])
@login_required
def match_group():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to match group - not logged in')
        abort(401)

    # Load JSON data
    data = json.loads(request.data)
    group_id = data.get('groupId')
    group = Group.query.get(group_id)
    traceLogger.debug(
        f"User ({g.user.userId}) matched with {group_id}")

    # Invalid movie
    if group is None:
        errorLogger.error(
            f'Failed to match group - group id not valid {group_id}')
        abort(403)

    num_members = len(group.members)
    max_strength = num_members * 2

    # Movie match by summing strengths
    if (num_members > 1):
        FriendMovieChoice = aliased(MovieChoice)
        in_group_too = aliased(in_group)
        matches = db.session.query(Movie, MovieChoice.strength, FriendMovieChoice.strength)\
            .join(MovieChoice, Movie.movieId == MovieChoice.movieId)\
            .join(FriendMovieChoice, Movie.movieId == FriendMovieChoice.movieId)\
            .join(Group, Group.groupId == group_id)\
            .filter(MovieChoice.userId == g.user.userId,
                    in_group.c.userId == MovieChoice.userId,
                    in_group_too.c.userId == FriendMovieChoice.userId,
                    MovieChoice.userId != FriendMovieChoice.userId,
                    MovieChoice.strength + FriendMovieChoice.strength > 0)\
            .order_by(desc(MovieChoice.strength + FriendMovieChoice.strength)).all()
    else:
        matches = db.session.query(Movie, MovieChoice.strength)\
            .join(MovieChoice, Movie.movieId == MovieChoice.movieId)\
            .filter(MovieChoice.userId == g.user.userId,
                    MovieChoice.strength > 0)\
            .order_by(desc(MovieChoice.strength)).all()

    return jsonify({'matches': [matchToDict(match) for match in matches],
                    'maxStrength': max_strength})

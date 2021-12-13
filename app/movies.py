#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 22:45:40 2021

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

bp = Blueprint('movies', __name__)


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

    g.user.moviechoices.clear()
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/next_movie')
@login_required
def next_movie():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to get next_movie - not logged in')
        abort(401)

    # Get random movie user has not already chosen
    while True:
        # No movies
        if Movie.query.count() < 1:
            movie = None
            break

        movie = Movie.get_random(g.user.userId)
        if movie not in g.user.moviechoices:
            break

    # Run out
    if movie is None:
        return jsonify({'movie': None})

    # Convert to useful form for the html
    movie_dict = movie.as_dict()
    movie_dict['releasedate'] = movie.releasedate.strftime('%b %d %Y')

    return jsonify({'movie': movie_dict})


@bp.route('/add_movie', methods=['POST'])
@login_required
def add_movie():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to add_movie - not logged in')
        abort(401)

    # Load JSON data
    data = json.loads(request.data)
    movie_id = data.get('movieId')
    decision = data.get('decision')
    movie = Movie.query.get(movie_id)

    traceLogger.debug(
        f"User ({g.user.userId}) decided {decision} on movie {movie_id}")

    # Invalid decision
    if decision not in ['0', '1', '2']:
        errorLogger.error(
            f'Failed to add movie - decision not valid {decision}')
        abort(403)

    # Invalid movie
    if movie is None:
        errorLogger.error(
            f'Failed to add movie - movie id not valid {movie_id}')
        abort(403)

    # Make decision on movie
    if movie not in g.user.moviechoices:
        g.user.moviechoices.append(movie)
    choice = MovieChoice.query.filter_by(
        userId=g.user.userId, movieId=movie_id).first()
    choice.strength = int(decision)
    db.session.commit()

    return json.dumps({'status': 'OK'})


@bp.route('/movies')
@login_required
def movies():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to load movies - not logged in')
        abort(401)

    # Chosen movies with strength 2 (yes)
    movies_yes = Movie.query.join(
        MovieChoice, User).filter(User.userId == g.user.userId,
                                  Movie.movieId == MovieChoice.movieId,
                                  MovieChoice.strength == 2)
    # Chosen movies with strength 1 (maybe)
    movies_maybe = Movie.query.join(
        MovieChoice, User).filter(User.userId == g.user.userId,
                                  Movie.movieId == MovieChoice.movieId,
                                  MovieChoice.strength == 1)
    return render_template("main/movies.html",
                           title="Your Movies",
                           user=g.user,
                           movies_yes=movies_yes,
                           movies_maybe=movies_maybe)


def matchToDict(match):
    match_dict = match.Movie.as_dict()
    match_dict['strength'] = match[1] + match[2]
    return match_dict


@bp.route('/match_friend', methods=['POST'])
@login_required
def match_friend():
    # Not logged in
    if g.user == None:
        errorLogger.error('Failed to get next_movie - not logged in')
        abort(401)

    # Load JSON data
    data = json.loads(request.data)
    friend_id = data.get('friendId')
    friend = User.query.get(friend_id)

    # Invalid movie
    if friend is None:
        errorLogger.error(
            f'Failed to match friend - friend id not valid {movie_id}')
        abort(403)

    traceLogger.debug(
        f"User ({g.user.userId}) matched with {friend_id}")

    # Movie match by strengths adding to 4 (both said yes)
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

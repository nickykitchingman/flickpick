import os
import unittest
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models
from app.models import User
from datetime import date
from werkzeug.security import check_password_hash

class AppTest(unittest.TestCase):
    def populate_db(self):
        test_user = User(
            forename='fname',
            surname='sname',
            username='test',
            birthday=date(2001,10,31),
            email='test@test.com')
        test_user.set_password('test')
        db.session.add(test_user)
        db.session.commit()

    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        self.populate_db()
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_valid(self):
        return self.app.post('/auth/register', data={
            'forename':'foo',
            'surname':'bar',
            'username':'test2',
            'password':'test2',
            'confirm_password':'test2',
            'birthday':'31/10/2001',
            'email':'test2@test.com',
        }, follow_redirects=True)

    def register_emailalreadyexists(self):
        return self.app.post('/auth/register', data={
            'forename':'foo',
            'surname':'bar',
            'username':'test2',
            'password':'test2',
            'confirm_password':'test2',
            'birthday':'31/10/2001',
            'email':'test@test.com',
        }, follow_redirects=True)

    def login_valid(self):
        return self.app.post('/auth/login', data={
            'username':'test',
            'password':'test',
        }, follow_redirects=True)

    def login_invalid(self):
        return self.app.post('/auth/login', data={
            'username':'doesnotexist',
            'password':'doesnotexist',
        }, follow_redirects=True)
    

    # MATCHER
    def test_matcherexists(self):
        response = self.app.get('/matcher', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
    
    # MOVIES
    def test_moviesexists(self):
        response = self.app.get('/movies', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
    
    # FRIENDS
    def test_friendsexists(self):
        response = self.app.get('/friends', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
    
    # GROUPS
    def test_groupsexists(self):
        response = self.app.get('/groups', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    # LOGIN
    def test_login_valid(self):
        response = self.login_valid()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/')

    def test_login_invalid(self):
        response = self.login_invalid()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/auth/login')

    # LOGOUT
    def test_logout(self):
        self.login_valid()
        response = self.app.get('/auth/logout', follow_redirects=True)
        
        # Sign up button available (redirected to index)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/')
        html = response.get_data(as_text=True)
        self.assertTrue('Sign Up' in html)

    # REGISTRATION
    def test_registerfrontend_valid(self):
        response = self.register_valid()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/auth/login')

    def test_registerdatabase_valid(self):
        response = self.register_valid()
        user = User.query.filter_by(username='test2').first()

        # Check every value in db matches new user correctly
        self.assertNotEqual(user, None)
        self.assertEqual(user.forename, 'foo')
        self.assertEqual(user.surname, 'bar')
        self.assertTrue(check_password_hash(user.password, 'test2'))
        self.assertEqual(user.email, 'test2@test.com')
        self.assertEqual(user.birthday, date(2001, 10, 31))

    def test_registerfrontend_invalid(self):
        response = self.register_emailalreadyexists()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/auth/register')

    def test_registerdatabase_invalid(self):
        response = self.register_emailalreadyexists()
        user = User.query.filter_by(username='test2').first()

        # Check user does not exists in db
        self.assertEqual(user, None)


# RUN
if __name__ == '__main__':
    unittest.main()
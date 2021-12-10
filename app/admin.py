from app import app, adminView, db, models, traceLogger, accessLogger
from flask import Blueprint, url_for, session, g
from .models import User, Movie, StreamSite, Group, Role

from flask_admin.contrib.sqla import ModelView 
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemyUserDatastore

# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)

class MyModelView(ModelView):
    def is_accessible(self):
        # Get current user
        if g.user is None: return False

        # Valid role
        return g.user.has_role('superuser')
    
    def _handle_view(self, name):
        if not self.is_accessible():
            accessLogger.info('User tried to access admin without correct authorisation')
            return redirect(url_for('auth.login'))

# Admin front end
adminView.add_view(MyModelView(User, db.session))
adminView.add_view(MyModelView(Movie, db.session))
adminView.add_view(MyModelView(StreamSite, db.session))
adminView.add_view(MyModelView(Group, db.session))
adminView.add_view(MyModelView(Role, db.session))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
# @security.context_processor
# def security_context_processor():
#     return dict(
#         admin_base_template=admin.base_template,
#         admin_view=admin.index_view,
#         h=admin_helpers,
#         get_url=url_for
#     )
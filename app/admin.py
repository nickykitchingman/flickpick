from app import app, db, models, traceLogger, accessLogger
from flask import Blueprint, url_for, session, g, redirect
from .models import User, Movie, Group, Role, MovieChoice

from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin import Admin, AdminIndexView

# Override index view for admin to prevent unauthorised access


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Get current user
        if g.user is None:
            return False

        # Valid role
        return g.user.has_role('superuser')

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            user_id = "unknown" if g.user is None else g.user.userId
            accessLogger.info(
                f'Unauthorised user ({user_id}) attempted to access admin')
            return redirect(url_for('auth.login'))

# Override model views for admin to prevent unauthorised access


class MyModelView(ModelView):
    def is_accessible(self):
        # Get current user
        if g.user is None:
            return False

        # Valid role
        return g.user.has_role('superuser')

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            user_id = "unknown" if g.user is None else g.user.userId
            accessLogger.info(
                f'Unauthorised user ({user_id}) attempted to access admin')
            return redirect(url_for('auth.login'))


# Admin front end
adminView = Admin(app, template_mode="bootstrap3",
                  index_view=MyAdminIndexView())

adminView.add_link(MenuLink(name='Main Site', url='/'))
adminView.add_link(MenuLink(name='Logout', url='/auth/logout'))

adminView.add_view(MyModelView(User, db.session))
adminView.add_view(MyModelView(Movie, db.session))
adminView.add_view(MyModelView(Group, db.session))
adminView.add_view(MyModelView(Role, db.session))
adminView.add_view(MyModelView(MovieChoice, db.session))

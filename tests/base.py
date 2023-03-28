import json

from flask_testing import TestCase

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        """
        Create an instance of the app with the testing configuration
        :return:
        """
        app.config.from_object('app.config.TestingConfig')
        return app

    def setUp(self):
        """
        Create the database
        :return:
        """
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """
        Drop the database tables and also remove the session
        :return:
        """
        db.session.remove()
        db.drop_all()

    def register_user(self, email, username, password):
        """
        Helper method for registering a user with dummy data
        :return:
        """
        return self.client.post(
            '/register',
            data=dict(email=email, username=username, password=password, confirm_password=password),
            follow_redirects=True
        )

    def login_user(self, email, password):
        """
        Helper method for log a user in
        :return:
        """
        return self.client.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

import json
import unittest

from app import app, bcrypt, db
from app.models import User
from tests.base import BaseTestCase


class TestAuth(BaseTestCase):
    def test_get_register(self):
        """
        Tests GET request to the /register route to assert the registration page is
        returned.
        """
        response = self.client.get("/register")

        assert response is not None
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_post_register(self):
        """
        Test POST request to the /register route to assert the user is successfully
        registered.
        """
        response = self.register_user('test@gmail.com', 'test', 'test123')

        assert response is not None
        assert response.status_code == 200
        assert b"Successfully registered." in response.data

    def test_get_login(self):
        """
        Test GET request to the /login route to assert the login page is returned.
        """
        response = self.client.get("/login")

        assert response is not None
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_post_login(self):
        """
        Test POST request to the /login route to assert the user is successfully logged
        in.
        """
        self.register_user('test@gmail.com', 'test', 'test123')
        response = self.login_user('test@gmail.com', 'test123')

        assert response is not None
        assert response.status_code == 200
        assert b"Successfully logged in" in response.data

    def test_post_logout(self):
        """
        Test POST request to the /logout route to assert the user is successfully
        logged out.
        """
        self.register_user('test@gmail.com', 'test', 'test123')
        self.login_user('test@gmail.com', 'test123')

        response = self.client.post("/logout", follow_redirects=True)

        assert response is not None
        assert response.status_code == 200
        assert b"Successfully logged out" in response.data


if __name__ == '__main__':
    unittest.main()

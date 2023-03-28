import json
import time
import unittest

from app import db
from app.models.user import User
from tests.base import BaseTestCase


class TestAuthBluePrint(BaseTestCase):
    def test_user_registration(self):
        """
        Test a user is successfully created through the api
        :return:
        """
        with self.client:
            response = self.register_user('example@gmail.com', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_registration_fails_if_content_type_not_json(self):
        """
        Test the content type is application/json
        :return:
        """
        with self.client:
            response = self.register_user_with_wrong_request_content_type('example@gmail.com', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(data['message'] == 'Content-type must be json')
            self.assertEqual(response.status_code, 400)

    def test_user_registration_missing_email_or_and_password(self):
        """
        Test that the email and password are set when sending the request
        :return:
        """
        with self.client:
            response = self.register_user("", "")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(
                data['message'] == 'Missing or wrong email format or password is less than eight characters')

    def test_user_email_validity(self):
        """
        Check that the user has supplied a valid email address.
        :return:
        """
        with self.client:
            response = self.register_user('john', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(
                data['message'] == 'Missing or wrong email format or password is less than eight characters')

    def test_user_password_length_is_greater_than_eight_characters(self):
        with self.client:
            response = self.register_user('john@gmail.com', '123')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(
                data['message'] == 'Missing or wrong email format or password is less than eight characters')

    def test_user_is_already_registered(self):
        """
        Test that the user already exists.
        :return:
        """
        user = User('example@gmail.com', '12345678')
        db.session.add(user)
        db.session.commit()

        with self.client:
            response = self.register_user('example@gmail.com', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Failed, User already exists, Please sign in')
            self.assertEqual(response.status_code, 409)

    def test_user_can_login(self):
        """
        Register and login in a user
        :return:
        """
        with self.client:
            self.register_and_login_in_user()

    def test_login_request_payload_is_json(self):
        """
        Test that the content type is application/json
        :return:
        """
        with self.client:
            response = self.client.post(
                'v1/auth/login',
                content_type='application/javascript',
                data=json.dumps(dict(email='example@gmail.com', password='12345678')))
            data = json.loads(response.data.decode())
            self.assertTrue(response.content_type == 'application/json',
                            msg='The content type must be application/json')
            self.assertTrue(response.status_code, 202)
            self.assertTrue(data['status'] == 'failed', msg='failed must be returned')
            self.assertTrue(data['message'] == 'Content-type must be json', msg='Check the returned message')

    def test_login_has_incorrect_email_and_valid_length_password(self):
        """
        Test the email of the user trying to login is valid and the password length is greater than 4 characters
        :return:
        """
        with self.client:
            response = self.login_user('johngmail.com', '12345678')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(response.content_type == 'application/json')
            self.assertTrue(data['status'] == 'failed', msg='Status should be failed')
            self.assertTrue(
                data['message'] == 'Missing or wrong email format or password is less than eight characters')

    def test_user_trying_to_login_does_not_exist_or_passwords_do_not_much(self):
        """
        Test that the user does not exist or the password is incorrect
        :return:
        """
        with self.client:
            response = self.login_user('john@gmail.com', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'User does not exist or password is incorrect')

    def test_valid_user_log_out(self):
        """
        Test that a user is logged out with a valid auth token
        :return:
        """
        with self.client:
            # Register and login user
            login_data = self.register_and_login_in_user()
            # Logout user
            logout_response = self.logout_user(login_data['auth_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(logout_data['status'] == 'success')
            self.assertTrue(logout_data['message'] == 'Successfully logged out')

    def test_expired_user_token_user_log_out(self):
        """
        Try to log out a user whose auth token has expired.
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            # Pause for 3 seconds
            time.sleep(self.app.config['AUTH_TOKEN_EXPIRATION_TIME_DURING_TESTS'])
            # Logout user
            logout_response = self.logout_user(login_data['auth_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertTrue(logout_data['status'] == 'failed')
            self.assertTrue(logout_data['message'] == 'Signature expired, Please sign in again')
            self.assertEqual(logout_response.status_code, 401)

    def test_log_out_request_contains_an_authorization_header(self):
        """
        Test that the authorization header is set
        :return:
        """
        with self.client:
            response = self.client.post(
                'v1/auth/logout',
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Provide an authorization header')
            self.assertEqual(response.status_code, 400)

    def test_log_out_has_a_valid_token(self):
        """
        Test that a valid authorization token has been sent within the header
        :return:
        """
        with self.client:
            response = self.client.post(
                'v1/auth/logout',
                headers=dict(Authorization='Bearersdfsdvfj.bvdfvbdfxcvxcxcv')
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Provide a valid auth token')
            self.assertEqual(response.status_code, 401)

    def test_user_token_was_blacklisted(self):
        """
        Test that the auth token has already been added to the Blacklisted tokens table,
        so a user cannot log out.
        :return:
        """
        with self.client:
            # Register and login user
            login_data = self.register_and_login_in_user()
            # Logout user
            logout_response = self.logout_user(login_data['auth_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(logout_data['status'] == 'success')
            self.assertTrue(logout_data['message'] == 'Successfully logged out')

            logout_again_response = self.logout_user(login_data['auth_token'])
            logout_again_data = json.loads(logout_again_response.data.decode())
            self.assertEqual(logout_again_response.status_code, 401)
            self.assertTrue(logout_again_data['status'] == 'failed')
            self.assertTrue(logout_again_data['message'] == 'Token was Blacklisted, Please login In')

    def register_and_login_in_user(self):
        """
        Helper method to sign up and login a user
        :return: Json login response
        """
        reg_response = self.register_user('john@gmail.com', '12345678')
        data = json.loads(reg_response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully registered')
        self.assertTrue(data['auth_token'])
        self.assertTrue(reg_response.content_type == 'application/json')
        self.assertEqual(reg_response.status_code, 201)
        # Login the user
        login_response = self.client.post(
            'v1/auth/login',
            data=json.dumps(dict(email='john@gmail.com', password='12345678')),
            content_type='application/json'
        )
        login_data = json.loads(login_response.data.decode())
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_data['auth_token'])
        self.assertTrue(login_data['status'] == 'success')
        self.assertTrue(login_data['message'] == 'Successfully logged in')
        self.assertTrue(login_response.content_type == 'application/json')
        return login_data

    def logout_user(self, token):
        """
        Helper method to log out a user
        :param token: Auth token
        :return:
        """
        logout_response = self.client.post(
            'v1/auth/logout',
            headers=dict(Authorization='Bearer ' + token)
        )
        return logout_response

    def register_user_with_wrong_request_content_type(self, email, password):
        """
        Helper method to register a user using a wrong content-type
        :param email: Email
        :param password: Password
        :return:
        """
        return self.client.post(
            'v1/auth/register',
            content_type='application/javascript',
            data=json.dumps(dict(email=email, password=password)))

    def login_user(self, email, password):
        """
        Helper method to login a user
        :param email: Email
        :param password: Password
        :return:
        """
        return self.client.post(
            'v1/auth/login',
            content_type='application/json',
            data=json.dumps(dict(email=email, password=password)))

    def test_user_can_reset_password(self):
        """
        Test that a password is successfully reset.
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='12345678', newPassword='09876543', passwordConfirmation='09876543')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['status'] == 'success')
            self.assertTrue(res['message'] == 'Password reset successfully')

    def test_request_fails_if_content_type_not_json(self):
        """
        Test a request fails if content type is not json
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='12345678', newPassword='098765',
                                     passwordConfirmation='098765')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Content type must be json')

    def test_old_password_supplied_by_user_is_incorrect(self):
        """
        Test that the user supplied an incorrect password
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                content_type='application/json',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='13456', newPassword='098765',
                                     passwordConfirmation='098765')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Incorrect password')

    def test_some_attributes_are_not_in_the_requested(self):
        """
        Test that some attributes are not included in the request.
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                content_type='application/json',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='12345678', newPassword='098765')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Missing required attributes')

    def test_that_new_password_does_not_match_confirmation(self):
        """
        Test that the new password does not match the password confirmation.
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='12345678', newPassword='098765',
                                     passwordConfirmation='09865')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'New Passwords do not match')

    def test_failed_status_when_new_password_is_less_than_eight_characters(self):
        """
        Test that a failed status message is returned when new password is less than eight characters long
        :return:
        """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['auth_token']
            response = self.client.post(
                'v1/auth/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='12345678', newPassword='0987', passwordConfirmation='0987')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'New password should be at least eight characters long')


if __name__ == '__main__':
    unittest.main()

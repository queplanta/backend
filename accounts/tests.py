import json

from django.test import TestCase


class AccountsTest(TestCase):
    def setUp(self):
        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($auth: RegisterInput!) {
                            register(input: $auth) {
                                clientMutationId,
                                user {
                                    firstName
                                }
                            }
                        }
                        ''',
                'variables': {
                    'auth': {
                        'clientMutationId': 'mutation1',
                        'name': 'Alisson',
                        'username': 'alisson',
                        'password': 'patricio',
                        'email': 'eu@alisson.net'
                    }
                }
            }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'register': {
                    'user': {
                        'firstName': 'Alisson'
                    },
                    'clientMutationId': 'mutation1'
                },
            }
        })
        self.assertFalse('sessionid' in response.cookies)


    def _do_login(self, password='patricio'):
        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($auth: AuthenticateInput!) {
                            authenticate(input: $auth) {
                                clientMutationId,
                                viewer {
                                    me {
                                        firstName
                                        isAuthenticated
                                    }
                                }
                            }
                        }
                        ''',
                'variables': {
                    'auth': {
                        'clientMutationId': 'mutation2',
                        'username': 'alisson',
                        'password': password,
                    }
                }
            }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'authenticate': {
                    'viewer': {
                        'me': {
                            'firstName': 'Alisson',
                            'isAuthenticated': True
                        },
                    },
                    'clientMutationId': 'mutation2'
                },
            }
        })
        self.assertTrue('sessionid' in response.cookies)
        return response


    def test_login_success(self):
        self._do_login()
        
        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        {
                            viewer {
                                me {
                                    firstName
                                    isAuthenticated
                                }
                            }
                        }
                        ''',
            }))
        self.assertEqual(response.json(), {
            'data': {
                'viewer': {
                    'me': {
                        'firstName': 'Alisson',
                        'isAuthenticated': True
                    },
                },
            }
        })

    def test_login_fail(self):
        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($auth: AuthenticateInput!) {
                            authenticate(input: $auth) {
                                clientMutationId,
                                viewer {
                                    me {
                                        isAuthenticated
                                    }
                                }
                                errors {
                                    key
                                    message
                                }
                            }
                        }
                        ''',
                'variables': {
                    'auth': {
                        'clientMutationId': 'mutation2',
                        'username': 'alisson',
                        'password': '123456',
                    }
                }
            }))

        from django.contrib.auth.forms import AuthenticationForm

        self.assertEqual(response.status_code, 200)
        expected = {
            'data': {
                'authenticate': {
                    'viewer': {
                        'me': None
                    },
                    'clientMutationId': 'mutation2',
                    'errors': [{
                        'key': 'invalid_login',
                        'message': AuthenticationForm.error_messages['invalid_login'] % {
                            'username': 'username',
                            'password': 'password'
                        }
                    }]
                },
            }
        }
        self.assertEqual(response.json(), expected)
        self.assertFalse('sessionid' in response.cookies)

    def test_logout(self):
        self._do_login()

        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($auth: DeauthenticateInput!) {
                            deauthenticate(input: $auth) {
                                clientMutationId,
                                viewer {
                                    me {
                                        firstName
                                        isAuthenticated
                                    }
                                }
                            }
                        }
                        ''',
                'variables': {
                    'auth': {
                        'clientMutationId': 'mutation3',
                    }
                }
            }))



        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'deauthenticate': {
                    'viewer': {
                        'me': None,
                    },
                    'clientMutationId': 'mutation3'
                },
            }
        })
        self.assertTrue('sessionid' in response.cookies)

    def test_password_change(self):
        self._do_login()

        def change_password(old, new1, new2):
            return self.client.post('/graphql', content_type='application/json',
                data=json.dumps({
                    'query': '''
                            mutation M($auth: PasswordChangeInput!) {
                                mePasswordChange(input: $auth) {
                                    clientMutationId,
                                    errors {
                                        key
                                    }
                                }
                            }
                            ''',
                    'variables': {
                        'auth': {
                            'clientMutationId': 'passwordchange',
                            'oldPassword': old,
                            'newPassword1': new1,
                            'newPassword2': new2,
                        }
                    }
                }))

        # wrong password test
        response = change_password('wrongpassword', 'n3wp4ssw0rd', 'n3wp4ssw0rd')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'mePasswordChange': {
                    'errors': [{'key': 'password_incorrect'}],
                    'clientMutationId': 'passwordchange'
                },
            }
        })

        # new passwords doenst match
        response = change_password('patricio', 'n3wp4ssw0rd', 'newp4ssw0rd')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'mePasswordChange': {
                    'errors': [{'key': 'password_mismatch'}],
                    'clientMutationId': 'passwordchange'
                },
            }
        })

        # success
        response = change_password('patricio', 'n3wp4ssw0rd', 'n3wp4ssw0rd')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'mePasswordChange': {
                    'errors': [],
                    'clientMutationId': 'passwordchange'
                },
            }
        })

        self._do_login(password='n3wp4ssw0rd')
        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        {
                            viewer {
                                me {
                                    firstName
                                    isAuthenticated
                                }
                            }
                        }
                        ''',
            }))
        self.assertEqual(response.json(), {
            'data': {
                'viewer': {
                    'me': {
                        'firstName': 'Alisson',
                        'isAuthenticated': True
                    },
                },
            }
        })

    def test_password_reset(self):
        def password_reset_email(email):
            return self.client.post('/graphql', content_type='application/json',
                data=json.dumps({
                    'query': '''
                            mutation M($auth: PasswordResetEmailInput!) {
                                mePasswordResetEmail(input: $auth) {
                                    clientMutationId,
                                    errors {
                                        key
                                    }
                                }
                            }
                            ''',
                    'variables': {
                        'auth': {
                            'clientMutationId': 'passwordresetemail',
                            'email': email,
                        }
                    }
                }))

        def password_reset_complete(uidb64, token, new_password1, new_password2):
            return self.client.post('/graphql', content_type='application/json',
                data=json.dumps({
                    'query': '''
                            mutation M($auth: PasswordResetCompleteInput!) {
                                mePasswordResetComplete(input: $auth) {
                                    clientMutationId,
                                    errors {
                                        key
                                    }
                                }
                            }
                            ''',
                    'variables': {
                        'auth': {
                            'clientMutationId': 'passwordresetcomplete',
                            'uidb64': uidb64,
                            'token': token,
                            'newPassword1': new_password1,
                            'newPassword2': new_password2
                        }
                    }
                }))

        # get token

        response = password_reset_email('eu@alisson.net')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'mePasswordResetEmail': {
                    'errors': [],
                    'clientMutationId': 'passwordresetemail'
                },
            }
        })

        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)

        import re
        from backend.urls import URL_PASSWORD_RESET
        r = re.compile(URL_PASSWORD_RESET)

        reset_url = r.search(mail.outbox[0].body)

        self.assertTrue(reset_url is not None)

        uidb64 = reset_url.group('uidb64')
        token = reset_url.group('token')

        # complete, change password

        response = password_reset_complete(uidb64, token, 'n3wp4ssw0rd2', 'n3wp4ssw0rd2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'mePasswordResetComplete': {
                    'errors': [],
                    'clientMutationId': 'passwordresetcomplete'
                },
            }
        })

        self._do_login(password='n3wp4ssw0rd2')

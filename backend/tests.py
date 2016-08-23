import json

from django.test import TestCase

from accounts.models import User


class UserTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.user = User(
            username='alisson',
            email='eu@alisson.net'
        )
        self.user.set_password('patricio')
        self.user.save()

    def _do_login(self):
        response = self.client.post(
            '/graphql', content_type='application/json', data=json.dumps({
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
                        'password': 'patricio',
                    }
                }
            }))
        self.assertTrue(
            response.json()['data']['authenticate']
            ['viewer']['me']['isAuthenticated'])

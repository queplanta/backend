import json

from django.test import TestCase

from accounts.models import User


class GraphQLTest(TestCase):
    def graphql(self, data, client=None):
        if not client:
            client = self.client
        return client.post('/graphql',
                           content_type='application/json',
                           data=json.dumps(data))


class UserTestCase(GraphQLTest):
    def setUp(self):
        self.maxDiff = None
        self.user = User(
            username='alisson',
            email='eu@alisson.net'
        )
        self.user.set_password('patricio')
        self.user.save(request=None)

        self.user_2 = User(
            username='lanna',
            email='lanna@naturebismo.com'
        )
        self.user_2.set_password('patricia')
        self.user_2.save(request=None)

    def _do_login(self, username='alisson', password='patricio'):
        response = self.graphql({
            'query': '''
                    mutation M($auth: AuthenticateInput!) {
                        authenticate(input: $auth) {
                            clientMutationId,
                            viewer {
                                me {
                                    username
                                    isAuthenticated
                                }
                            }
                        }
                    }
                    ''',
            'variables': {
                'auth': {
                    'clientMutationId': 'mutation2',
                    'username': username,
                    'password': password,
                }
            }
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {
                'authenticate': {
                    'viewer': {
                        'me': {
                            'username': username,
                            'isAuthenticated': True
                        },
                    },
                    'clientMutationId': 'mutation2'
                },
            }
        })
        self.assertTrue('sessionid' in response.cookies)
        return response

    def _do_login_2(self, username='lanna', password='patricia'):
        return self._do_login(username, password)

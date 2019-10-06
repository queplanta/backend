import json

from django.test import TestCase

from accounts.models import User


class GraphQLTest(TestCase):
    def graphql(self, data, client=None, content_type='application/json'):
        if not client:
            client = self.client
        if content_type == 'application/json':
            data = json.dumps(data)
        else:
            form_data = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    form_data[key] = json.dumps(value)
                else:
                    form_data[key] = value
            data = form_data
        return client.post('/graphql',
                           content_type=content_type,
                           data=data)


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
            email='lanna@queplanta.com'
        )
        self.user_2.set_password('patricia')
        self.user_2.save(request=None)

        self.user_admin = User(
            username='admin',
            email='admin@queplanta.com',
            is_superuser=True
        )
        self.user_admin.set_password('admin')
        self.user_admin.save(request=None)

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

    def _do_login_admin(self, username='admin', password='admin'):
        return self._do_login(username, password)

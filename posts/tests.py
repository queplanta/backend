import json

from django.test import TestCase

from accounts.models import User


class PostsTest(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.user = User(
            username='alisson',
            email='eu@alisson.net'
        )
        self.user.set_password('patricio')
        self.user.save()

    def _do_login(self):
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
                        'password': 'patricio',
                    }
                }
            }))
        self.assertTrue(response.json()['data']['authenticate']['viewer']['me']['isAuthenticated'])

    def _do_create_page(self, client, post):
        return client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($input_0: PostCreateInput!) {
                            postCreate(input: $input_0) {
                                clientMutationId,
                                post {
                                    url,
                                    title,
                                    body,
                                    publishedAt,
                                    revisionCreated {
                                        author {
                                            username
                                        }
                                    },
                                    tags {
                                        edges {
                                            node {
                                                title,
                                                slug
                                            }
                                        }
                                    }
                                },
                                errors {
                                    key,
                                    message,
                                },
                            }
                        }
                        ''',
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'url': post['url'],
                        'title': post['title'],
                        'body': post['body'],
                        'tags': post['tags'],
                        'publishedAt': post['publishedAt'],
                    }
                }
            }))

    def test_create_page(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37+00:00',
            'tags': 'tést tãg, Outra Tag',
        }

        # without login should fail
        response = self._do_create_page(self.client, post)

        from backend.fields import LoginRequiredError
        login_required_error = LoginRequiredError()

        expected = {
            'data': {
                'postCreate': {
                    'post': None,
                    'clientMutationId': '1',
                    'errors': [{
                        'key': login_required_error.key,
                        'message': str(login_required_error.message),
                    }]
                },
            }
        }
        self.assertEqual(response.json(), expected)

        # logged in
        self._do_login()
        response = self._do_create_page(self.client, post)
        expected = {
            'data': {
                'postCreate': {
                    'post': {
                        'url': post['url'],
                        'title': post['title'],
                        'body': post['body'],
                        'publishedAt': post['publishedAt'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            }
                        },
                        'tags': {
                            'edges': [
                                {'node': {
                                    'title': 'tést tãg',
                                    'slug': 'test-tag'
                                }},
                                {'node': {
                                    'title': 'Outra Tag',
                                    'slug': 'outra-tag'
                                }}
                            ]
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

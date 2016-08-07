import json

from django.test import TestCase

from accounts.models import User


class CommentsTest(TestCase):
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
                                    id
                                    document {
                                        id
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

    def test_comment(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37+00:00',
            'tags': 'tést tãg, Outra Tag',
        }

        comment = {
            'body': 'first comment',
        }

        self._do_login()
        response = self._do_create_page(self.client, post)
        postId = response.json()['data']['postCreate']['post']['document']['id']
        postId2 = response.json()['data']['postCreate']['post']['id']

        response = self.client.post('/graphql', content_type='application/json',
            data=json.dumps({
                'query': '''
                        mutation M($input_0: CommentCreateInput!) {
                            commentCreate(input: $input_0) {
                                clientMutationId,
                                parent {
                                    ... on Post {
                                        id
                                        comments {
                                            count
                                            edges {
                                                node {
                                                    body
                                                    revisionCreated {
                                                        author {
                                                            username
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
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
                        'body': comment['body'],
                        'parent': postId2,
                    }
                }
            }))

        expected = {
            'data': {
                'commentCreate': {
                    'parent': {
                        'id': postId2,
                        'comments': {
                            'count': 1,
                            'edges': [
                                {'node': {
                                    'body': comment['body'],
                                    'revisionCreated': {
                                        'author': {
                                            'username': self.user.username,
                                        }
                                    },
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

        response = self.client.post('/graphql',
            content_type='application/json',
            data=json.dumps({
                'query': '''
                        query($id: ID!) {
                            post(id: $id) {
                                document {
                                    id
                                },
                                comments {
                                    count,
                                    edges {
                                        node {
                                            body,
                                            revisionCreated {
                                                author {
                                                    username
                                                }
                                            }
                                            parent {
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        ''',
                'variables': {
                    'id': postId2
                }
            }))

        expected = {
            'data': {
                'post': {
                    'document': {
                        'id': postId,
                    },
                    'comments': {
                        'count': 1,
                        'edges': [
                            {'node': {
                                'body': comment['body'],
                                'revisionCreated': {
                                    'author': {
                                        'username': self.user.username,
                                    }
                                },
                                'parent': {
                                    'id': postId
                                },
                            }}
                        ]
                    },
                },
            }
        }
        self.assertEqual(response.json(), expected)

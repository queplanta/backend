import json

from django.test import TestCase

from accounts.models import User


class VotesTest(TestCase):
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
        self.assertTrue(response.json()['data']['authenticate']
                                       ['viewer']['me']['isAuthenticated'])

    def _do_create_page(self, client, post):
        return client.post(
            '/graphql', content_type='application/json', data=json.dumps({
                'query': '''
                    mutation M($input_0: PostCreateInput!) {
                        postCreate(input: $input_0) {
                            clientMutationId,
                            post {
                                id
                                voting {
                                    count
                                    mine {
                                        value
                                    }
                                }
                            },
                            errors {
                                code
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

    def test_vote(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37+00:00',
            'tags': 'tést tãg, Outra Tag',
        }

        self._do_login()
        response = self._do_create_page(self.client, post)
        post.update(response.json()['data']['postCreate']['post'])

        response = self.client.post(
            '/graphql', content_type='application/json', data=json.dumps({
                'query': '''
                    mutation M($input_0: VoteSetInput!) {
                        voteSet(input: $input_0) {
                            clientMutationId,
                            voting {
                                count
                                mine {
                                    value
                                }
                                votes {
                                    edges {
                                        node {
                                            value
                                            revisionCreated {
                                                author {
                                                    username
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            vote {
                                value
                                author {
                                    username
                                }
                            }
                            errors {
                                code
                            },
                        }
                    }
                    ''',
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'parent': post['id'],
                        'value': -1,
                    }
                }
            }))

        self.assertEqual(response.json(), {
            'data': {
                'voteSet': {
                    'voting': {
                        'count': 1,
                        'mine': {
                            'value': -1,
                        },
                        'votes': {
                            'edges': [
                                {'node': {
                                    'value': -1,
                                    'revisionCreated': {
                                        'author': {
                                            'username': self.user.username,
                                        }
                                    },
                                }}
                            ]
                        }
                    },
                    'vote': {
                        'value': -1,
                        'author': {
                            'username': self.user.username,
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        })

        # delete a vote
        response = self.client.post(
            '/graphql', content_type='application/json', data=json.dumps({
                'query': '''
                    query ($id_0: ID!) {
                        post(id: $id_0) {
                          voting {
                            mine {
                                id
                            }
                          }
                        }
                    }
                    ''',
                'variables': {
                    'id_0': post['id']
                }
            }))
        vote = response.json()['data']['post']['voting']['mine']

        response = self.client.post(
            '/graphql', content_type='application/json', data=json.dumps({
                'query': '''
                    mutation M($input_0: VoteDeleteInput!) {
                        voteDelete(input: $input_0) {
                            clientMutationId,
                            voteDeletedID
                            errors {
                                code
                            },
                        }
                    }
                    ''',
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'id': vote['id'],
                    }
                }
            }))

        response = self.client.post(
            '/graphql', content_type='application/json', data=json.dumps({
                'query': '''
                    query ($id_0: ID!) {
                        post(id: $id_0) {
                          voting {
                            count
                            mine {
                                id
                            }
                          }
                        }
                    }
                    ''',
                'variables': {
                    'id_0': post['id']
                }
            }))
        self.assertEqual(response.json(), {
            'data': {'post': {'voting': {'count': 0, 'mine': None}}}})

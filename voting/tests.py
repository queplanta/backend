from backend.tests import UserTestCase


class VotesTest(UserTestCase):
    def _do_create_page(self, client, post):
        return self.graphql({
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
        }, client=client)

    def test_vote(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37',
            'tags': 'tést tãg, Outra Tag',
        }

        self._do_login()
        response = self._do_create_page(self.client, post)
        post.update(response.json()['data']['postCreate']['post'])

        response = self.graphql({
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
                            parent {
                                owner {
                                    username
                                    reputation
                                }
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
        })

        self.assertEqual(response.json(), {
            'data': {
                'voteSet': {
                    'voting': {
                        'count': 1,
                        'mine': {
                            'value': -1
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
                        },
                        'parent': {
                            'owner': {
                                'reputation': 3,
                                'username': self.user.username,
                            }
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        })

        # delete a vote
        response = self.graphql({
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
        })
        vote = response.json()['data']['post']['voting']['mine']

        response = self.graphql({
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
        })

        response = self.graphql({
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
        })
        self.assertEqual(response.json(), {
            'data': {'post': {'voting': {'count': 0, 'mine': None}}}})

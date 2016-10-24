from backend.tests import UserTestCase


class WhatIsThisTest(UserTestCase):
    def setUp(self):
        super(WhatIsThisTest, self).setUp()

        self._do_login()

        node = {
            'title': 'Mangifera',
            'description': '',
            'rank': 'genus',
            'parent': None,
        }
        response = self._do_create_life_node(self.client, node)
        self.genus = response.json()['data']['lifeNodeCreate']['lifeNode']

        node = {
            'title': 'Mangifera indica',
            'description': 'The fruit tastes like heaven',
            'rank': 'species',
            'parent': self.genus['id'],
        }
        self.species = self._do_create_life_node(self.client, node)

    def test_create_what(self):
        response = self.graphql({
            'query': '''
                mutation M($input_0: WhatIsThisCreateInput!) {
                    whatIsThisCreate(input: $input_0) {
                        clientMutationId,
                        whatisthis {
                            node {
                                id
                                when,
                                where,
                                notes,
                                author {
                                    username
                                }
                                revisionCreated {
                                    author {
                                        username
                                    }
                                },
                            }
                        },
                        errors {
                            code,
                        },
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'when': 'ontem',
                    'where': 'mariana, mg',
                    'notes': 'na baira da estrada, florindo',
                }
            }
        })

        expected = {
            'data': {
                'whatIsThisCreate': {
                    'whatisthis': {
                        'node': {
                            'id': response.json()['data']['whatIsThisCreate']['whatisthis']['node']['id'],
                            'when': 'ontem',
                            'where': 'mariana, mg',
                            'notes': 'na baira da estrada, florindo',
                            'author': {
                                'username': self.user.username,
                            },
                            'revisionCreated': {
                                'author': {
                                    'username': self.user.username,
                                }
                            }
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def _do_create_life_node(self, client, node):
        return self.graphql({
            'query': '''
                mutation M($input_0: LifeNodeCreateInput!) {
                    lifeNodeCreate(input: $input_0) {
                        clientMutationId,
                        lifeNode {
                            id
                            title,
                            description,
                            rank,
                            revisionCreated {
                                author {
                                    username
                                }
                            },
                            parent {
                                id,
                                title,
                                rank
                            }
                        },
                        errors {
                            code,
                        },
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'title': node['title'],
                    'description': node['description'],
                    'rank': node['rank'],
                    'parent': node['parent'],
                }
            }
        }, client=client)

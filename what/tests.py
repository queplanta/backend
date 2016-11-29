from backend.tests import UserTestCase
from django.test.client import MULTIPART_CONTENT


class WhatIsThisTest(UserTestCase):
    def setUp(self):
        super(WhatIsThisTest, self).setUp()

        self._do_login()

        node = {
            'title': 'Mangifera',
            'description': '',
            'rank': 'GENUS',
            'parent': None,
        }
        response = self._do_create_life_node(self.client, node)
        self.genus = response.json()['data']['lifeNodeCreate']['lifeNode']

        node = {
            'title': 'Mangifera indica',
            'description': 'The fruit tastes like heaven',
            'rank': 'SPECIES',
            'parent': self.genus['id'],
        }
        response = self._do_create_life_node(self.client, node)
        self.species = response.json()['data']['lifeNodeCreate']['lifeNode']

    def test_create_what(self):
        with open('public/default_user_avatar.jpg', 'rb') as image1, open('public/default_user_avatar.jpg', 'rb') as image2:
            response = self.graphql({
                'query': '''
                    mutation M($input_0: WhatIsThisCreateInput!) {
                        whatIsThisCreate(input: $input_0) {
                            clientMutationId,
                            whatIsThis {
                                node {
                                    id
                                    when,
                                    where,
                                    notes,
                                    images {
                                        edges {
                                            node {
                                                id
                                            }
                                        }
                                    }
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
                                location,
                                message
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
                },
                'images': [image1, image2],
            }, content_type=MULTIPART_CONTENT)

        whatisthis = response.json()['data']['whatIsThisCreate']['whatIsThis']['node']

        expected = {
            'data': {
                'whatIsThisCreate': {
                    'whatIsThis': {
                        'node': {
                            'id': whatisthis['id'],
                            'when': 'ontem',
                            'where': 'mariana, mg',
                            'notes': 'na baira da estrada, florindo',
                            'author': {
                                'username': self.user.username,
                            },
                            'images': {
                                'edges': [
                                    whatisthis['images']['edges'][0],
                                    whatisthis['images']['edges'][1],
                                ],
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

        response = self._do_create_suggestion_id({
            'whatIsThis': whatisthis['id'],
            'identification': self.genus['id'],
            'notes': 'tenho uma no meu quintal'
        })

        suggestionID1 = response.json()['data']['suggestionIDCreate']['suggestionID']['node']

        expected = {
            'data': {
                'suggestionIDCreate': {
                    'suggestionID': {
                        'node': {
                            'id': suggestionID1['id'],
                            'whatIsThis': {
                                'id': whatisthis['id'],
                            },
                            'identification': {
                                'id': self.genus['id'],
                            },
                            'notes': 'tenho uma no meu quintal',
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

        response = self._do_create_suggestion_id({
            'whatIsThis': whatisthis['id'],
            'identification': self.species['id'],
            'notes': 'minha vó tem uma'
        })

        suggestionID2 = response.json()['data']['suggestionIDCreate']['suggestionID']['node']

        response = self.graphql({
            'query': '''
                query($id: ID!) {
                    whatIsThis(id: $id) {
                        id,
                        suggestions {
                            edges {
                                node {
                                    id,
                                    identification {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': whatisthis['id']
            }
        })

        expected = {
            'data': {
                'whatIsThis': {
                    'id': whatisthis['id'],
                    'suggestions': {
                        'edges': [
                            {'node': {
                                'id': suggestionID1['id'],
                                'identification': {
                                    'id': self.genus['id']
                                }
                            }},
                            {'node': {
                                'id': suggestionID2['id'],
                                'identification': {
                                    'id': self.species['id']
                                }
                            }}
                        ]
                    },
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def _do_create_suggestion_id(self, suggestionID):
        return self.graphql({
            'query': '''
                mutation M($input_0: SuggestionIDCreateInput!) {
                    suggestionIDCreate(input: $input_0) {
                        clientMutationId,
                        suggestionID {
                            node {
                                id
                                identification {
                                    id
                                },
                                whatIsThis {
                                    id
                                },
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
                    'whatIsThis': suggestionID['whatIsThis'],
                    'identification': suggestionID['identification'],
                    'notes': suggestionID['notes'],
                }
            }
        })

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

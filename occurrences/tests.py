from backend.tests import UserTestCase
from django.test.client import MULTIPART_CONTENT


class OccurrenceTest(UserTestCase):
    def setUp(self):
        super(OccurrenceTest, self).setUp()

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

    def test_create_occurrence(self):
        with open('public/default_user_avatar.jpg', 'rb') as image1, open('public/default_user_avatar.jpg', 'rb') as image2:
            response = self.graphql({
                'query': '''
                    mutation M($input_0: OccurrenceCreateInput!) {
                        occurrenceCreate(input: $input_0) {
                            clientMutationId,
                            occurrence {
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
                                    location { lat, lng }
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
                        'location': {
                            'lat': -43.9678283,
                            'lng': -19.8539275,
                        }
                    }
                },
                'images': [image1, image2],
            }, content_type=MULTIPART_CONTENT)

        occurrence = response.json()['data']['occurrenceCreate']['occurrence']['node']

        expected = {
            'data': {
                'occurrenceCreate': {
                    'occurrence': {
                        'node': {
                            'id': occurrence['id'],
                            'when': 'ontem',
                            'where': 'mariana, mg',
                            'notes': 'na baira da estrada, florindo',
                            'author': {
                                'username': self.user.username,
                            },
                            'images': {
                                'edges': [
                                    occurrence['images']['edges'][0],
                                    occurrence['images']['edges'][1],
                                ],
                            },
                            'revisionCreated': {
                                'author': {
                                    'username': self.user.username,
                                }
                            },
                            'location': {
                                'lat': -43.9678283,
                                'lng': -19.8539275,
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
            'occurrence': occurrence['id'],
            'identity': self.genus['id'],
            'notes': 'tenho uma no meu quintal'
        })

        suggestionID1 = response.json()['data']['suggestionIDCreate']['suggestionID']['node']

        expected = {
            'data': {
                'suggestionIDCreate': {
                    'suggestionID': {
                        'node': {
                            'id': suggestionID1['id'],
                            'occurrence': {
                                'id': occurrence['id'],
                            },
                            'identity': {
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
            'occurrence': occurrence['id'],
            'identity': self.species['id'],
            'notes': 'minha vó tem uma'
        })

        suggestionID2 = response.json()['data']['suggestionIDCreate']['suggestionID']['node']

        response = self.graphql({
            'query': '''
                query($id: ID!) {
                    occurrence(id: $id) {
                        id,
                        suggestions {
                            edges {
                                node {
                                    id,
                                    identity {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': occurrence['id']
            }
        })

        expected = {
            'data': {
                'occurrence': {
                    'id': occurrence['id'],
                    'suggestions': {
                        'edges': [
                            {'node': {
                                'id': suggestionID1['id'],
                                'identity': {
                                    'id': self.genus['id']
                                }
                            }},
                            {'node': {
                                'id': suggestionID2['id'],
                                'identity': {
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
                                identity {
                                    id
                                },
                                occurrence {
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
                    'occurrence': suggestionID['occurrence'],
                    'identity': suggestionID['identity'],
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

from backend.tests import UserTestCase
from django.test.client import MULTIPART_CONTENT


class SowingTest(UserTestCase):
    def setUp(self):
        super(SowingTest, self).setUp()

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

    def test_create_sowing(self):
        with open('public/default_user_avatar.jpg', 'rb') as image1, open('public/default_user_avatar.jpg', 'rb') as image2:
            response = self.graphql({
                'query': """
                    mutation M($input_0: SowingCreateInput!) {
                        sowingCreate(input: $input_0) {
                            clientMutationId,
                            sowing {
                                node {
                                    id
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
                                    location { type, coordinates }
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
                    """,
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'where': 'mariana, mg',
                        'notes': 'na baira da estrada, florindo',
                        'location': {
                            'type': 'Point',
                            'coordinates': [-19.8539275, -43.9678283],
                        },
                        'species': [self.species['id'], self.genus['id']],
                    }
                },
                'images': [image1, image2],
            }, content_type=MULTIPART_CONTENT)

        sowing = response.json()['data']['sowingCreate']['sowing']['node']

        expected = {
            'data': {
                'sowingCreate': {
                    'sowing': {
                        'node': {
                            'id': sowing['id'],
                            'where': 'mariana, mg',
                            'notes': 'na baira da estrada, florindo',
                            'author': {
                                'username': self.user.username,
                            },
                            'images': {
                                'edges': [
                                    sowing['images']['edges'][0],
                                    sowing['images']['edges'][1],
                                ],
                            },
                            'revisionCreated': {
                                'author': {
                                    'username': self.user.username,
                                }
                            },
                            'location': {
                                'type': 'Point',
                                'coordinates': [-19.8539275, -43.9678283],
                            }
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_create_sowing_guest_with_name_email(self):
        # ensure we are logged out for a guest submission
        self.client.logout()

        with open('public/default_user_avatar.jpg', 'rb') as image1:
            response = self.graphql({
                'query': """
                    mutation M($input_0: SowingCreateInput!) {
                        sowingCreate(input: $input_0) {
                            clientMutationId,
                            sowing {
                                node {
                                    id
                                    where
                                    notes
                                    author { username }
                                    authorName
                                    authorEmail
                                    images { edges { node { id } } }
                                }
                            }
                            errors { code location message }
                        }
                    }
                """,
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'where': 'bairro central',
                        'notes': 'semeadura comunitária',
                        'species': [self.species['id']],
                        'name': 'Convidado',
                        'email': 'convidado@example.com',
                    }
                },
                'images': [image1],
            }, content_type=MULTIPART_CONTENT)

        sowing = response.json()['data']['sowingCreate']['sowing']['node']

        expected = {
            'data': {
                'sowingCreate': {
                    'sowing': {
                        'node': {
                            'id': sowing['id'],
                            'where': 'bairro central',
                            'notes': 'semeadura comunitária',
                            'author': None,
                            'authorName': 'Convidado',
                            'authorEmail': 'convidado@example.com',
                            'images': {
                                'edges': [sowing['images']['edges'][0]],
                            },
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None,
                }
            }
        }
        self.assertEqual(response.json(), expected)

    def _do_create_life_node(self, client, node):
        return self.graphql({
            'query': """
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
                """,
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

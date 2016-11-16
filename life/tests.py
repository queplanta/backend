from backend.tests import UserTestCase
from django.test.client import MULTIPART_CONTENT


class LifeNodeTest(UserTestCase):
    def _do_create(self, client, node, extra={}):
        query = {
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
                            commonNames,
                            gbifId,
                            images {
                                edges {
                                    node {
                                        id
                                    }
                                }
                            }
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
                    'commonNames': node['commonNames'],
                    'gbifId': node.get('gbifId'),
                    'imagesToAdd': node.get('imagesToAdd', []),
                }
            }
        }
        query.update(extra)
        return self.graphql(query, client=client, content_type=MULTIPART_CONTENT)

    def test_create(self):
        self._do_login()
        node = {
            'title': 'Mangifera',
            'description': '',
            'rank': 'genus',
            'parent': None,
            'commonNames': [],
        }
        response = self._do_create(self.client, node)
        parent = response.json()['data']['lifeNodeCreate']['lifeNode']

        with open('public/default_user_avatar.jpg', 'rb') as image1, open('public/default_user_avatar.jpg', 'rb') as image2:
            node = {
                'title': 'Mangifera indica',
                'description': 'The fruit tastes like heaven',
                'rank': 'species',
                'parent': parent['id'],
                'gbifId': 3190638,
                'commonNames': [{
                    'name': 'Mangueira',
                    'language': 'por'
                }],
                'imagesToAdd': [
                    {
                        'field': 'image_1',
                        'description': 'description of a mango tree photography'
                    },
                    {
                        'field': 'image_2',
                        'description': 'description of a mango fruit photography'
                    }
                ]
            }
            response = self._do_create(self.client, node, {
                'image_1': image1,
                'image_2': image2
            })

        lifeNode = response.json()['data']['lifeNodeCreate']['lifeNode']
        expected = {
            'data': {
                'lifeNodeCreate': {
                    'lifeNode': {
                        'id': response.json()['data']['lifeNodeCreate']['lifeNode']['id'],
                        'title': node['title'],
                        'description': node['description'],
                        'rank': node['rank'],
                        'gbifId': node['gbifId'],
                        'commonNames': ['Mangueira'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            }
                        },
                        'images': {
                            'edges': [
                                lifeNode['images']['edges'][0],
                                lifeNode['images']['edges'][1],
                            ],
                        },
                        'parent': {
                            'id': parent['id'],
                            'title': parent['title'],
                            'rank': parent['rank'],
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_create_species(self):
        self._do_login()

        response = self.graphql({
            'query': '''
                mutation M($input_0: SpeciesCreateInput!) {
                    speciesCreate(input: $input_0) {
                        clientMutationId,
                        species {
                            id
                            title,
                            rank,
                            commonNames,
                            revisionCreated {
                                author {
                                    username
                                }
                            },
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
                    'species': 'Mimosa pudica',
                    'genus': 'Mimosa',
                    'family': 'Fabaceae',
                    'commonNames': 'dormideira, malícia, sensitiva, dorme-dorme'
                }
            }
        })

        expected = {
            'data': {
                'speciesCreate': {
                    'species': {
                        'id': response.json()['data']['speciesCreate']['species']['id'],
                        'title': 'Mimosa pudica',
                        'rank': 'species',
                        'commonNames': ['dorme-dorme', 'dormideira',
                                        'malícia', 'sensitiva'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            }
                        },
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

from backend.tests import UserTestCase


class LifeNodeTest(UserTestCase):
    def _do_create(self, client, node):
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
                            commonNames,
                            gbifId,
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
                }
            }
        }, client=client)

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

        node = {
            'title': 'Mangifera indica',
            'description': 'The fruit tastes like heaven',
            'rank': 'species',
            'parent': parent['id'],
            'gbifId': 3190638,
            'commonNames': [{
                'name': 'Mangueira',
                'language': 'por'
            }]
        }
        response = self._do_create(self.client, node)
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

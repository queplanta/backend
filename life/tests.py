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

    def test_create(self):
        self._do_login()
        node = {
            'title': 'Mangifera',
            'description': '',
            'rank': 'genus',
            'parent': None,
        }
        response = self._do_create(self.client, node)
        parent = response.json()['data']['lifeNodeCreate']['lifeNode']


        node = {
            'title': 'Mangifera indica',
            'description': 'The fruit tastes like heaven',
            'rank': 'species',
            'parent': parent['id'],
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

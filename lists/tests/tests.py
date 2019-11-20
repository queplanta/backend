from backend.tests import UserTestCase


class ListsTest(UserTestCase):
    def _do_create_list(self, client, llist):
        return self.graphql({
            'query': '''
                mutation M($input_0: ListCreateInput!) {
                    listCreate(input: $input_0) {
                        clientMutationId,
                        list {
                            id
                            url,
                            title,
                            description,
                            revisionCreated {
                                author {
                                    username
                                },
                                message
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
                    'url': llist['url'],
                    'title': llist['title'],
                    'description': llist['description'],
                    'revisionMessage': llist['revisionMessage']
                }
            }
        }, client=client)

    def test_create_list(self):
        self._do_login()
        llist = {
            'url': 'new-list-title',
            'title': 'new list title',
            'description': 'new list description',
            'revisionMessage': 'initial revision message'
        }
        response = self._do_create_list(self.client, llist)
        list_id = response.json()['data']['listCreate']['list']['id']
        expected = {
            'data': {
                'listCreate': {
                    'list': {
                        'id': list_id,
                        'url': llist['url'],
                        'title': llist['title'],
                        'description': llist['description'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            },
                            'message': llist['revisionMessage']
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

        # add item to list
        node = {
            'title': 'Mangifera',
            'description': '',
            'rank': 'GENUS',
            'parent': None
        }
        response = response = self.graphql({
            'query': '''
                mutation M($input_0: LifeNodeCreateInput!) {
                    lifeNodeCreate(input: $input_0) {
                        clientMutationId,
                        lifeNode {
                            id
                        }
                    }
                }''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'title': node['title'],
                    'description': node['description'],
                    'rank': node['rank'],
                    'parent': node['parent'],
                }
            }
        })
        node_id = response.json()['data']['lifeNodeCreate']['lifeNode']['id']

        response = self.graphql({
            'query': '''
                mutation M($input_0: ListAddItemInput!) {
                    listAddItem(input: $input_0) {
                        clientMutationId,
                        list {
                            id,
                            items {
                                notes
                                item {
                                    ... on LifeNode {
                                        title
                                    }
                                }
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
                    'listId': list_id,
                    'itemId': node_id,
                    'notes': 'note about the genus on this list'
                }
            }
        })
        expected = {
            'data': {
                'listAddItem': {
                    'list': {
                        'id': list_id,
                        'items': [{
                            'notes': 'note about the genus on this list',
                            'item': {
                                'title': node['title'],
                            }
                        }]
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

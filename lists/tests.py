from backend.tests import UserTestCase


class ListsTest(UserTestCase):
    def _do_create_list(self, client, llist):
        return self.graphql({
            'query': '''
                mutation M($input_0: ListCreateInput!) {
                    listCreate(input: $input_0) {
                        clientMutationId,
                        list {
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
        expected = {
            'data': {
                'listCreate': {
                    'list': {
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

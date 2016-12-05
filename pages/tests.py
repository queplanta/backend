from backend.tests import UserTestCase


class PagesTest(UserTestCase):
    def _do_create_page(self, client, page):
        return self.graphql({
            'query': '''
                mutation M($input_0: PageCreateInput!) {
                    pageCreate(input: $input_0) {
                        clientMutationId,
                        page {
                            url,
                            title,
                            body,
                            publishedAt,
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
                    'url': page['url'],
                    'title': page['title'],
                    'body': page['body'],
                    'publishedAt': page['publishedAt'],
                    'revisionMessage': page['revisionMessage']
                }
            }
        }, client=client)

    def test_create_page(self):
        self._do_login()
        page = {
            'url': 'new-page-title',
            'title': 'new page title',
            'body': 'new page content',
            'publishedAt': '2011-01-05T20:26:37',
            'revisionMessage': 'initial revision message'
        }
        response = self._do_create_page(self.client, page)
        expected = {
            'data': {
                'pageCreate': {
                    'page': {
                        'url': page['url'],
                        'title': page['title'],
                        'body': page['body'],
                        'publishedAt': page['publishedAt'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            },
                            'message': page['revisionMessage']
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

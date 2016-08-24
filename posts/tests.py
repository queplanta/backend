from backend.tests import UserTestCase
from backend.fields import LoginRequiredError


class PostsTest(UserTestCase):
    def _do_create_page(self, client, post):
        return self.graphql({
            'query': '''
                mutation M($input_0: PostCreateInput!) {
                    postCreate(input: $input_0) {
                        clientMutationId,
                        post {
                            url,
                            title,
                            body,
                            publishedAt,
                            revisionCreated {
                                author {
                                    username
                                }
                            },
                            tags {
                                edges {
                                    node {
                                        title,
                                        slug
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
                    'url': post['url'],
                    'title': post['title'],
                    'body': post['body'],
                    'tags': post['tags'],
                    'publishedAt': post['publishedAt'],
                }
            }
        }, client=client)

    def test_create_page(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37+00:00',
            'tags': 'tést tãg, Outra Tag',
        }

        # without login should fail
        response = self._do_create_page(self.client, post)
        login_required_error = LoginRequiredError()
        expected = {
            'data': {
                'postCreate': {
                    'post': None,
                    'clientMutationId': '1',
                    'errors': [{
                        'code': login_required_error.code,
                    }]
                },
            }
        }
        self.assertEqual(response.json(), expected)

        # logged in
        self._do_login()
        response = self._do_create_page(self.client, post)
        expected = {
            'data': {
                'postCreate': {
                    'post': {
                        'url': post['url'],
                        'title': post['title'],
                        'body': post['body'],
                        'publishedAt': post['publishedAt'],
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            }
                        },
                        'tags': {
                            'edges': [
                                {'node': {
                                    'title': 'tést tãg',
                                    'slug': 'test-tag'
                                }},
                                {'node': {
                                    'title': 'Outra Tag',
                                    'slug': 'outra-tag'
                                }}
                            ]
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

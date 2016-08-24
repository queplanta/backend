from backend.tests import UserTestCase


class CommentsTest(UserTestCase):
    def _do_create_page(self, client, post):
        return self.graphql({
            'query': '''
                mutation M($input_0: PostCreateInput!) {
                    postCreate(input: $input_0) {
                        clientMutationId,
                        post {
                            id
                            document {
                                id
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

    def test_comment(self):
        post = {
            'url': 'new-post-title',
            'title': 'new post title',
            'body': 'new post content',
            'publishedAt': '2011-01-05T20:26:37+00:00',
            'tags': 'tést tãg, Outra Tag',
        }

        comment = {
            'body': 'first comment',
        }

        self._do_login()
        response = self._do_create_page(self.client, post)
        postDocumentId = response.json()['data']['postCreate']['post']['document']['id']
        postId = response.json()['data']['postCreate']['post']['id']

        response = self.graphql({
            'query': '''
                mutation M($input_0: CommentCreateInput!) {
                    commentCreate(input: $input_0) {
                        clientMutationId,
                        commenting {
                            count
                            comments {
                                edges {
                                    node {
                                        body
                                        revisionCreated {
                                            author {
                                                username
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        errors {
                            code,
                        },
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'body': comment['body'],
                    'parent': postId,
                }
            }
        })

        expected = {
            'data': {
                'commentCreate': {
                    'commenting': {
                        'count': 1,
                        'comments': {
                            'edges': [
                                {'node': {
                                    'body': comment['body'],
                                    'revisionCreated': {
                                        'author': {
                                            'username': self.user.username,
                                        }
                                    },
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

        response = self.graphql({
            'query': '''
                query($id: ID!) {
                    post(id: $id) {
                        document {
                            id
                        },
                        commenting {
                            count,
                            comments {
                                edges {
                                    node {
                                        body,
                                        revisionCreated {
                                            author {
                                                username
                                            }
                                        }
                                        parent {
                                            id
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': postId
            }
        })

        expected = {
            'data': {
                'post': {
                    'document': {
                        'id': postDocumentId,
                    },
                    'commenting': {
                        'count': 1,
                        'comments': {
                            'edges': [
                                {'node': {
                                    'body': comment['body'],
                                    'revisionCreated': {
                                        'author': {
                                            'username': self.user.username,
                                        }
                                    },
                                    'parent': {
                                        'id': postDocumentId
                                    },
                                }}
                            ]
                        }
                    },
                },
            }
        }
        self.assertEqual(response.json(), expected)

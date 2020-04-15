from backend.tests import UserTestCase
from graphql_relay.node.node import to_global_id
from life.tests.factories import LifeNodeFactory
from .factories import UsageFactory


class UsagesTest(UserTestCase):
    def test_can_add_usage(self):
        self._do_login()
        plant = LifeNodeFactory()
        usage = {
            'plants': [to_global_id('LifeNode', plant.document_id)],
            'types': ['FOOD'],
            'title': 'You can eat the fruit',
            'body': 'Take skin off and eat the flash',
            'source': 'My grandmother'
        }
        response = self.graphql({
            'query': '''
                mutation M($input_0: UsageCreateInput!) {
                    usageCreate(input: $input_0) {
                        clientMutationId,
                        usage {
                            source
                            title,
                            body,
                            types,
                            plants(first: 10) {
                                edges {
                                    node {
                                        title
                                    }
                                }
                            }
                            revisionCreated {
                                author {
                                    username
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
                    'plants': usage['plants'],
                    'types': usage['types'],
                    'source': usage['source'],
                    'title': usage['title'],
                    'body': usage['body'],
                }
            }
        }, client=self.client)

        expected = {
            'data': {
                'usageCreate': {
                    'usage': {
                        'source': usage['source'],
                        'title': usage['title'],
                        'types': usage['types'],
                        'body': usage['body'],
                        'plants': {
                            'edges': [{'node': {
                                'title': plant.title
                            }}]
                        },
                        'revisionCreated': {
                            'author': {
                                'username': self.user.username,
                            },
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }

        self.assertEqual(response.json(), expected)

    #  def test_usage_by_url(self):
    #      usage = UsageFactory()
    #      response = self.graphql({
    #          'query': '''
    #              query UsageQuery(
    #                $url: String!
    #              ) {
    #                usage: usageByUrl(url: $url) {
    #                  url
    #                  title
    #                }
    #              }
    #              ''',
    #          'variables': {
    #              'url': usage.url
    #          }
    #      }, client=self.client)
    #      self.assertEqual(response.json(), {'data': {'usage': {'url': usage.url, 'title': usage.title}}})


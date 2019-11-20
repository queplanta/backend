from backend.tests import UserTestCase
from django.test.client import MULTIPART_CONTENT
from graphql_relay.node.node import to_global_id

from .factories import LifeNodeFactory
from lists.tests.factories import CollectionItemFactory, WishItemFactory


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
                            commonNames(first: 10) {
                                edges {
                                    node {
                                        name
                                    }
                                }
                            },
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
                            },
                            myCollectionItem {
                                id
                            }
                            myWishItem {
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
            'rank': 'GENUS',
            'parent': None,
            'commonNames': [],
        }
        response = self._do_create(self.client, node)
        parent = response.json()['data']['lifeNodeCreate']['lifeNode']

        with open('public/default_user_avatar.jpg', 'rb') as image1, open('public/default_user_avatar.jpg', 'rb') as image2:
            node = {
                'title': 'Mangifera indica',
                'description': 'The fruit tastes like heaven',
                'rank': 'SPECIES',
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
                        'commonNames': {
                            'edges': [
                                {'node': {
                                    'name': 'Mangueira'
                                }}
                            ]
                        },
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
                        },
                        'myCollectionItem': None,
                        'myWishItem': None,
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
                            commonNames(first: 10) {
                                edges {
                                    node {
                                        name
                                    }
                                }
                            },
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
                        'rank': 'SPECIES',
                        'commonNames': {
                            'edges': [
                                {'node': {'name': 'dorme-dorme'}},
                                {'node': {'name': 'dormideira'}},
                                {'node': {'name': 'malícia'}},
                                {'node': {'name': 'sensitiva'}}
                            ]
                        },
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

    def test_add_characteristic(self):
        self._do_login()
        node = {
            'title': 'Mangifera indica',
            'description': 'The fruit tastes like heaven',
            'rank': 'SPECIES',
            'parent': None,
            'commonNames': [],
        }
        response = self._do_create(self.client, node)
        parent = response.json()['data']['lifeNodeCreate']['lifeNode']

        response = self.graphql({
            'query': '''
                mutation M($input_0: CharacteristicAddInput!) {
                    lifeNodeCharacteristicAdd(input: $input_0) {
                        clientMutationId,
                        lifeNode {
                            id
                            characteristics(first: 10) {
                                edges {
                                    node {
                                        title
                                        value
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
                    'lifeNode': parent['id'],
                    'title': 'Edible',
                    'value': 'Only its fruits',
                }
            }
        })

        expected = {
            'data': {
                'lifeNodeCharacteristicAdd': {
                    'lifeNode': {
                        'id': parent['id'],
                        'characteristics': {
                            'edges': [{
                                'node': {
                                    'title': 'Edible',
                                    'value': 'Only its fruits'
                                }
                            }]
                        }
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_my_collection_item(self):
        self._do_login()
        life_node = LifeNodeFactory()
        collection_item = CollectionItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        collection_item_id = to_global_id("CollectionItem", collection_item.document.pk)

        response = self.graphql({
            'query': '''
                query M($id: Int!) {
                    lifeNodeByIntID(documentId: $id) {
                        myCollectionItem {
                            id
                        }
                    }
                }
                ''',
            'variables': {
                'id': life_node.document_id,
            },
        }, client=self.client)

        expected = {
            'data': {
                'lifeNodeByIntID': {
                    'myCollectionItem': {
                        'id': collection_item_id,
                    },
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_my_wish_item(self):
        self._do_login()
        life_node = LifeNodeFactory()
        wish_item = WishItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        wish_item_id = to_global_id("WishItem", wish_item.document.pk)

        response = self.graphql({
            'query': '''
                query M($id: Int!) {
                    lifeNodeByIntID(documentId: $id) {
                        myWishItem {
                            id
                        }
                    }
                }
                ''',
            'variables': {
                'id': life_node.document_id,
            },
        }, client=self.client)

        expected = {
            'data': {
                'lifeNodeByIntID': {
                    'myWishItem': {
                        'id': wish_item_id,
                    },
                },
            }
        }
        self.assertEqual(response.json(), expected)
